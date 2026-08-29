"""测试恋爱月刊模块。"""
import pytest
from unittest.mock import patch, MagicMock


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


@patch("routers.magazine.generate_magazine_content")
def test_generate_magazine(mock_generate, client, paired_headers):
    """测试生成月刊。"""
    # Mock AI 生成内容
    mock_generate.return_value = """### 1. 主编致辞
测试主编致辞内容。

### 2. 数据解剖室
测试数据解剖内容。

### 3. 恋爱大赏
测试恋爱大赏内容。

### 4. 恋爱天气预报
测试恋爱天气预报内容。"""

    response = client.post("/api/magazines/generate", headers=paired_headers, json={
        "year": "2026",
        "month": "05"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["year"] == "2026"
    assert data["month"] == "05"
    assert "主编致辞" in data["content"]


@patch("routers.magazine.generate_magazine_content")
def test_generate_magazine_duplicate(mock_generate, client, paired_headers):
    """测试重复生成月刊（支持重新生成）。"""
    # Mock AI 生成内容
    mock_generate.return_value = "测试内容"

    # 第一次生成
    response1 = client.post("/api/magazines/generate", headers=paired_headers, json={
        "year": "2026",
        "month": "05"
    })
    assert response1.status_code == 200
    id1 = response1.json()["id"]

    # 第二次生成应该成功（重新生成）
    response2 = client.post("/api/magazines/generate", headers=paired_headers, json={
        "year": "2026",
        "month": "05"
    })
    assert response2.status_code == 200
    id2 = response2.json()["id"]

    # 列表中应该只有一条记录
    response3 = client.get("/api/magazines", headers=paired_headers)
    month_list = [m for m in response3.json() if m["year"] == "2026" and m["month"] == "05"]
    assert len(month_list) == 1


def test_generate_magazine_not_paired(client, auth_headers):
    """测试未配对时生成月刊。"""
    response = client.post("/api/magazines/generate", headers=auth_headers, json={
        "year": "2026",
        "month": "05"
    })
    assert response.status_code == 400
    assert "尚未配对" in response.json()["detail"]


@patch("routers.magazine.generate_magazine_content")
def test_list_magazines(mock_generate, client, paired_headers):
    """测试获取月刊列表。"""
    # Mock AI 生成内容
    mock_generate.return_value = "测试内容"

    # 生成月刊
    client.post("/api/magazines/generate", headers=paired_headers, json={
        "year": "2026",
        "month": "05"
    })

    # 获取列表
    response = client.get("/api/magazines", headers=paired_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


@patch("routers.magazine.generate_magazine_content")
def test_get_magazine(mock_generate, client, paired_headers):
    """测试获取月刊详情。"""
    # Mock AI 生成内容
    mock_generate.return_value = "测试内容"

    # 生成月刊
    response1 = client.post("/api/magazines/generate", headers=paired_headers, json={
        "year": "2026",
        "month": "05"
    })
    magazine_id = response1.json()["id"]

    # 获取详情
    response2 = client.get(f"/api/magazines/{magazine_id}", headers=paired_headers)
    assert response2.status_code == 200
    assert response2.json()["id"] == magazine_id


@patch("routers.magazine.generate_magazine_content")
def test_delete_magazine(mock_generate, client, paired_headers):
    """测试删除月刊。"""
    # Mock AI 生成内容
    mock_generate.return_value = "测试内容"

    # 生成月刊
    response1 = client.post("/api/magazines/generate", headers=paired_headers, json={
        "year": "2026",
        "month": "05"
    })
    magazine_id = response1.json()["id"]

    # 删除
    response2 = client.delete(f"/api/magazines/{magazine_id}", headers=paired_headers)
    assert response2.status_code == 200
    assert response2.json()["message"] == "已删除"

    # 确认已删除
    response3 = client.get("/api/magazines", headers=paired_headers)
    assert len(response3.json()) == 0
