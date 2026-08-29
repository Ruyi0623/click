# 咔哒 App — API 安全防护分析

> 分析日期：2026-06-03
> 后端框架：Python / FastAPI
> 部署方式：Docker + Nginx 反向代理

---

## 一、已有防护措施

### 1. JWT Token 认证

| 项目 | 说明 |
|------|------|
| 算法 | HS256（python-jose） |
| 有效期 | 7 天 |
| 密钥来源 | 环境变量 `JWT_SECRET` |
| 启动检查 | 拒绝空密钥和常见弱密钥启动 |
| 覆盖范围 | 所有业务接口通过 `Depends(get_current_user)` 强制校验 |

**认证流程：**
```
客户端 → Authorization: Bearer <token> → FastAPI 依赖注入 → decode_token() → 查询数据库 → 返回 User 对象
```

未携带或无效 Token 的请求直接返回 **HTTP 401**。

**相关文件：** `backend/auth.py`、`backend/routers/auth.py`

---

### 2. 手机验证码防暴力破解

| 防护项 | 实现方式 |
|--------|----------|
| 发送频率限制 | 同一手机号 60 秒内只能发送一次（Redis TTL） |
| 验证尝试上限 | 最多 5 次错误，超限后验证码作废需重新获取 |
| 验证码有效期 | 5 分钟（Redis TTL 300s） |
| 随机数生成 | `secrets.randbelow()` 密码学安全 |
| 开发模式 | 仅 `DEV_MODE=true` 时启用固定验证码 `123456`，默认关闭 |

**相关文件：** `backend/services/sms.py`

---

### 3. CORS 跨域限制

```python
# 配置来源：环境变量 CORS_ORIGINS（逗号分隔域名列表）
# 默认值：空 → 不允许任何跨域请求
allow_credentials = True
allow_methods = ["GET", "POST", "PUT", "DELETE"]
allow_headers = ["Authorization", "Content-Type"]
```

**相关文件：** `backend/main.py`

---

### 4. 数据隔离（Couple 作用域）

所有业务接口都通过 `get_couple()` 函数校验当前用户只能访问自己情侣关系下的数据：

```python
Couple.query.filter(
    (Couple.user1_id == user_id) | (Couple.user2_id == user_id)
)
```

- 未配对用户访问业务接口 → HTTP 400
- 照片删除额外校验：只有上传者本人可删除（HTTP 403）

**覆盖模块：** 纪念日、胶囊、足迹、基金、杂志、消息、心情、罚单、照片、心愿

---

### 5. API 文档访问控制

| 端点 | 生产环境 | 开发环境 |
|------|----------|----------|
| `/docs`（Swagger） | ❌ 关闭 | ✅ 开启 |
| `/redoc`（ReDoc） | ❌ 关闭 | ✅ 开启 |
| `/openapi.json` | ❌ 关闭 | ✅ 开启 |

通过 `DEBUG_MODE` 环境变量控制，默认关闭。

**相关文件：** `backend/main.py`

---

### 6. Nginx 安全响应头

```nginx
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; ..." always;
```

**其他 Nginx 配置：**
- 请求体大小限制：10MB
- MySQL / Redis 仅在 Docker 内网暴露，不映射到宿主机

**相关文件：** `nginx/nginx.conf`

---

### 7. 文件上传安全

| 防护项 | 实现方式 |
|--------|----------|
| 扩展名白名单 | `.jpg .jpeg .png .gif .webp .bmp .heic` |
| 文件大小限制 | 10MB |
| 内容验证 | Pillow `Image.verify()` 确认是合法图片 |
| 文件名处理 | `uuid.uuid4().hex` 重命名，防路径遍历 |
| 存储隔离 | 按 `couple_id` 分目录存储 |
| Content-Type 校验 | 必须以 `image/` 开头 |

**相关文件：** `backend/services/storage.py`、`backend/routers/photo.py`

---

### 8. 配对码安全

