"""测试聊天消息模块。"""
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


def test_create_message(client, paired_headers):
    """测试发送消息。"""
    response = client.post("/api/messages", headers=paired_headers, json={
        "content": "你好呀！",
        "type": "text"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "你好呀！"
    assert data["type"] == "text"
    assert "id" in data
    assert "created_at" in data


def test_create_message_not_paired(client, auth_headers):
    """测试未配对时发送消息。"""
    response = client.post("/api/messages", headers=auth_headers, json={
        "content": "你好呀！"
    })
    assert response.status_code == 400
    assert "尚未配对" in response.json()["detail"]


def test_list_messages(client, paired_headers):
    """测试获取消息列表。"""
    # 发送几条消息
    client.post("/api/messages", headers=paired_headers, json={"content": "消息1"})
    client.post("/api/messages", headers=paired_headers, json={"content": "消息2"})
    client.post("/api/messages", headers=paired_headers, json={"content": "消息3"})

    # 获取列表
    response = client.get("/api/messages", headers=paired_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    # 消息应该按时间正序排列
    assert data[0]["content"] == "消息1"
    assert data[2]["content"] == "消息3"


def test_list_messages_with_limit(client, paired_headers):
    """测试获取消息列表带限制。"""
    # 发送几条消息
    client.post("/api/messages", headers=paired_headers, json={"content": "消息1"})
    client.post("/api/messages", headers=paired_headers, json={"content": "消息2"})
    client.post("/api/messages", headers=paired_headers, json={"content": "消息3"})

    # 获取限制数量的消息
    response = client.get("/api/messages?limit=2", headers=paired_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # 应该返回最新的2条
    assert data[0]["content"] == "消息2"
    assert data[1]["content"] == "消息3"


def test_delete_message(client, paired_headers):
    """测试删除消息。"""
    # 发送消息
    response = client.post("/api/messages", headers=paired_headers, json={"content": "测试消息"})
    message_id = response.json()["id"]

    # 删除
    response = client.delete(f"/api/messages/{message_id}", headers=paired_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "已删除"

    # 确认已删除
    response = client.get("/api/messages", headers=paired_headers)
    assert len(response.json()) == 0


def test_delete_message_not_found(client, paired_headers):
    """测试删除不存在的消息。"""
    response = client.delete("/api/messages/999", headers=paired_headers)
    assert response.status_code == 404
