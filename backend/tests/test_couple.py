"""测试配对模块。"""


def test_generate_code(client, auth_headers):
    """测试生成配对码。"""
    response = client.post("/api/couple/generate", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "code" in data
    assert len(data["code"]) == 6
    assert data["expires_in"] == 300


def test_confirm_pair(client, auth_headers):
    """测试配对确认。"""
    # 创建第二个用户
    client.post("/api/auth/send-code", json={"phone": "13800138001"})
    response2 = client.post("/api/auth/login", json={"phone": "13800138001", "code": "123456"})
    headers2 = {"Authorization": f"Bearer {response2.json()['access_token']}"}

    # 用户1生成配对码
    response = client.post("/api/couple/generate", headers=auth_headers)
    code = response.json()["code"]

    # 用户2确认配对
    response = client.post("/api/couple/confirm", headers=headers2, json={
        "code": code,
        "start_date": "2024-01-01"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "配对成功"


def test_confirm_pair_self(client, auth_headers):
    """测试不能和自己配对。"""
    # 生成配对码
    response = client.post("/api/couple/generate", headers=auth_headers)
    code = response.json()["code"]

    # 尝试和自己配对
    response = client.post("/api/couple/confirm", headers=auth_headers, json={"code": code})
    assert response.status_code == 400
    assert "不能和自己配对" in response.json()["detail"]


def test_confirm_pair_invalid_code(client, auth_headers):
    """测试无效配对码。"""
    response = client.post("/api/couple/confirm", headers=auth_headers, json={"code": "999999"})
    assert response.status_code == 400
    assert "配对码无效" in response.json()["detail"]


def test_get_couple_info(client, auth_headers):
    """测试获取配对信息。"""
    # 创建第二个用户并配对
    client.post("/api/auth/send-code", json={"phone": "13800138001"})
    response2 = client.post("/api/auth/login", json={"phone": "13800138001", "code": "123456"})
    headers2 = {"Authorization": f"Bearer {response2.json()['access_token']}"}

    response = client.post("/api/couple/generate", headers=auth_headers)
    code = response.json()["code"]
    client.post("/api/couple/confirm", headers=headers2, json={"code": code})

    # 获取配对信息
    response = client.get("/api/couple/info", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "partner_id" in data
    assert "partner_nickname" in data
    assert data["start_date"] is not None
    assert data["days_together"] >= 0


def test_get_couple_info_not_paired(client, auth_headers):
    """测试未配对时获取信息。"""
    response = client.get("/api/couple/info", headers=auth_headers)
    assert response.status_code == 404
    assert "尚未配对" in response.json()["detail"]


def test_unbind(client, auth_headers):
    """测试解除配对。"""
    # 创建第二个用户并配对
    client.post("/api/auth/send-code", json={"phone": "13800138001"})
    response2 = client.post("/api/auth/login", json={"phone": "13800138001", "code": "123456"})
    headers2 = {"Authorization": f"Bearer {response2.json()['access_token']}"}

    response = client.post("/api/couple/generate", headers=auth_headers)
    code = response.json()["code"]
    client.post("/api/couple/confirm", headers=headers2, json={"code": code})

    # 解除配对
    response = client.post("/api/couple/unbind", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "已解除配对"

    # 确认已解除
    response = client.get("/api/couple/info", headers=auth_headers)
    assert response.status_code == 404


def test_unbind_not_paired(client, auth_headers):
    """测试未配对时解除配对。"""
    response = client.post("/api/couple/unbind", headers=auth_headers)
    assert response.status_code == 404
