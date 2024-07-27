import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from configuration.properties import app
from src.service.user_service import UserService

@pytest.fixture
def user_service_mock():
    return MagicMock(spec=UserService)

@pytest.fixture
def test_client():
    return TestClient(app)

def test_create_user(test_client, user_service_mock):
    user_data = {
        "user_id": "1",
        "nom_prenom": "John Doe",
        "email": "john@example.com"
    }

    created_user = User(**user_data)
    user_service_mock.create_user.return_value = created_user

    response = test_client.post("/users", json=user_data)

    assert response.status_code == 200
    assert response.json() == created_user.dict()

def test_get_user_by_id(test_client, user_service_mock):
    user_id = "1"
    user_data = {
        "user_id": user_id,
        "nom_prenom": "Jane Doe",
        "email": "jane@example.com"
    }

    user = User(**user_data)
    user_service_mock.get_user_by_id.return_value = user

    response = test_client.get(f"/users/{user_id}")

    assert response.status_code == 200
    assert response.json() == user.dict()
