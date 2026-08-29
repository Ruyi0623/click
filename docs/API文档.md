# 咔哒 API 文档

> **版本** 1.0.0 · **基础路径** `/api` · **协议** HTTPS

---

## 概述

咔哒 API 是一套为情侣提供私密专属空间的 RESTful 接口，支持手机号验证码登录、配对码绑定、纪念日管理、共享相册、愿望清单等功能。只有配对成功的两人才能访问共享数据。

### 技术栈

| 类别 | 技术 | 说明 |
|------|------|------|
| 语言 | Python 3.11+ | — |
| 框架 | FastAPI | 自动生成 OpenAPI 文档 |
| 数据库 | MySQL 8 | 主数据存储 |
| ORM | SQLAlchemy 2.0 | 数据库操作 |
| 缓存 | Redis | 验证码、配对码存储 |
| 认证 | JWT | 单 Token，有效期 7 天 |
| 图片存储 | 本地目录 | Nginx 托管，后期迁移 MinIO |

### 通用说明

- 所有响应均为 JSON 格式
- 时间字段使用 ISO 8601 格式（`YYYY-MM-DD` 或 `YYYY-MM-DDTHH:MM:SS`）
- ID 字段均为 UUID 字符串
- 需要认证的接口必须在请求头携带 `Authorization: Bearer <token>`

---

## 认证

### 认证方式

采用 JWT Bearer Token 认证。登录成功后获取 `access_token`，后续请求在 Header 中携带：

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

Token 有效期为 7 天，过期后需重新登录。

---

## 端点列表

### 系统

#### `GET /`

根路径，返回 API 基本信息。

**响应**

```json
{
  "message": "咔哒 API v1.0"
}
```

> 当 `DEBUG_MODE=true` 时，响应会额外包含 `"docs": "/docs"`。

#### `GET /api/health`

健康检查。

**响应**

```json
{
  "status": "ok"
}
```

---

### 认证模块

#### `POST /api/auth/send-code`

发送短信验证码。

**请求体**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `phone` | string | 是 | 手机号，11~20 位 |

```json
{
  "phone": "13800138000"
}
```

**响应** `200`

```json
{
  "message": "验证码已发送"
}
```

**错误**

| 状态码 | 说明 |
|--------|------|
| `429` | 60 秒内重复请求 |

---

#### `POST /api/auth/login`

手机号 + 验证码登录或注册。首次登录自动注册账号。

**请求体**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `phone` | string | 是 | 手机号 |
| `code` | string | 是 | 6 位验证码 |
| `nickname` | string | 否 | 昵称，首次注册时使用，不填则自动生成 |

```json
{
  "phone": "13800138000",
  "code": "123456",
  "nickname": "小明"
}
```

