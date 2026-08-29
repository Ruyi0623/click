import os
import httpx

WECHAT_APPID = os.getenv("WECHAT_APPID", "")
WECHAT_SECRET = os.getenv("WECHAT_SECRET", "")


async def code2session(code: str) -> dict:
    """
    用微信 wx.login() 获取的 code 换取 openid 和 session_key。

    返回: {"openid": "...", "session_key": "...", "unionid": "..."}
    抛出: ValueError 如果 code 无效或配置缺失
    """
    if not WECHAT_APPID or not WECHAT_SECRET:
        raise ValueError("WECHAT_APPID 或 WECHAT_SECRET 未配置")

    url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": WECHAT_APPID,
        "secret": WECHAT_SECRET,
        "js_code": code,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, timeout=10)
        data = resp.json()

    if "errcode" in data and data["errcode"] != 0:
        raise ValueError(f"微信登录失败: {data.get('errmsg', '未知错误')}")

    if "openid" not in data:
        raise ValueError("微信返回数据异常，缺少 openid")

    return data
