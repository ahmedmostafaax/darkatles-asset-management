from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

HEADERS = {"x-api-key": "my-secret-api-key"}

def test_root():
    response = client.get("/")
    assert response.status_code == 200

def test_create_asset():
    response = client.post("/assets/", json={
        "type": "domain",
        "value": "example.com",
        "source": "manual",
        "tags": ["test"],
        "metadata": {}
    }, headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["value"] == "example.com"

def test_deduplication():
    client.post("/assets/", json={
        "type": "domain",
        "value": "dedup-test.com",
        "source": "manual",
        "tags": ["first"],
        "metadata": {}
    }, headers=HEADERS)
    client.post("/assets/", json={
        "type": "domain",
        "value": "dedup-test.com",
        "source": "manual",
        "tags": ["second"],
        "metadata": {}
    }, headers=HEADERS)
    response = client.get("/assets/", params={"value_contains": "dedup-test.com"})
    assert len(response.json()) == 1
    assert "first" in response.json()[0]["tags"]
    assert "second" in response.json()[0]["tags"]

def test_list_assets_filter():
    response = client.get("/assets/", params={"type": "domain"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_bulk_import():
    response = client.post("/assets/bulk-import", json=[
        {"type": "domain", "value": "bulk1.com", "source": "import", "tags": [], "metadata": {}},
        {"type": "ip_address", "value": "1.2.3.4", "source": "scan", "tags": [], "metadata": {}},
    ], headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["created"] >= 0

def test_unauthorized():
    response = client.post("/assets/", json={
        "type": "domain",
        "value": "unauth.com",
        "source": "manual",
        "tags": [],
        "metadata": {}
    }, headers={"x-api-key": "wrong-key"})
    assert response.status_code == 401