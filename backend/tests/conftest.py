import os
import pytest
import redis
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 设置测试模式
os.environ["DEV_MODE"] = "true"

from database import Base, get_db
from main import app

# 使用 SQLite 作为测试数据库
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redis 连接
redis_client = redis.Redis(host="localhost", port=6379, db=0)


@pytest.fixture(scope="function")
def db():
    """创建测试数据库会话。"""
    # 清除 Redis 数据
    redis_client.flushdb()

    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """创建测试客户端。"""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    """创建已认证用户的 headers。"""
    # 发送验证码
    response = client.post("/api/auth/send-code", json={"phone": "13800138000"})
    assert response.status_code == 200

    # 登录
    response = client.post("/api/auth/login", json={"phone": "13800138000", "code": "123456"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}
