import bcrypt


def hash_password(plain: str) -> str:
    """对明文密码进行 bcrypt 哈希。"""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """校验明文密码与哈希是否匹配。"""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
