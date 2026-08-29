"""测试纪念日模块。"""
import pytest


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


def test_create_anniversary(client, paired_headers):
    """测试创建纪念日。"""
    response = client.post("/api/anniversaries", headers=paired_headers, json={
        "title": "在一起纪念日",
        "date": "2024-01-01",
        "repeat_type": "yearly"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "在一起纪念日"
    assert data["date"] == "2024-01-01"
    assert data["repeat_type"] == "yearly"
    assert "days_until" in data


def test_create_anniversary_not_paired(client, auth_headers):
    """测试未配对时创建纪念日。"""
    response = client.post("/api/anniversaries", headers=auth_headers, json={
        "title": "在一起纪念日",
        "date": "2024-01-01",
        "repeat_type": "yearly"
    })
    assert response.status_code == 400
    assert "尚未配对" in response.json()["detail"]


def test_list_anniversaries(client, paired_headers):
    """测试获取纪念日列表。"""
    # 创建纪念日
    client.post("/api/anniversaries", headers=paired_headers, json={
        "title": "在一起纪念日",
        "date": "2024-01-01",
        "repeat_type": "yearly"
    })
    client.post("/api/anniversaries", headers=paired_headers, json={
        "title": "生日",
        "date": "2024-06-15",
        "repeat_type": "yearly"
    })

    # 获取列表
    response = client.get("/api/anniversaries", headers=paired_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_update_anniversary(client, paired_headers):
    """测试更新纪念日。"""
    # 创建纪念日
    response = client.post("/api/anniversaries", headers=paired_headers, json={
        "title": "在一起纪念日",
        "date": "2024-01-01",
        "repeat_type": "yearly"
    })
    anniversary_id = response.json()["id"]

    # 更新
    response = client.put(f"/api/anniversaries/{anniversary_id}", headers=paired_headers, json={
        "title": "恋爱纪念日"
    })
    assert response.status_code == 200
    assert response.json()["title"] == "恋爱纪念日"


def test_update_anniversary_not_found(client, paired_headers):
    """测试更新不存在的纪念日。"""
    response = client.put("/api/anniversaries/999", headers=paired_headers, json={
        "title": "测试"
    })
    assert response.status_code == 404


def test_delete_anniversary(client, paired_headers):
    """测试删除纪念日。"""
    # 创建纪念日
    response = client.post("/api/anniversaries", headers=paired_headers, json={
        "title": "在一起纪念日",
        "date": "2024-01-01",
        "repeat_type": "yearly"
    })
    anniversary_id = response.json()["id"]

    # 删除
    response = client.delete(f"/api/anniversaries/{anniversary_id}", headers=paired_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "已删除"

    # 确认已删除
    response = client.get("/api/anniversaries", headers=paired_headers)
    assert len(response.json()) == 0
