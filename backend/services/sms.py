import os
import secrets
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import redis

logger = logging.getLogger(__name__)

# 配置
ALIYUN_ACCESS_KEY = os.getenv("ALIYUN_ACCESS_KEY")
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM")

# 开发模式：仅当显式设置 DEV_MODE=true 时才启用
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"
DEV_CODE = "123456"

if DEV_MODE:
    logger.warning("⚠️  DEV_MODE 已启用！所有验证码固定为 123456，仅供开发调试使用。")

redis_client = redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379"),
    decode_responses=True,
)


def send_email_code(to_email: str, code: str) -> bool:
    """发送邮箱验证码。"""
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_FROM
        msg["To"] = to_email
        msg["Subject"] = "咔哒 - 验证码"

        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #ff6b81;">咔哒 - 验证码</h2>
            <p>您的验证码是：</p>
            <h1 style="color: #ff4757; font-size: 36px; letter-spacing: 5px;">{code}</h1>
            <p style="color: #666;">验证码 5 分钟内有效，请勿泄露给他人。</p>
            <hr style="border: 1px solid #eee;">
            <p style="color: #999; font-size: 12px;">此邮件由咔哒系统发送，请勿回复。</p>
        </body>
        </html>
        """

        msg.attach(MIMEText(body, "html", "utf-8"))

        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM, to_email, msg.as_string())

        return True
    except Exception as e:
        print(f"发送邮件失败: {e}")
        return False


def send_verification_code(phone: str, email: str = None) -> str:
    """发送验证码，返回验证码内容。

    Args:
        phone: 手机号（用作 Redis key）
        email: 邮箱地址（如果提供则发送邮箱验证码）
    """
    code = str(secrets.randbelow(900000) + 100000)  # 6位数字，密码学安全

    if DEV_MODE:
        code = DEV_CODE
    elif email and SMTP_USER:
        send_email_code(email, code)
    elif ALIYUN_ACCESS_KEY:
        # TODO: 接入阿里云短信
        pass

    # 存入 Redis，5 分钟过期
    redis_client.setex(f"sms:{phone}", 300, code)
    # 限频：60 秒内不能重复发送
    redis_client.setex(f"sms:limit:{phone}", 60, "1")
    return code


MAX_VERIFY_ATTEMPTS = 5  # 最大验证尝试次数


def verify_code(phone: str, code: str) -> bool:
    """校验验证码是否正确，超过最大尝试次数后锁定。"""
    attempts_key = f"sms:attempts:{phone}"
    attempts = int(redis_client.get(attempts_key) or 0)

    if attempts >= MAX_VERIFY_ATTEMPTS:
        # 清除验证码和尝试计数，强制重新获取
        redis_client.delete(f"sms:{phone}")
        redis_client.delete(attempts_key)
        return False

    stored = redis_client.get(f"sms:{phone}")
    if stored and stored == code:
        # 验证成功，清除计数和验证码
        redis_client.delete(f"sms:{phone}")
        redis_client.delete(attempts_key)
        return True

    # 验证失败，增加尝试计数（与验证码 TTL 一致，5 分钟过期）
    redis_client.setex(attempts_key, 300, attempts + 1)
    return False


def is_rate_limited(phone: str) -> bool:
    """检查是否在限频中。"""
    return redis_client.exists(f"sms:limit:{phone}") > 0