**响应** `200`

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "nickname": "小明"
}
```

**错误**

| 状态码 | 说明 |
|--------|------|
| `400` | 验证码错误或已过期 |

---

#### `GET /api/auth/me`

获取当前登录用户信息。

**需要认证** 是

**响应** `200`

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "phone": "13800138000",
  "nickname": "小明",
  "avatar_url": null,
  "has_couple": true
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 用户 ID |
| `phone` | string | 手机号 |
| `nickname` | string | 昵称 |
| `avatar_url` | string \| null | 头像 URL |
| `has_couple` | boolean | 是否已配对 |

---

### 配对模块

#### `POST /api/couple/generate`

生成配对码。配对码有效期 5 分钟，同一用户重复生成会覆盖旧码。

**需要认证** 是

**响应** `200`

```json
{
  "code": "384721",
  "expires_in": 300
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | string | 6 位数字配对码 |
| `expires_in` | int | 过期时间（秒） |

**错误**

| 状态码 | 说明 |
|--------|------|
| `400` | 已有伴侣，请先解除配对 |

---

#### `POST /api/couple/confirm`

输入配对码完成配对。使用 Redis `GETDEL` 原子操作防止并发竞争。

**需要认证** 是

**请求体**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `code` | string | 是 | 6 位配对码 |
| `start_date` | string (date) | 否 | 恋爱起始日期，默认当天 |

```json
{
  "code": "384721",
  "start_date": "2024-01-15"
}
```

**响应** `200`

```json
{
  "message": "配对成功",
  "couple_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901"
}
```

**错误**

| 状态码 | 说明 |
|--------|------|
| `400` | 配对码无效或已过期 |
| `400` | 不能和自己配对 |
| `400` | 其中一方已有伴侣，配对失败 |

---

#### `GET /api/couple/info`

获取配对信息，包括伴侣资料和在一起天数。

**需要认证** 是

**响应** `200`

```json
{
  "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "partner_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
  "partner_nickname": "小红",
  "partner_avatar": null,
  "start_date": "2024-01-15",
  "days_together": 498
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 配对关系 ID |
| `partner_id` | string | 伴侣用户 ID |
| `partner_nickname` | string | 伴侣昵称 |
| `partner_avatar` | string \| null | 伴侣头像 |
| `start_date` | date | 恋爱起始日期 |
| `days_together` | int | 在一起天数 |

**错误**

| 状态码 | 说明 |
|--------|------|
| `404` | 尚未配对 |

---

#### `POST /api/couple/unbind`

解除配对关系。

**需要认证** 是

**响应** `200`

```json
{
  "message": "已解除配对"
}
```

**错误**

| 状态码 | 说明 |
|--------|------|
| `404` | 尚未配对 |

---

### 纪念日模块

#### `GET /api/anniversaries`

获取纪念日列表，按距离下次日期升序排列。

**需要认证** 是

**响应** `200`

```json
[
  {
    "id": "d4e5f6a7-b8c9-0123-defa-234567890123",
    "title": "在一起纪念日",
    "date": "2024-01-15",
    "repeat_type": "yearly",
    "days_until": 232
  },
  {
    "id": "e5f6a7b8-c9d0-1234-efab-345678901234",
    "title": "第一次旅行",
    "date": "2024-06-20",
    "repeat_type": "none",
    "days_until": null
  }
]
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 纪念日 ID |
| `title` | string | 标题 |
| `date` | date | 日期 |
| `repeat_type` | string | 重复类型：`yearly`（每年）/ `none`（不重复） |
| `days_until` | int \| null | 距离下次天数，已过期的一次性纪念日返回 `null` |

---

#### `POST /api/anniversaries`

创建纪念日。

**需要认证** 是

**请求体**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | 是 | 标题，1~100 字符 |
| `date` | date | 是 | 日期，格式 `YYYY-MM-DD` |
| `repeat_type` | string | 否 | `yearly`（默认）/ `none` |

```json
{
  "title": "在一起纪念日",
  "date": "2024-01-15",
  "repeat_type": "yearly"
}
```

**响应** `200` — 返回创建的纪念日对象（同列表格式）。

**错误**

| 状态码 | 说明 |
|--------|------|
| `400` | 尚未配对 |

---

#### `PUT /api/anniversaries/{anniversary_id}`

更新纪念日。所有字段可选，仅传需要修改的字段。

**需要认证** 是

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| `anniversary_id` | string | 纪念日 ID |

**请求体**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | 否 | 新标题 |
| `date` | date | 否 | 新日期 |
| `repeat_type` | string | 否 | 新重复类型 |

```json
{
  "title": "恋爱纪念日"
}
```

**响应** `200` — 返回更新后的纪念日对象。

**错误**

| 状态码 | 说明 |
|--------|------|
| `400` | 尚未配对 |
| `404` | 纪念日不存在 |

---

#### `DELETE /api/anniversaries/{anniversary_id}`

删除纪念日。

**需要认证** 是

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| `anniversary_id` | string | 纪念日 ID |

**响应** `200`

```json
{
  "message": "已删除"
}
```

**错误**

| 状态码 | 说明 |
|--------|------|
| `400` | 尚未配对 |
| `404` | 纪念日不存在 |

---

### 相册模块

#### `GET /api/photos`

获取共享相册列表，按上传时间倒序排列。

**需要认证** 是

**响应** `200`

```json
[
  {
    "id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
    "uploader_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "url": "https://yourdomain.com/uploads/couple_id/photo.jpg",
    "thumbnail_url": "https://yourdomain.com/uploads/couple_id/thumb.jpg",
    "caption": "今天的晚餐",
    "width": 1920,
    "height": 1080,
    "taken_at": null,
    "created_at": "2024-12-01T18:30:00"
  }
]
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 照片 ID |
| `uploader_id` | string | 上传者 ID |
| `url` | string | 原图 URL |
| `thumbnail_url` | string \| null | 缩略图 URL |
| `caption` | string \| null | 图片描述 |
| `width` | int \| null | 原图宽度 |
| `height` | int \| null | 原图高度 |
| `taken_at` | datetime \| null | 拍摄时间 |
| `created_at` | datetime | 上传时间 |

---

#### `POST /api/photos`

上传照片到共享相册。自动生成 400x400 缩略图。

**需要认证** 是

**请求格式** `multipart/form-data`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file` | file | 是 | 图片文件（jpg/jpeg/png/gif/webp/bmp/heic，最大 10MB） |
| `caption` | string | 否 | 图片描述 |

**响应** `200` — 返回照片对象（同列表格式）。

**错误**

| 状态码 | 说明 |
|--------|------|
| `400` | 尚未配对 |
| `400` | 不支持的文件类型 |
| `400` | 文件大小超过 10MB 限制 |
| `400` | 文件内容不是有效的图片格式 |

---

#### `DELETE /api/photos/{photo_id}`

删除照片。仅上传者可删除，同时删除原图和缩略图文件。

**需要认证** 是

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| `photo_id` | string | 照片 ID |

**响应** `200`

```json
{
  "message": "已删除"
}
```

**错误**

| 状态码 | 说明 |
|--------|------|
| `400` | 尚未配对 |
| `404` | 照片不存在 |
| `403` | 只能删除自己上传的照片 |

---

### 愿望清单模块

#### `GET /api/wishes`

获取愿望清单。未完成的排在前面，同状态按创建时间倒序。

**需要认证** 是

**响应** `200`

```json
[
  {
    "id": "a7b8c9d0-e1f2-3456-abcd-567890123456",
    "created_by": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "content": "一起去看日出",
    "is_done": false,
    "done_at": null
  },
  {
    "id": "b8c9d0e1-f2a3-4567-bcde-678901234567",
    "created_by": "c3d4e5f6-a7b8-9012-cdef-123456789012",
    "content": "学会做蛋糕",
    "is_done": true,
    "done_at": "2024-11-20T10:30:00"
  }
]
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 愿望 ID |
| `created_by` | string | 创建者 ID |
| `content` | string | 愿望内容 |
| `is_done` | boolean | 是否完成 |
| `done_at` | datetime \| null | 完成时间 |

---

#### `POST /api/wishes`

添加愿望。

**需要认证** 是

**请求体**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `content` | string | 是 | 愿望内容，1~200 字符 |

```json
{
  "content": "一起去看日出"
}
```

**响应** `200` — 返回创建的愿望对象。

**错误**

| 状态码 | 说明 |
|--------|------|
| `400` | 尚未配对 |

---

#### `PUT /api/wishes/{wish_id}`

更新愿望。可修改内容或标记完成。

**需要认证** 是

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| `wish_id` | string | 愿望 ID |

**请求体**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `content` | string | 否 | 新内容 |
| `is_done` | boolean | 否 | 设为 `true` 标记完成，`false` 取消完成 |

```json
{
  "is_done": true
}
```

**响应** `200` — 返回更新后的愿望对象。

**错误**

| 状态码 | 说明 |
|--------|------|
| `400` | 尚未配对 |
| `404` | 愿望不存在 |

---

#### `DELETE /api/wishes/{wish_id}`

删除愿望。

**需要认证** 是

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| `wish_id` | string | 愿望 ID |

**响应** `200`

```json
{
  "message": "已删除"
}
```

**错误**

| 状态码 | 说明 |
|--------|------|
| `400` | 尚未配对 |
| `404` | 愿望不存在 |

---

### 心情模块

#### `GET /api/moods`

获取心情列表（自己和伴侣的）。

**需要认证** 是

**响应** `200`

```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "emoji": "😊",
    "mood_date": "2026-05-29"
  }
]
```

**错误**

| 状态码 | 说明 |
|--------|------|
| `400` | 尚未配对 |

---

#### `POST /api/moods`

记录今天的心情。同一天重复提交会更新。

**需要认证** 是

**请求体**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `emoji` | string | 是 | 心情表情（1-10 字符） |
| `mood_date` | string | 是 | 日期，格式 `YYYY-MM-DD` |

```json
{
  "emoji": "😊",
  "mood_date": "2026-05-29"
}
```

**响应** `200` — 返回心情对象。

**错误**

| 状态码 | 说明 |
|--------|------|
| `400` | 尚未配对 |

---

#### `DELETE /api/moods/{mood_id}`

删除心情记录。

**需要认证** 是

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| `mood_id` | string | 心情 ID |

**响应** `200`

```json
{
  "message": "已删除"
}
```

**错误**

| 状态码 | 说明 |
|--------|------|
| `404` | 心情记录不存在 |

---

### 聊天模块

#### `GET /api/messages`

获取聊天消息列表。

**需要认证** 是

**查询参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `limit` | integer | 否 | 返回数量，默认 50 |

**响应** `200`

```json
[
  {
    "id": "uuid",
    "sender_id": "uuid",
    "type": "text",
    "content": "你好呀！",
    "created_at": "2026-05-29T10:30:00"
  }
]
```

**错误**

| 状态码 | 说明 |
|--------|------|
| `400` | 尚未配对 |

---

#### `POST /api/messages`

发送消息。

**需要认证** 是

**请求体**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `content` | string | 是 | 消息内容 |
| `type` | string | 否 | 消息类型，`text` 或 `image`，默认 `text` |

```json
{
  "content": "你好呀！",
  "type": "text"
}
```

**响应** `200` — 返回消息对象。

**错误**

| 状态码 | 说明 |
|--------|------|
| `400` | 尚未配对 |

---

#### `DELETE /api/messages/{message_id}`

删除消息（只能删除自己的）。

**需要认证** 是

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| `message_id` | string | 消息 ID |

**响应** `200`

```json
{
  "message": "已删除"
}
```

**错误**

| 状态码 | 说明 |
|--------|------|
| `404` | 消息不存在 |

---

### 恋爱月刊模块

#### `GET /api/magazines`

获取月刊列表。

**需要认证** 是

**响应** `200`

```json
[
  {
    "id": "uuid",
    "year": "2026",
    "month": "05",
    "content": "月刊内容...",
    "created_at": "2026-06-01T00:00:00"
  }
]
```

**错误**

| 状态码 | 说明 |
|--------|------|
| `400` | 尚未配对 |

---

#### `POST /api/magazines/generate`

生成恋爱月刊。AI 会根据当月的互动数据自动生成月刊。

**需要认证** 是

**请求体**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `year` | string | 是 | 年份，如 `2026` |
| `month` | string | 是 | 月份，如 `05` |

```json
{
  "year": "2026",
  "month": "05"
}
```

**响应** `200` — 返回生成的月刊对象。

**错误**

| 状态码 | 说明 |
|--------|------|
| `400` | 尚未配对或该月月刊已生成 |
| `500` | 生成失败（如 AI 服务不可用） |

---

#### `GET /api/magazines/{magazine_id}`

获取月刊详情。

**需要认证** 是

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| `magazine_id` | string | 月刊 ID |

**响应** `200` — 返回月刊对象。

**错误**

| 状态码 | 说明 |
|--------|------|
| `404` | 月刊不存在 |

---

#### `DELETE /api/magazines/{magazine_id}`

删除月刊。

**需要认证** 是

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| `magazine_id` | string | 月刊 ID |

**响应** `200`

```json
{
  "message": "已删除"
}
```

**错误**

| 状态码 | 说明 |
|--------|------|
| `404` | 月刊不存在 |

---

### 恋爱存折模块

#### 心愿基金

##### `GET /api/funds`

获取心愿基金列表。

**需要认证** 是

**响应** `200`

```json
[
  {
    "id": "uuid",
    "name": "去大理旅行",
    "target_amount": 5000,
    "current_amount": 1500,
    "icon": "✈️",
    "progress": 30.0,
    "created_at": "2026-05-01T00:00:00"
  }
]
```

---

##### `POST /api/funds`

创建心愿基金。

**需要认证** 是

**请求体**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 基金名称 |
| `target_amount` | float | 是 | 目标金额 |
| `icon` | string | 否 | 图标，默认 🎯 |

```json
{
  "name": "去大理旅行",
  "target_amount": 5000,
  "icon": "✈️"
}
```

**响应** `200` — 返回基金对象。

---

##### `POST /api/funds/{fund_id}/contribute`

向心愿基金投入资金。

**需要认证** 是

**请求体**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `amount` | float | 是 | 投入金额 |
| `note` | string | 否 | 备注 |

```json
{
  "amount": 500,
  "note": "省下的午饭钱"
}
```

**响应** `200` — 返回投入记录。

---

##### `GET /api/funds/{fund_id}/contributions`

获取基金投入记录。

**需要认证** 是

**响应** `200` — 返回投入记录列表。

---

##### `DELETE /api/funds/{fund_id}`

删除心愿基金。

**需要认证** 是

**响应** `200`

```json
{
  "message": "已删除"
}
```

---

#### 账单系统

##### `GET /api/transactions`

获取账单列表。

**需要认证** 是

**查询参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `limit` | integer | 否 | 返回数量，默认 50 |

**响应** `200`

```json
[
  {
    "id": "uuid",
    "paid_by": "uuid",
    "amount": 260,
    "category": "餐饮",
    "description": "火锅",
    "split_type": "equal",
    "photo_url": null,
    "mood": "超级开心",
    "created_at": "2026-05-01T12:00:00"
  }
]
```

---

##### `POST /api/transactions`

创建账单。

**需要认证** 是

**请求体**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `amount` | float | 是 | 金额 |
| `category` | string | 是 | 分类（餐饮、交通、娱乐等） |
| `description` | string | 否 | 描述 |
| `split_type` | string | 否 | 分摊方式：`equal`/`payer_full`/`other_full`/`fund` |
| `photo_url` | string | 否 | 照片 URL |
| `mood` | string | 否 | 心情 |

```json
{
  "amount": 260,
  "category": "餐饮",
  "description": "火锅",
  "split_type": "equal",
  "mood": "超级开心"
}
```

**响应** `200` — 返回账单对象。

---

##### `GET /api/transactions/balance`

获取账务平衡信息。

**需要认证** 是

**响应** `200`

```json
{
  "user1_id": "uuid",
  "user1_nickname": "用户1",
  "user1_paid": 1500,
  "user2_id": "uuid",
  "user2_nickname": "用户2",
  "user2_paid": 1000,
  "balance": 250,
  "who_owes": "用户2欠用户1 250.00 元"
}
```

---

##### `DELETE /api/transactions/{transaction_id}`

删除账单。

**需要认证** 是

**响应** `200`

```json
{
  "message": "已删除"
}
```

---

#### 恋爱罚单

##### `GET /api/penalties`

获取罚单列表。

**需要认证** 是

**响应** `200`

```json
[
  {
    "id": "uuid",
    "issuer_id": "uuid",
    "offender_id": "uuid",
    "reason": "打游戏超时",
    "penalty_type": "money",
    "amount": 10,
    "action": null,
    "is_done": false,
    "done_at": null,
    "created_at": "2026-05-01T12:00:00"
  }
]
```

---

##### `POST /api/penalties`

开具恋爱罚单。

**需要认证** 是

**请求体**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `offender_id` | string | 是 | 被罚人 ID |
| `reason` | string | 是 | 罚单原因 |
| `penalty_type` | string | 否 | 类型：`money`（罚款）或 `action`（行动） |
| `amount` | float | 条件 | 罚款金额（penalty_type=money 时必填） |
| `action` | string | 条件 | 行动内容（penalty_type=action 时必填） |

```json
{
  "offender_id": "uuid",
  "reason": "打游戏超时",
  "penalty_type": "money",
  "amount": 10
}
```

**响应** `200` — 返回罚单对象。

---

##### `POST /api/penalties/{penalty_id}/done`

标记罚单已完成（被罚方调用）。

**需要认证** 是

**响应** `200` — 返回更新后的罚单对象。

---

##### `DELETE /api/penalties/{penalty_id}`

删除罚单。

**需要认证** 是

**响应** `200`

```json
{
  "message": "已删除"
}
```

---

### 足迹地图模块

#### `GET /api/footprints`

获取足迹列表。

**需要认证** 是

**响应** `200`

```json
[
  {
    "id": "uuid",
    "created_by": "uuid",
    "name": "西湖",
    "latitude": 30.259244,
    "longitude": 120.148516,
    "visited_at": "2026-05-01",
    "note": "一起看了日落",
    "created_at": "2026-05-01T12:00:00"
  }
]
```

---

#### `POST /api/footprints`

添加足迹。

**需要认证** 是

**请求体**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 地点名称 |
| `latitude` | float | 是 | 纬度 |
| `longitude` | float | 是 | 经度 |
| `visited_at` | string | 是 | 到访日期（YYYY-MM-DD） |
| `note` | string | 否 | 备注 |

```json
{
  "name": "西湖",
  "latitude": 30.259244,
  "longitude": 120.148516,
  "visited_at": "2026-05-01",
  "note": "一起看了日落"
}
```

**响应** `200` — 返回足迹对象。

---

#### `GET /api/footprints/{footprint_id}`

获取足迹详情。

**需要认证** 是

**响应** `200` — 返回足迹对象。

---

#### `PUT /api/footprints/{footprint_id}`

更新足迹。

**需要认证** 是

**请求体** — 同创建足迹。

**响应** `200` — 返回更新后的足迹对象。

---

#### `DELETE /api/footprints/{footprint_id}`

删除足迹。

**需要认证** 是

**响应** `200`

```json
{
  "message": "已删除"
}
```

---

### 时光胶囊模块

#### `GET /api/capsules`

获取时光胶囊列表。

**需要认证** 是

**说明** 未到期的胶囊内容会显示为 "🔒 未到期，暂不可见"。

**响应** `200`

```json
[
  {
    "id": "uuid",
    "created_by": "uuid",
    "content": "写给未来的我们...",
    "open_at": "2026-08-01T00:00:00",
    "is_opened": false,
    "created_at": "2026-05-01T12:00:00"
  }
]
```

---

#### `POST /api/capsules`

创建时光胶囊。

**需要认证** 是

**请求体**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `content` | string | 是 | 胶囊内容 |
| `open_at` | string | 是 | 开启时间（ISO 8601 格式） |

```json
{
  "content": "写给未来的我们：希望我们永远幸福！",
  "open_at": "2026-08-01T00:00:00"
}
```

**响应** `200` — 返回胶囊对象（内容隐藏）。

**错误**

| 状态码 | 说明 |
|--------|------|
| `400` | 尚未配对或开启时间不在未来 |

---

#### `GET /api/capsules/{capsule_id}`

获取时光胶囊详情。

**需要认证** 是

**响应** `200` — 返回胶囊对象。

---

#### `POST /api/capsules/{capsule_id}/open`

手动开启时光胶囊。

**需要认证** 是

**说明** 只有到期后才能开启。

**响应** `200` — 返回已开启的胶囊对象。

**错误**

| 状态码 | 说明 |
|--------|------|
| `400` | 胶囊已开启或尚未到期 |

---

#### `DELETE /api/capsules/{capsule_id}`

删除时光胶囊。

**需要认证** 是

**响应** `200`

```json
{
  "message": "已删除"
}
```

---

## 错误码一览

| 状态码 | 含义 | 常见场景 |
|--------|------|----------|
| `200` | 成功 | 正常响应 |
| `400` | 请求错误 | 参数校验失败、业务逻辑错误（未配对、验证码错误等） |
| `401` | 未认证 | Token 缺失、无效或过期 |
| `403` | 无权限 | 操作他人资源（如删除他人照片） |
| `404` | 不存在 | 资源未找到（纪念日、照片、愿望、配对关系） |
| `429` | 请求过频 | 验证码 60 秒限频 |

**错误响应格式**

```json
{
  "detail": "错误描述信息"
}
```

---

## 部署指南

### 环境要求

| 依赖 | 版本 |
|------|------|
| Python | 3.11+ |
| MySQL | 8.0+ |
| Redis | 6.0+ |
| Nginx | 1.18+ |

### 安装步骤

**1. 克隆项目并安装依赖**

```bash
cd backend
pip install -r requirements.txt
```

**2. 配置环境变量**

```bash
cp .env.example .env
# 编辑 .env 文件，填入数据库密码、JWT 密钥等
```

**3. 创建数据库**

```sql
CREATE DATABASE click_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**4. 初始化数据库表**

