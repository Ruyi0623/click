"""测试恋爱罚单模块。"""
import pytest


@pytest.fixture
def paired_users(client, auth_headers):
    """创建已配对用户的 headers。"""
    client.post("/api/auth/send-code", json={"phone": "13800138001"})
    response2 = client.post("/api/auth/login", json={"phone": "13800138001", "code": "123456"})
    user2_id = response2.json()["user_id"]
    headers2 = {"Authorization": f"Bearer {response2.json()['access_token']}"}

    response = client.post("/api/couple/generate", headers=auth_headers)
    code = response.json()["code"]
    client.post("/api/couple/confirm", headers=headers2, json={"code": code})

    return auth_headers, headers2, user2_id


def test_create_money_penalty(client, paired_users):
    """测试开具金钱罚单。"""
    headers1, headers2, user2_id = paired_users

    response = client.post("/api/penalties", headers=headers1, json={
        "offender_id": user2_id,
        "reason": "打游戏超时",
        "penalty_type": "money",
        "amount": 10
    })
    assert response.status_code == 200
    data = response.json()
    assert data["reason"] == "打游戏超时"
    assert data["penalty_type"] == "money"
    assert data["amount"] == 10
    assert data["is_done"] is False


def test_create_action_penalty(client, paired_users):
    """测试开具行动罚单。"""
    headers1, headers2, user2_id = paired_users

    response = client.post("/api/penalties", headers=headers1, json={
        "offender_id": user2_id,
        "reason": "惹我生气了",
        "penalty_type": "action",
        "action": "帮对方洗碗一周"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["penalty_type"] == "action"
    assert data["action"] == "帮对方洗碗一周"


def test_create_penalty_not_paired(client, auth_headers):
    """测试未配对时开罚单。"""
    response = client.post("/api/penalties", headers=auth_headers, json={
        "offender_id": "fake-id",
        "reason": "测试",
        "penalty_type": "money",
        "amount": 5
    })
    assert response.status_code == 400


def test_create_penalty_invalid_offender(client, paired_users):
    """测试对非伴侣开罚单。"""
    headers1, _, _ = paired_users

    response = client.post("/api/penalties", headers=headers1, json={
        "offender_id": "invalid-user-id",
        "reason": "测试",
        "penalty_type": "money",
        "amount": 5
    })
    assert response.status_code == 400
    assert "只能对伴侣开罚单" in response.json()["detail"]


def test_list_penalties(client, paired_users):
    """测试获取罚单列表。"""
    headers1, headers2, user2_id = paired_users

    client.post("/api/penalties", headers=headers1, json={
        "offender_id": user2_id,
        "reason": "罚单1",
        "penalty_type": "money",
        "amount": 5
    })
    client.post("/api/penalties", headers=headers2, json={
        "offender_id": user2_id,
        "reason": "罚单2",
        "penalty_type": "action",
        "action": "捏肩"
    })

    response = client.get("/api/penalties", headers=headers1)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_mark_penalty_done(client, paired_users):
    """测试标记罚单完成。"""
    headers1, headers2, user2_id = paired_users

    response = client.post("/api/penalties", headers=headers1, json={
        "offender_id": user2_id,
        "reason": "打游戏超时",
        "penalty_type": "money",
        "amount": 10
    })
    penalty_id = response.json()["id"]

    # 被罚方标记完成
    response = client.post(f"/api/penalties/{penalty_id}/done", headers=headers2)
    assert response.status_code == 200
    assert response.json()["is_done"] is True
    assert response.json()["done_at"] is not None


def test_delete_penalty(client, paired_users):
    """测试删除罚单。"""
    headers1, _, user2_id = paired_users

    response = client.post("/api/penalties", headers=headers1, json={
        "offender_id": user2_id,
        "reason": "测试",
        "penalty_type": "money",
        "amount": 5
    })
    penalty_id = response.json()["id"]

    response = client.delete(f"/api/penalties/{penalty_id}", headers=headers1)
    assert response.status_code == 200
    assert response.json()["message"] == "已删除"

    response = client.get("/api/penalties", headers=headers1)
    assert len(response.json()) == 0
