"""测试愿望清单模块。"""
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


def test_create_wish(client, paired_headers):
    """测试创建愿望。"""
    response = client.post("/api/wishes", headers=paired_headers, json={
        "content": "一起去看日出"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "一起去看日出"
    assert data["is_done"] is False
    assert data["done_at"] is None


def test_create_wish_not_paired(client, auth_headers):
    """测试未配对时创建愿望。"""
    response = client.post("/api/wishes", headers=auth_headers, json={
        "content": "一起去看日出"
    })
    assert response.status_code == 400
    assert "尚未配对" in response.json()["detail"]


def test_list_wishes(client, paired_headers):
    """测试获取愿望列表。"""
    # 创建愿望
    client.post("/api/wishes", headers=paired_headers, json={"content": "愿望1"})
    client.post("/api/wishes", headers=paired_headers, json={"content": "愿望2"})

    # 获取列表
    response = client.get("/api/wishes", headers=paired_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_update_wish_content(client, paired_headers):
    """测试更新愿望内容。"""
    # 创建愿望
    response = client.post("/api/wishes", headers=paired_headers, json={"content": "原始内容"})
    wish_id = response.json()["id"]

    # 更新内容
    response = client.put(f"/api/wishes/{wish_id}", headers=paired_headers, json={
        "content": "更新后的内容"
    })
    assert response.status_code == 200
    assert response.json()["content"] == "更新后的内容"


def test_update_wish_done(client, paired_headers):
    """测试标记愿望完成。"""
    # 创建愿望
    response = client.post("/api/wishes", headers=paired_headers, json={"content": "测试愿望"})
    wish_id = response.json()["id"]

    # 标记完成
    response = client.put(f"/api/wishes/{wish_id}", headers=paired_headers, json={
        "is_done": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["is_done"] is True
    assert data["done_at"] is not None


def test_update_wish_not_found(client, paired_headers):
    """测试更新不存在的愿望。"""
    response = client.put("/api/wishes/999", headers=paired_headers, json={
        "content": "测试"
    })
    assert response.status_code == 404


def test_delete_wish(client, paired_headers):
    """测试删除愿望。"""
    # 创建愿望
    response = client.post("/api/wishes", headers=paired_headers, json={"content": "测试愿望"})
    wish_id = response.json()["id"]

    # 删除
    response = client.delete(f"/api/wishes/{wish_id}", headers=paired_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "已删除"

    # 确认已删除
    response = client.get("/api/wishes", headers=paired_headers)
    assert len(response.json()) == 0


def test_delete_wish_not_found(client, paired_headers):
    """测试删除不存在的愿望。"""
    response = client.delete("/api/wishes/999", headers=paired_headers)
    assert response.status_code == 404
