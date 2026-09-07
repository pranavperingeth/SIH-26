import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
from fastapi.testclient import TestClient

from backend.api.main import app

VALID_ADDRESS = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
INVALID_ADDRESS = "hello"

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_investigation_valid_address():
    response = client.post(
        "/api/investigate",
        json={"wallet_address": VALID_ADDRESS},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "PENDING"
    assert body["investigation_id"]


def test_create_investigation_invalid_address():
    response = client.post(
        "/api/investigate",
        json={"wallet_address": INVALID_ADDRESS},
    )
    assert response.status_code == 422


def test_list_investigations():
    response = client.get("/api/investigations")
    assert response.status_code == 200
    body = response.json()
    assert "results" in body
    assert isinstance(body["results"], list)


def test_get_investigation_found_and_not_found():
    create_response = client.post(
        "/api/investigate",
        json={"wallet_address": VALID_ADDRESS},
    )
    investigation_id = create_response.json()["investigation_id"]

    ok_response = client.get(f"/api/investigations/{investigation_id}")
    assert ok_response.status_code == 200
    assert ok_response.json()["id"] == investigation_id

    missing_response = client.get("/api/investigations/does-not-exist")
    assert missing_response.status_code == 404


def test_wallet_endpoints():
    for path in [
        f"/api/wallet/{VALID_ADDRESS}",
        f"/api/wallet/{VALID_ADDRESS}/risk",
        f"/api/wallet/{VALID_ADDRESS}/graph",
        f"/api/wallet/{VALID_ADDRESS}/transactions",
    ]:
        response = client.get(path)
        assert response.status_code == 200
        assert isinstance(response.json(), dict)


def test_wallet_endpoint_invalid_address():
    response = client.get(f"/api/wallet/{INVALID_ADDRESS}")
    assert response.status_code == 422


def test_alerts_list():
    response = client.get("/api/alerts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
