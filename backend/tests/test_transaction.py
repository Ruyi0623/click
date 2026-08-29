"""测试账单模块。"""
import pytest


@pytest.fixture
def paired_headers(client, auth_headers):
    """创建已配对用户的 headers。"""
    client.post("/api/auth/send-code", json={"phone": "13800138001"})
    response2 = client.post("/api/auth/login", json={"phone": "13800138001", "code": "123456"})
    headers2 = {"Authorization": f"Bearer {response2.json()['access_token']}"}

    response = client.post("/api/couple/generate", headers=auth_headers)
    code = response.json()["code"]
    client.post("/api/couple/confirm", headers=headers2, json={"code": code})

    return auth_headers


def test_create_transaction(client, paired_headers):
    """测试创建账单。"""
    response = client.post("/api/transactions", headers=paired_headers, json={
        "amount": 260,
        "category": "餐饮",
        "description": "火锅",
        "split_type": "equal",
        "mood": "超级开心"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 260
    assert data["category"] == "餐饮"
    assert data["description"] == "火锅"
    assert data["split_type"] == "equal"


def test_create_transaction_not_paired(client, auth_headers):
    """测试未配对时创建账单。"""
    response = client.post("/api/transactions", headers=auth_headers, json={
        "amount": 100,
        "category": "测试"
    })
    assert response.status_code == 400


def test_list_transactions(client, paired_headers):
    """测试获取账单列表。"""
    client.post("/api/transactions", headers=paired_headers, json={
        "amount": 100,
        "category": "餐饮"
    })
    client.post("/api/transactions", headers=paired_headers, json={
        "amount": 200,
        "category": "交通"
    })

    response = client.get("/api/transactions", headers=paired_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_balance(client, paired_headers):
    """测试获取账务平衡。"""
    # 用户1消费
    client.post("/api/transactions", headers=paired_headers, json={
        "amount": 300,
        "category": "餐饮"
    })

    response = client.get("/api/transactions/balance", headers=paired_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["user1_paid"] == 300
    assert data["user2_paid"] == 0
    assert "欠" in data["who_owes"]


def test_delete_transaction(client, paired_headers):
    """测试删除账单。"""
    response = client.post("/api/transactions", headers=paired_headers, json={
        "amount": 100,
        "category": "测试"
    })
    transaction_id = response.json()["id"]

    response = client.delete(f"/api/transactions/{transaction_id}", headers=paired_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "已删除"

    response = client.get("/api/transactions", headers=paired_headers)
    assert len(response.json()) == 0