- 使用 `secrets.randbelow()` 生成 6 位配对码
- 有效期 5 分钟（Redis TTL）
- 禁止自己和自己配对
- 禁止重复配对
- 生成新码时旧码自动失效

**相关文件：** `backend/routers/couple.py`

---

## 二、未实现的防护措施

| 防护类型 | 说明 | 风险等级 |
|----------|------|----------|
| **HTTPS** | nginx.conf 中 HTTPS 配置已存在但被注释，当前走 HTTP 明文传输 | 🔴 高 |
| **API 签名机制** | 无 HMAC 签名、无请求参数签名 | 🟡 中 |
| **防重放攻击** | 无 nonce / timestamp 校验 | 🟡 中 |
| **请求防篡改** | 无请求 body hash 校验 | 🟡 中 |
| **全局限流** | 仅验证码接口有限流，其他 API 无频率限制 | 🟡 中 |
| **API Key 双层验证** | 无 AppID + AppSecret 机制 | 🟢 低 |
| **Redis 认证** | Redis 无密码保护 | 🟡 中 |
| **数据库连接加密** | MySQL 连接未使用 SSL | 🟢 低 |

---

## 三、安全架构总览

```
                        ┌─────────────────────────────────────────┐
                        │              Internet                    │
                        └──────────────────┬──────────────────────┘
                                           │
                                           ▼
                        ┌─────────────────────────────────────────┐
                        │         Nginx (反向代理)                  │
                        │  • 安全响应头                             │
                        │  • 请求体大小限制 (10MB)                   │
                        │  • HTTPS [待开启]                         │
                        └──────────────────┬──────────────────────┘
                                           │
                                           ▼
                        ┌─────────────────────────────────────────┐
                        │         FastAPI 应用                     │
                        │  • CORS 跨域限制                         │
                        │  • JWT Token 认证 (所有业务接口)           │
                        │  • 数据隔离 (Couple 作用域)               │
                        │  • 验证码防暴力破解                        │
                        │  • 文件上传白名单验证                      │
                        │  • API 文档访问控制                       │
                        └───────┬─────────────────┬───────────────┘
                                │                 │
                                ▼                 ▼
                        ┌──────────────┐  ┌──────────────┐
                        │    MySQL     │  │    Redis     │
                        │  (Docker内网) │  │  (Docker内网) │
                        │  不暴露公网   │  │  不暴露公网   │
                        └──────────────┘  └──────────────┘
```

---

## 四、上线前建议（按优先级）

### 🔴 P0 — 必须做

1. **开启 HTTPS**
   - nginx.conf 中已有注释模板，取消注释并配置 SSL 证书
   - 推荐使用 Let's Encrypt 免费证书
   - 添加 HTTP → HTTPS 301 重定向

2. **更换所有默认密码**
   - `.env` 中的 `JWT_SECRET`、数据库密码、Redis 密码
   - `alembic.ini` 中的数据库连接串

### 🟡 P1 — 强烈建议

3. **添加全局限流**
   - Nginx 层：`limit_req_zone` 限制单 IP 请求频率
   - 或 FastAPI 中间件层实现

4. **Redis 设置密码**
   - docker-compose 中配置 `requirepass`

5. **敏感配置外部化**
   - `.env` 文件不应提交到 Git
   - 生产环境使用 Docker Secrets 或环境变量注入

### 🟢 P2 — 锦上添花

6. **请求签名校验**（HMAC-SHA256）
7. **时间戳 + nonce 防重放**
8. **数据库连接启用 SSL**

---

## 五、结论

当前防护**对情侣日常 App 来说基本合格**：

- ✅ JWT 认证覆盖所有业务接口，不存在未鉴权的数据泄露
- ✅ CORS + 数据隔离 + API 文档关闭，公网暴露面小
- ✅ 后端数据库/缓存都在 Docker 内网，不直接暴露

**最大短板是未开启 HTTPS**，上线前务必补上。其余防护可根据用户量增长逐步加强。
