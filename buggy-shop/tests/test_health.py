# tests/test_health.py

def test_root_endpoint(client):
    """Тест корневого эндпоинта"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "BuggyShop API" in data["message"]
    assert "version" in data


def test_health_check(client):
    """Тест health check эндпоинта"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"