```bash
# 使用 Alembic 迁移（推荐）
alembic upgrade head

# 或手动建表（参考项目文档中的 SQL 语句）
```

**5. 启动服务**

```bash
# 开发环境
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产环境
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
```

**6. 访问 API 文档**

浏览器打开 `http://localhost:8000/docs` 查看自动生成的交互式 API 文档。

### Nginx 配置

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # API 接口
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 图片访问
    location /uploads/ {
        alias /app/uploads/;
    }
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}
```

### systemd 服务配置

创建 `/etc/systemd/system/click_app.service`：

```ini
[Unit]
Description=Couple App API
After=network.target mysql.service redis.service

[Service]
User=www
WorkingDirectory=/app/backend
ExecStart=/usr/local/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable click_app
sudo systemctl start click_app
```

### 环境变量说明

| 变量 | 必填 | 说明 |
|------|------|------|
| `DATABASE_URL` | 是 | MySQL 连接字符串 |
| `REDIS_URL` | 是 | Redis 连接地址 |
| `JWT_SECRET` | 是 | JWT 签名密钥，**必须修改**，不安全的默认值会导致启动失败 |
| `JWT_EXPIRE_DAYS` | 否 | Token 有效期，默认 7 天 |
| `UPLOAD_DIR` | 否 | 图片存储目录，默认 `./uploads` |
| `UPLOAD_BASE_URL` | 否 | 图片访问基础 URL |
| `CORS_ORIGINS` | 否 | CORS 允许的前端域名，逗号分隔，留空不允许跨域 |
| `DEBUG_MODE` | 否 | 调试模式，设为 `true` 暴露 `/docs` 文档，生产环境应为 `false` |
| `DEV_MODE` | 否 | 开发模式，设为 `true` 验证码固定为 `123456`，生产环境切勿开启 |
| `ALIYUN_ACCESS_KEY` | 否 | 阿里云 AccessKey |
| `ALIYUN_ACCESS_SECRET` | 否 | 阿里云 AccessSecret |
| `ALIYUN_SMS_SIGN` | 否 | 短信签名 |
| `ALIYUN_SMS_TEMPLATE` | 否 | 短信模板 ID |
| `SMTP_HOST` | 否 | 邮箱 SMTP 服务器地址 |
| `SMTP_PORT` | 否 | 邮箱 SMTP 端口 |
| `SMTP_USER` | 否 | 邮箱账号 |
| `SMTP_PASSWORD` | 否 | 邮箱授权码 |
| `SMTP_FROM` | 否 | 发件人地址 |
| `DEEPSEEK_API_KEY` | 否 | DeepSeek API 密钥（AI 月刊功能） |

---

*文档版本：v1.0.0 · 基于后端代码自动生成*
