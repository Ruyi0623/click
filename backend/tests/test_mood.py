"""测试心情模块。"""
import pytest
from datetime import date


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


def test_create_mood(client, paired_headers):
    """测试创建心情。"""
    today = date.today().isoformat()
    response = client.post("/api/moods", headers=paired_headers, json={
        "emoji": "😊",
        "mood_date": today
    })
    assert response.status_code == 200
    data = response.json()
    assert data["emoji"] == "😊"
    assert data["mood_date"] == today


def test_create_mood_not_paired(client, auth_headers):
    """测试未配对时创建心情。"""
    today = date.today().isoformat()
    response = client.post("/api/moods", headers=auth_headers, json={
        "emoji": "😊",
        "mood_date": today
    })
    assert response.status_code == 400
    assert "尚未配对" in response.json()["detail"]


def test_update_mood_same_date(client, paired_headers):
    """测试同一天更新心情。"""
    today = date.today().isoformat()

    # 第一次创建
    response1 = client.post("/api/moods", headers=paired_headers, json={
        "emoji": "😊",
        "mood_date": today
    })
    assert response1.status_code == 200
    mood_id = response1.json()["id"]

    # 同一天更新
    response2 = client.post("/api/moods", headers=paired_headers, json={
        "emoji": "😢",
        "mood_date": today
    })
    assert response2.status_code == 200
    assert response2.json()["id"] == mood_id
    assert response2.json()["emoji"] == "😢"


def test_list_moods(client, paired_headers):
    """测试获取心情列表。"""
    today = date.today().isoformat()

    # 创建心情
    client.post("/api/moods", headers=paired_headers, json={
        "emoji": "😊",
        "mood_date": today
    })

    # 获取列表
    response = client.get("/api/moods", headers=paired_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_delete_mood(client, paired_headers):
    """测试删除心情。"""
    today = date.today().isoformat()

    # 创建心情
    response = client.post("/api/moods", headers=paired_headers, json={
        "emoji": "😊",
        "mood_date": today
    })
    mood_id = response.json()["id"]

    # 删除
    response = client.delete(f"/api/moods/{mood_id}", headers=paired_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "已删除"


def test_delete_mood_not_found(client, paired_headers):
    """测试删除不存在的心情。"""
    response = client.delete("/api/moods/999", headers=paired_headers)
    assert response.status_code == 404
