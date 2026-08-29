import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import redis
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:123456@localhost:3306/click_app")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

redis_client = redis.from_url(REDIS_URL, decode_responses=True)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_redis():
    return redis_client
