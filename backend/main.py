import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

from routers import auth_router, couple_router, anniversary_router, photo_router, wish_router, mood_router, message_router, magazine_router, fund_router, transaction_router, penalty_router, footprint_router, capsule_router, collection_router, diary_router

# 生产环境关闭文档（通过环境变量控制）
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

app = FastAPI(
    title="咔哒 API",
    description="咔哒 - 情侣私密专属空间的 REST API",
    version="1.0.0",
    docs_url="/docs" if DEBUG_MODE else None,
    redoc_url="/redoc" if DEBUG_MODE else None,
    openapi_url="/openapi.json" if DEBUG_MODE else None,
    redirect_slashes=False,
)

# CORS 配置：从环境变量读取允许的前端域名，逗号分隔
# 示例：CORS_ORIGINS=http://localhost:5173,https://your-domain.com
_cors_origins_str = os.getenv("CORS_ORIGINS", "")
_cors_origins = [o.strip() for o in _cors_origins_str.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins if _cors_origins else [],  # 空列表 = 不允许任何跨域
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# 挂载图片目录
upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
os.makedirs(upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

# 注册路由
app.include_router(auth_router, prefix="/api")
app.include_router(couple_router, prefix="/api")
app.include_router(anniversary_router, prefix="/api")
app.include_router(photo_router, prefix="/api")
app.include_router(wish_router, prefix="/api")
app.include_router(mood_router, prefix="/api")
app.include_router(message_router, prefix="/api")
app.include_router(magazine_router, prefix="/api")
app.include_router(fund_router, prefix="/api")
app.include_router(transaction_router, prefix="/api")
app.include_router(penalty_router, prefix="/api")
app.include_router(footprint_router, prefix="/api")
app.include_router(capsule_router, prefix="/api")
app.include_router(collection_router, prefix="/api")
app.include_router(diary_router, prefix="/api")


@app.get("/")
def root():
    info = {"message": "咔哒 API v1.0"}
    if DEBUG_MODE:
        info["docs"] = "/docs"
    return info


@app.get("/api/health")
def health():
    return {"status": "ok"}
