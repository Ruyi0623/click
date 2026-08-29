"""测试足迹地图模块。"""
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


def test_create_footprint(client, paired_headers):
    """测试创建足迹。"""
    response = client.post("/api/footprints", headers=paired_headers, json={
        "name": "西湖",
        "latitude": 30.259244,
        "longitude": 120.148516,
        "visited_at": "2026-05-01",
        "note": "一起看了日落"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "西湖"
    assert data["latitude"] == 30.259244
    assert data["longitude"] == 120.148516
    assert data["note"] == "一起看了日落"


def test_create_footprint_not_paired(client, auth_headers):
    """测试未配对时创建足迹。"""
    response = client.post("/api/footprints", headers=auth_headers, json={
        "name": "测试地点",
        "latitude": 30.0,
        "longitude": 120.0,
        "visited_at": "2026-05-01"
    })
    assert response.status_code == 400


def test_list_footprints(client, paired_headers):
    """测试获取足迹列表。"""
    client.post("/api/footprints", headers=paired_headers, json={
        "name": "西湖",
        "latitude": 30.259244,
        "longitude": 120.148516,
        "visited_at": "2026-05-01"
    })
    client.post("/api/footprints", headers=paired_headers, json={
        "name": "故宫",
        "latitude": 39.916345,
        "longitude": 116.397155,
        "visited_at": "2026-05-15"
    })

    response = client.get("/api/footprints", headers=paired_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_footprint(client, paired_headers):
    """测试获取足迹详情。"""
    response = client.post("/api/footprints", headers=paired_headers, json={
        "name": "西湖",
        "latitude": 30.259244,
        "longitude": 120.148516,
        "visited_at": "2026-05-01",
        "note": "测试备注"
    })
    footprint_id = response.json()["id"]

    response = client.get(f"/api/footprints/{footprint_id}", headers=paired_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "西湖"
    assert response.json()["note"] == "测试备注"


def test_update_footprint(client, paired_headers):
    """测试更新足迹。"""
    response = client.post("/api/footprints", headers=paired_headers, json={
        "name": "西湖",
        "latitude": 30.259244,
        "longitude": 120.148516,
        "visited_at": "2026-05-01"
    })
    footprint_id = response.json()["id"]

    response = client.put(f"/api/footprints/{footprint_id}", headers=paired_headers, json={
        "name": "杭州西湖",
        "latitude": 30.259244,
        "longitude": 120.148516,
        "visited_at": "2026-05-01",
        "note": "更新了名称"
    })
    assert response.status_code == 200
    assert response.json()["name"] == "杭州西湖"
    assert response.json()["note"] == "更新了名称"


def test_delete_footprint(client, paired_headers):
    """测试删除足迹。"""
    response = client.post("/api/footprints", headers=paired_headers, json={
        "name": "西湖",
        "latitude": 30.259244,
        "longitude": 120.148516,
        "visited_at": "2026-05-01"
    })
    footprint_id = response.json()["id"]

    response = client.delete(f"/api/footprints/{footprint_id}", headers=paired_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "已删除"

    response = client.get("/api/footprints", headers=paired_headers)
    assert len(response.json()) == 0


def test_get_footprint_not_found(client, paired_headers):
    """测试获取不存在的足迹。"""
    response = client.get("/api/footprints/999", headers=paired_headers)
    assert response.status_code == 404
