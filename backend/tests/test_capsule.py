"""测试时光胶囊模块。"""
import pytest
from datetime import datetime, timedelta


@pytest.fixture
def paired_headers(client, auth_headers):
    """创建已配对用户的 headers。"""
    # 创建第二个用户
    client.post("/api/auth/send-code", json={"phone": "13800138001"})
    response2 = client.post("/api/auth/login", json={"phone": "13800138001", "code": "123456"})
    headers2 = {"Authorization": f"Bearer {response2.json()['access_token']}"}

    # 配对
    response = client.post("/api/couple/generate", headers=auth_headers)
    code = response.json()["code"]
    client.post("/api/couple/confirm", headers=headers2, json={"code": code})

    return auth_headers


def test_create_capsule(client, paired_headers):
    """测试创建时光胶囊。"""
    future_time = (datetime.utcnow() + timedelta(days=30)).isoformat()

    response = client.post("/api/capsules", headers=paired_headers, json={
        "content": "写给未来的我们：希望我们永远幸福！",
        "open_at": future_time
    })
    assert response.status_code == 200
    data = response.json()
    assert "未到期" in data["content"]
    assert data["is_opened"] is False


def test_create_capsule_past_time(client, paired_headers):
    """测试创建过去时间的胶囊。"""
    past_time = (datetime.utcnow() - timedelta(days=1)).isoformat()

    response = client.post("/api/capsules", headers=paired_headers, json={
        "content": "测试内容",
        "open_at": past_time
    })
    assert response.status_code == 400
    assert "未来" in response.json()["detail"]


def test_create_capsule_not_paired(client, auth_headers):
    """测试未配对时创建胶囊。"""
    future_time = (datetime.utcnow() + timedelta(days=30)).isoformat()

    response = client.post("/api/capsules", headers=auth_headers, json={
        "content": "测试内容",
        "open_at": future_time
    })
    assert response.status_code == 400


def test_list_capsules(client, paired_headers):
    """测试获取胶囊列表。"""
    future_time = (datetime.utcnow() + timedelta(days=30)).isoformat()

    client.post("/api/capsules", headers=paired_headers, json={
        "content": "胶囊1",
        "open_at": future_time
    })
    client.post("/api/capsules", headers=paired_headers, json={
        "content": "胶囊2",
        "open_at": future_time
    })

    response = client.get("/api/capsules", headers=paired_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_capsule(client, paired_headers):
    """测试获取胶囊详情。"""
    future_time = (datetime.utcnow() + timedelta(days=30)).isoformat()

    response = client.post("/api/capsules", headers=paired_headers, json={
        "content": "秘密内容",
        "open_at": future_time
    })
    capsule_id = response.json()["id"]

    response = client.get(f"/api/capsules/{capsule_id}", headers=paired_headers)
    assert response.status_code == 200
    assert "未到期" in response.json()["content"]


def test_delete_capsule(client, paired_headers):
    """测试删除胶囊。"""
    future_time = (datetime.utcnow() + timedelta(days=30)).isoformat()

    response = client.post("/api/capsules", headers=paired_headers, json={
        "content": "测试内容",
        "open_at": future_time
    })
    capsule_id = response.json()["id"]

    response = client.delete(f"/api/capsules/{capsule_id}", headers=paired_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "已删除"

    response = client.get("/api/capsules", headers=paired_headers)
    assert len(response.json()) == 0
