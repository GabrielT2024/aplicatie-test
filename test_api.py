from __future__ import annotations

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.database import get_db
from app.main import app


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    models.Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture()
def db_session(engine) -> Session:
    connection = engine.connect()
    transaction = connection.begin()

    session = sessionmaker(bind=connection, autocommit=False, autoflush=False)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(autouse=True)
def override_get_db(db_session: Session):
    def _get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


def test_create_welder_with_authorization(client: TestClient):
    response = client.post(
        "/welders",
        json={
            "first_name": "Ion",
            "last_name": "Popescu",
            "identifier": "ID-001",
            "phone": "0712345678",
            "email": "ion.popescu@example.com",
            "certification_date": "2023-01-15",
            "status": "active",
            "authorizations": [
                {
                    "standard": "ASME IX",
                    "process": "141",
                    "issue_date": "2023-01-15",
                    "expiration_date": "2023-07-15",
                }
            ],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["identifier"] == "ID-001"
    assert len(data["authorizations"]) == 1
    assert data["authorizations"][0]["standard"] == "ASME IX"


def test_duplicate_identifier_not_allowed(client: TestClient):
    payload = {
        "first_name": "Ion",
        "last_name": "Popescu",
        "identifier": "ID-002",
        "status": "active",
    }
    first = client.post("/welders", json=payload)
    assert first.status_code == 201
    second = client.post("/welders", json=payload)
    assert second.status_code == 400


def test_authorization_crud_and_expiry(client: TestClient):
    welder_resp = client.post(
        "/welders",
        json={
            "first_name": "Maria",
            "last_name": "Ionescu",
            "identifier": "ID-003",
            "status": "active",
        },
    )
    welder_id = welder_resp.json()["id"]

    create_resp = client.post(
        f"/welders/{welder_id}/authorizations",
        json={
            "standard": "CR9",
            "process": "111",
            "base_materials": "P235GH",
            "issue_date": date.today().isoformat(),
            "expiration_date": (date.today() + timedelta(days=30)).isoformat(),
        },
    )
    assert create_resp.status_code == 201
    authorization = create_resp.json()

    update_resp = client.put(
        f"/authorizations/{authorization['id']}",
        json={"notes": "Verificat periodic"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["notes"] == "Verificat periodic"

    expiring_resp = client.get(
        "/authorizations/expiring",
        params={"days": 60, "reference_date": date.today().isoformat()},
    )
    assert expiring_resp.status_code == 200
    expiring = expiring_resp.json()
    assert len(expiring) == 1
    assert expiring[0]["authorization"]["standard"] == "CR9"
