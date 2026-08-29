"""测试认证模块。"""


def test_send_code(client):
    """测试发送验证码。"""
    response = client.post("/api/auth/send-code", json={"phone": "13800138000"})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "验证码已发送"
    assert data["dev_code"] == "123456"


def test_send_code_rate_limit(client):
    """测试验证码发送频率限制。"""
    # 使用新手机号测试
    response1 = client.post("/api/auth/send-code", json={"phone": "13900139000"})
    assert response1.status_code == 200

    # 立即再次发送应该被限制
    response2 = client.post("/api/auth/send-code", json={"phone": "13900139000"})
    assert response2.status_code == 429


def test_login_success(client):
    """测试登录成功。"""
    # 先发送验证码
    client.post("/api/auth/send-code", json={"phone": "13800138000"})

    # 登录
    response = client.post("/api/auth/login", json={"phone": "13800138000", "code": "123456"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user_id" in data
    assert data["nickname"] == "用户8000"


def test_login_wrong_code(client):
    """测试验证码错误。"""
    # 先发送验证码
    client.post("/api/auth/send-code", json={"phone": "13800138000"})

    # 使用错误验证码登录
    response = client.post("/api/auth/login", json={"phone": "13800138000", "code": "999999"})
    assert response.status_code == 400
    assert "验证码错误" in response.json()["detail"]


def test_login_with_nickname(client):
    """测试带昵称登录。"""
    # 先发送验证码
    client.post("/api/auth/send-code", json={"phone": "13800138001"})

    # 带昵称登录
    response = client.post("/api/auth/login", json={
        "phone": "13800138001",
        "code": "123456",
        "nickname": "测试用户"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["nickname"] == "测试用户"


def test_get_me(client, auth_headers):
    """测试获取当前用户信息。"""
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["phone"] == "13800138000"
    assert data["nickname"] == "用户8000"
    assert data["has_couple"] is False


def test_get_me_unauthorized(client):
    """测试未认证访问。"""
    response = client.get("/api/auth/me")
    assert response.status_code in [401, 403]
