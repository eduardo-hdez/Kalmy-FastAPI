import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_item():
    item_data = {
    "name": "Minecraft",
    "description": "Best selling game",
    "price": 450,
    "available": True
    }

    response = client.post("/items/", json=item_data)

    assert response.status_code == 201

    data = response.json()

    assert "id" in data

    assert data["name"] == "Minecraft"
    assert data["price"] == 450