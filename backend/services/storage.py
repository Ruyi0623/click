import os
import uuid
import shutil
from pathlib import Path
from PIL import Image
from fastapi import UploadFile

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
UPLOAD_BASE_URL = os.getenv("UPLOAD_BASE_URL", "http://localhost:8000/uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# 允许的图片扩展名白名单
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".heic"}

Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


async def save_upload_file(file: UploadFile, couple_id: str) -> dict:
    """保存上传的图片，生成缩略图，返回文件信息。"""
    ext = Path(file.filename).suffix.lower() if file.filename else ".jpg"

    # 校验扩展名
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"不支持的文件类型: {ext}，允许: {', '.join(ALLOWED_EXTENSIONS)}")

    # 读取文件内容
    content = await file.read()

    # 校验文件大小
    if len(content) > MAX_FILE_SIZE:
        raise ValueError(f"文件大小超过限制（最大 {MAX_FILE_SIZE // 1024 // 1024}MB）")

    # 校验文件内容是否为有效图片（使用 Pillow 验证）
    try:
        from io import BytesIO
        img = Image.open(BytesIO(content))
        img.verify()  # 验证图片完整性
        # verify() 后需要重新打开才能获取尺寸
        img = Image.open(BytesIO(content))
        width, height = img.size
    except Exception:
        raise ValueError("文件内容不是有效的图片格式")

    filename = f"{uuid.uuid4().hex}{ext}"
    thumb_filename = f"{uuid.uuid4().hex}_thumb{ext}"

    # 按 couple_id 分目录存储
    couple_dir = Path(UPLOAD_DIR) / couple_id
    couple_dir.mkdir(parents=True, exist_ok=True)

    file_path = couple_dir / filename
    thumb_path = couple_dir / thumb_filename

    # 保存原图
    with open(file_path, "wb") as f:
        f.write(content)

    # 生成缩略图
    thumb_key = None
    try:
        with Image.open(file_path) as img:
            img.thumbnail((400, 400))
            img.save(thumb_path)
            thumb_key = f"{couple_id}/{thumb_filename}"
    except Exception:
        thumb_filename = None

    return {
        "file_key": f"{couple_id}/{filename}",
        "thumbnail_key": thumb_key,
        "width": width,
        "height": height,
        "url": f"{UPLOAD_BASE_URL}/{couple_id}/{filename}",
        "thumbnail_url": f"{UPLOAD_BASE_URL}/{couple_id}/{thumb_filename}" if thumb_filename else None,
    }


def delete_file(file_key: str):
    """删除文件。"""
    file_path = Path(UPLOAD_DIR) / file_key
    if file_path.exists():
        file_path.unlink()
