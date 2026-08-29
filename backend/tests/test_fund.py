"""测试心愿基金模块。"""
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


def test_create_fund(client, paired_headers):
    """测试创建心愿基金。"""
    response = client.post("/api/funds", headers=paired_headers, json={
        "name": "去大理旅行",
        "target_amount": 5000,
        "icon": "✈️"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "去大理旅行"
    assert data["target_amount"] == 5000
    assert data["current_amount"] == 0
    assert data["progress"] == 0


def test_create_fund_not_paired(client, auth_headers):
    """测试未配对时创建基金。"""
    response = client.post("/api/funds", headers=auth_headers, json={
        "name": "测试基金",
        "target_amount": 1000
    })
    assert response.status_code == 400


def test_list_funds(client, paired_headers):
    """测试获取基金列表。"""
    client.post("/api/funds", headers=paired_headers, json={
        "name": "基金1",
        "target_amount": 1000
    })
    client.post("/api/funds", headers=paired_headers, json={
        "name": "基金2",
        "target_amount": 2000
    })

    response = client.get("/api/funds", headers=paired_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_contribute_to_fund(client, paired_headers):
    """测试向基金投入资金。"""
    response = client.post("/api/funds", headers=paired_headers, json={
        "name": "旅行基金",
        "target_amount": 5000
    })
    fund_id = response.json()["id"]

    response = client.post(f"/api/funds/{fund_id}/contribute", headers=paired_headers, json={
        "amount": 500,
        "note": "省下的午饭钱"
    })
    assert response.status_code == 200
    assert response.json()["amount"] == 500

    # 检查基金余额
    response = client.get("/api/funds", headers=paired_headers)
    fund = response.json()[0]
    assert fund["current_amount"] == 500
    assert fund["progress"] == 10.0


def test_list_contributions(client, paired_headers):
    """测试获取投入记录。"""
    response = client.post("/api/funds", headers=paired_headers, json={
        "name": "旅行基金",
        "target_amount": 5000
    })
    fund_id = response.json()["id"]

    client.post(f"/api/funds/{fund_id}/contribute", headers=paired_headers, json={
        "amount": 500
    })
    client.post(f"/api/funds/{fund_id}/contribute", headers=paired_headers, json={
        "amount": 300
    })

    response = client.get(f"/api/funds/{fund_id}/contributions", headers=paired_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_delete_fund(client, paired_headers):
    """测试删除基金。"""
    response = client.post("/api/funds", headers=paired_headers, json={
        "name": "旅行基金",
        "target_amount": 5000
    })
    fund_id = response.json()["id"]

    response = client.delete(f"/api/funds/{fund_id}", headers=paired_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "已删除"

    response = client.get("/api/funds", headers=paired_headers)
    assert len(response.json()) == 0


def test_withdraw_from_fund(client, paired_headers):
    """测试从基金取出资金。"""
    response = client.post("/api/funds", headers=paired_headers, json={
        "name": "旅行基金",
        "target_amount": 5000
    })
    fund_id = response.json()["id"]

    # 先投入
    client.post(f"/api/funds/{fund_id}/contribute", headers=paired_headers, json={
        "amount": 1000
    })

    # 取出
    response = client.post(f"/api/funds/{fund_id}/contribute", headers=paired_headers, json={
        "amount": 300,
        "type": "withdraw",
        "note": "买了机票"
    })
    assert response.status_code == 200
    assert response.json()["amount"] == 300
    assert response.json()["type"] == "withdraw"

    # 检查余额
    response = client.get("/api/funds", headers=paired_headers)
    fund = response.json()[0]
    assert fund["current_amount"] == 700


def test_withdraw_insufficient_balance(client, paired_headers):
    """测试余额不足时取出。"""
    response = client.post("/api/funds", headers=paired_headers, json={
        "name": "旅行基金",
        "target_amount": 5000
    })
    fund_id = response.json()["id"]

    # 投入 500
    client.post(f"/api/funds/{fund_id}/contribute", headers=paired_headers, json={
        "amount": 500
    })

    # 取出 800，应失败
    response = client.post(f"/api/funds/{fund_id}/contribute", headers=paired_headers, json={
        "amount": 800,
        "type": "withdraw"
    })
    assert response.status_code == 400
    assert "余额不足" in response.json()["detail"]


def test_delete_contribution(client, paired_headers):
    """测试撤销贡献记录。"""
    response = client.post("/api/funds", headers=paired_headers, json={
        "name": "旅行基金",
        "target_amount": 5000
    })
    fund_id = response.json()["id"]

    # 投入 1000
    response = client.post(f"/api/funds/{fund_id}/contribute", headers=paired_headers, json={
        "amount": 1000
    })
    contribution_id = response.json()["id"]

    # 投入 500
    client.post(f"/api/funds/{fund_id}/contribute", headers=paired_headers, json={
        "amount": 500
    })

    # 撤销第一笔
    response = client.delete(f"/api/funds/{fund_id}/contributions/{contribution_id}", headers=paired_headers)
    assert response.status_code == 200

    # 余额应为 500
    response = client.get("/api/funds", headers=paired_headers)
    assert response.json()[0]["current_amount"] == 500

    # 记录应剩 1 条
    response = client.get(f"/api/funds/{fund_id}/contributions", headers=paired_headers)
    assert len(response.json()) == 1
