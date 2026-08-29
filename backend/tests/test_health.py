"""测试基础端点。"""


def test_root(client):
    """测试根端点。"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "咔哒 API" in data["message"]


def test_health(client):
    """测试健康检查端点。"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
