# 💑 咔哒 App · 产品开发计划书

> **版本** v1.3 · **发布路线** 纯 API → 微信小程序 → App  
> **前端** Uni-app（微信小程序）+ Flutter（App）  
> **后端** Python + FastAPI（纯 REST API）  
> **部署方式** 自有云服务器 · **核心机制** 配对码双向绑定 · **登录方式** 手机号 + 验证码

---

## 目录

1. [项目概述](#一项目概述)
2. [技术架构](#二技术架构)
3. [功能规划](#三功能规划)
4. [数据库设计](#四数据库设计)
5. [配对码核心逻辑](#五配对码核心逻辑)
6. [开发阶段计划](#六开发阶段计划)
7. [部署方案](#七部署方案)
8. [已知风险与解决方案](#八已知风险与解决方案)

---

## 一、项目概述

### 1.1 产品定位

为情侣提供一个**私密、温馨的专属空间**，记录两人的共同生活，包括纪念日、相册、心情、聊天等，只有配对的两人才能共享内容。

### 1.2 目标用户

- 异地恋 / 同城恋侣
- 希望有专属空间记录生活的情侣
- 年龄层：18 ~ 30 岁

### 1.3 发布路线

```
阶段一                阶段二              阶段三
纯 REST API    →   微信小程序    →   Flutter App
（写接口+测试）   （第一个前端）    （完整原生体验）
```

**不做 H5 网页**，后端专注 API，前端从小程序开始，一套 API 供所有端复用。

---

## 二、技术架构

### 2.1 总览

```
┌─────────────────────────────────────────────┐
│                  用户设备                     │
│     微信小程序（Uni-app）│  iOS/Android App   │
│                          │    （Flutter）     │
└──────────────┬───────────┴──────────┬────────┘
               │ HTTPS                │ HTTPS
               └──────────┬───────────┘
                  ┌────────▼────────┐
                  │   Nginx 反向代理  │
                  └────────┬────────┘
                           │
                  ┌────────▼────────┐
                  │   FastAPI 服务   │
                  │  （纯 REST API） │
                  └──┬──────────┬───┘
                     │          │
              ┌──────▼──┐  ┌────▼────┐
              │  MySQL   │  │  Redis  │
              └──────────┘  └─────────┘
                     │
              ┌──────▼──────────┐
              │  本地目录 → MinIO │
              │   (图片存储演进)  │
              └─────────────────┘
```

### 2.2 前端技术栈

#### 微信小程序（Uni-app）

| 类别 | 技术选型 | 说明 |
|------|----------|------|
| 框架 | **Uni-app + Vue 3** | 直接编译微信小程序 |
| 语言 | TypeScript | 类型安全 |
| UI 库 | **uView UI 3** | 专为 Uni-app 设计 |
| 状态管理 | **Pinia** | 轻量，天然支持 TS |
| 地图 | 腾讯地图 SDK | 足迹地图 |

#### App（Flutter）

| 类别 | 技术选型 | 说明 |
|------|----------|------|
| 框架 | **Flutter 3** | iOS + Android 原生体验 |
| 语言 | Dart | 上手快，类 JS 语法 |
| 状态管理 | **Riverpod** | Flutter 主流方案 |
| 网络请求 | Dio | HTTP 库，功能完善 |
| 地图 | flutter_map | 足迹地图 |
| 推送通知 | firebase_messaging | FCM 推送 |
| 本地存储 | Hive | 轻量缓存 |

### 2.3 后端技术栈（分阶段演进）

#### 第一阶段：API 开发期

| 类别 | 技术选型 | 说明 |
|------|----------|------|
| 语言 | **Python 3.11** | 上手快，CS 必学 |
| 框架 | **FastAPI** | 轻量，自带 `/docs` 调试页面 |
| 数据库 | **MySQL 8** | 主数据存储 |
| ORM | **SQLAlchemy + Alembic** | 操作数据库 + 迁移 |
| 缓存 | **Redis** | 仅存验证码 + 配对码 |
| 认证 | **JWT 单 Token** | 有效期 7 天 |
| 图片存储 | **服务器本地目录** | Nginx 托管，零配置 |
| 短信 | **阿里云 SMS** | 约 0.032 元/条 |
| 调试 | **FastAPI /docs** | 自动生成，替代 Postman |
| 部署 | **Nginx + Uvicorn** | 稳定够用 |

#### 第二阶段：小程序上线后补充

| 类别 | 技术选型 | 说明 |
|------|----------|------|
| 实时通信 | **WebSocket** | FastAPI 原生支持 |
| 图片存储 | **MinIO** | 从本地目录迁移，接口不变 |

#### 第三阶段：App 上线后补充

| 类别 | 技术选型 | 说明 |
|------|----------|------|
| 推送通知 | **FCM + APNs** | 安卓 + iOS 推送 |

### 2.4 核心依赖清单

```txt
# requirements.txt
fastapi==0.111.0
uvicorn==0.30.0          # 运行服务器
sqlalchemy==2.0.30       # ORM
alembic==1.13.0          # 数据库迁移
pymysql==1.1.0           # MySQL 驱动
redis==5.0.0             # Redis 客户端
python-jose==3.3.0       # JWT
python-multipart==0.0.9  # 文件上传
pillow==10.3.0           # 图片压缩
alibabacloud-dysmsapi    # 阿里云短信
python-dotenv==1.0.0     # 读取 .env
```

### 2.5 后端项目结构

```
backend/
├── main.py              # 入口文件
├── requirements.txt     # 依赖列表
├── .env                 # 环境变量（不提交 Git）
├── database.py          # 数据库连接
├── models/              # 数据表定义
│   ├── user.py
│   ├── couple.py
│   ├── photo.py
│   └── ...
├── routers/             # 路由（按模块拆分）
│   ├── auth.py          # 登录 / 注册
│   ├── couple.py        # 配对码
│   ├── photo.py         # 相册
│   ├── anniversary.py   # 纪念日
│   ├── wish.py          # 愿望清单
│   ├── mood.py          # 心情同步
│   ├── message.py       # 聊天
│   ├── capsule.py       # 时光胶囊
│   └── footprint.py     # 足迹地图
├── services/            # 业务逻辑
│   ├── sms.py           # 短信发送
│   └── storage.py       # 文件存储
└── uploads/             # 图片本地存储目录
```

### 2.6 运维

| 类别 | 技术选型 | 说明 |
|------|----------|------|
| 服务器 | 2核4G · Ubuntu 22.04 | 够跑到几百对用户 |
| 数据盘 | 100G 独立数据盘 | 专门存图片 |
| 反向代理 | **Nginx** | 路由分发 + 图片文件托管 |
| HTTPS | **Certbot** | Let's Encrypt 免费证书 |
| 进程管理 | **Uvicorn + systemd** | 服务器重启自动恢复 |

---

## 三、功能规划

### 3.1 核心记录功能

| # | 模块 | API 端点 | 说明 |
|---|------|----------|------|
| 1 | **恋爱天数 + 纪念日** | `/anniversaries` | 首页天数 + 纪念日增删改查 |
| 2 | **共享相册** | `/photos` | 上传 / 查询 / 删除，仅两人可见 |
| 3 | **愿望清单** | `/wishes` | 增删 + 标记完成 |

### 3.2 互动功能

| # | 模块 | API 端点 | 说明 |
|---|------|----------|------|
| 4 | **心情同步** | `/moods` | 每日一次，实时可见 |
| 5 | **应用内聊天** | `/messages` + WebSocket | 文字 + 图片 |
| 6 | **随机小任务** | `/tasks/random` | 每日随机，完成打卡 |
| 7 | **时光胶囊** | `/capsules` | 定时解锁 |
| 8 | **足迹地图** | `/footprints` | 坐标记录 + 查询 |

### 3.3 特色功能

| # | 模块 | API 端点 | 说明 |
|---|------|----------|------|
| 9 | **AI 恋爱月刊** | `/magazines` | 基于 DeepSeek API 自动生成月度报告 |
| 10 | **心愿基金** | `/funds` | 共同储蓄目标，进度追踪 |
| 11 | **恋爱账单** | `/transactions` | 双向记账，多种分摊方式 |
| 12 | **恋爱罚单** | `/penalties` | 趣味惩罚机制，罚款或行动 |

### 3.4 系统功能

| # | 模块 | API 端点 | 说明 |
|---|------|----------|------|
| 13 | **手机号登录** | `/auth/send-code` `/auth/login` | 验证码登录（支持邮箱） |
| 14 | **配对码** | `/couple/generate` `/couple/confirm` | 原子操作防并发 |
| 15 | **推送通知** | 第三阶段 | FCM + APNs |
| 16 | **解绑管理** | `/couple/unbind` | 历史数据保留 |

### 3.5 开发优先级

```
🔴 第一阶段（已完成）
   登录 → 配对码 → 纪念日 → 相册 → 愿望清单

🟡 第二阶段（已完成）
   心情同步 → 聊天 → 足迹地图 → 时光胶囊

🟢 第三阶段（已完成）
   AI 月刊 → 恋爱存折（心愿基金 + 账单 + 罚单）

🔵 第四阶段（待开发）
   前端小程序 → Flutter App → 推送通知
```

---

## 四、数据库设计

### 4.1 核心表结构

```sql
-- 用户表
CREATE TABLE users (
  id          VARCHAR(36)   PRIMARY KEY,
  phone       VARCHAR(20)   UNIQUE NOT NULL,
  nickname    VARCHAR(50)   NOT NULL,
  avatar_url  VARCHAR(500),
  created_at  DATETIME      DEFAULT NOW()
);

-- 配对关系表
CREATE TABLE couples (
  id          VARCHAR(36)   PRIMARY KEY,
  user1_id    VARCHAR(36)   NOT NULL,
  user2_id    VARCHAR(36)   NOT NULL,
  start_date  DATE          NOT NULL,
  created_at  DATETIME      DEFAULT NOW(),
  UNIQUE KEY  uq_couple (user1_id, user2_id),
  FOREIGN KEY (user1_id) REFERENCES users(id),
  FOREIGN KEY (user2_id) REFERENCES users(id)
);

-- 纪念日表
CREATE TABLE anniversaries (
  id          VARCHAR(36)   PRIMARY KEY,
  couple_id   VARCHAR(36)   NOT NULL,
  title       VARCHAR(100)  NOT NULL,
  date        DATE          NOT NULL,
  repeat_type ENUM('none','yearly') DEFAULT 'yearly',
  FOREIGN KEY (couple_id) REFERENCES couples(id)
);

-- 相册表
CREATE TABLE photos (
  id            VARCHAR(36)   PRIMARY KEY,
  couple_id     VARCHAR(36)   NOT NULL,
  uploader_id   VARCHAR(36)   NOT NULL,
  file_key      VARCHAR(500)  NOT NULL,
  thumbnail_key VARCHAR(500),
  caption       VARCHAR(200),
  width         INT,
  height        INT,
  taken_at      DATETIME,
  created_at    DATETIME      DEFAULT NOW(),
  FOREIGN KEY   (couple_id) REFERENCES couples(id)
);

-- 愿望清单表
CREATE TABLE wishes (
  id          VARCHAR(36)   PRIMARY KEY,
  couple_id   VARCHAR(36)   NOT NULL,
  created_by  VARCHAR(36)   NOT NULL,
  content     VARCHAR(200)  NOT NULL,
  is_done     BOOLEAN       DEFAULT FALSE,
  done_at     DATETIME,
  FOREIGN KEY (couple_id) REFERENCES couples(id)
);

-- 心情表
CREATE TABLE moods (
  id          VARCHAR(36)   PRIMARY KEY,
  couple_id   VARCHAR(36)   NOT NULL,
  user_id     VARCHAR(36)   NOT NULL,
  emoji       VARCHAR(10)   NOT NULL,
  mood_date   DATE          NOT NULL,
  UNIQUE KEY  uq_mood (user_id, mood_date),
  FOREIGN KEY (couple_id) REFERENCES couples(id)
);

-- 聊天消息表
CREATE TABLE messages (
  id          VARCHAR(36)   PRIMARY KEY,
  couple_id   VARCHAR(36)   NOT NULL,
  sender_id   VARCHAR(36)   NOT NULL,
  type        ENUM('text','image') DEFAULT 'text',
  content     TEXT          NOT NULL,
  created_at  DATETIME      DEFAULT NOW(),
  FOREIGN KEY (couple_id) REFERENCES couples(id)
);

-- 时光胶囊表
CREATE TABLE capsules (
  id          VARCHAR(36)   PRIMARY KEY,
  couple_id   VARCHAR(36)   NOT NULL,
  created_by  VARCHAR(36)   NOT NULL,
  content     TEXT          NOT NULL,
  open_at     DATETIME      NOT NULL,
  is_opened   BOOLEAN       DEFAULT FALSE,
  FOREIGN KEY (couple_id) REFERENCES couples(id)
);

-- 足迹表
CREATE TABLE footprints (
  id          VARCHAR(36)   PRIMARY KEY,
  couple_id   VARCHAR(36)   NOT NULL,
  created_by  VARCHAR(36)   NOT NULL,
  name        VARCHAR(100)  NOT NULL,
  latitude    DECIMAL(10,7) NOT NULL,
  longitude   DECIMAL(10,7) NOT NULL,
  visited_at  DATE          NOT NULL,
  note        TEXT,
  created_at  DATETIME      DEFAULT NOW(),
  FOREIGN KEY (couple_id) REFERENCES couples(id)
);

-- 月刊表
CREATE TABLE magazines (
  id          VARCHAR(36)   PRIMARY KEY,
  couple_id   VARCHAR(36)   NOT NULL,
  year        VARCHAR(4)    NOT NULL,
  month       VARCHAR(2)    NOT NULL,
  content     TEXT          NOT NULL,
  created_at  DATETIME      DEFAULT NOW(),
  FOREIGN KEY (couple_id) REFERENCES couples(id)
);

-- 心愿基金表
CREATE TABLE funds (
  id              VARCHAR(36)   PRIMARY KEY,
  couple_id       VARCHAR(36)   NOT NULL,
  name            VARCHAR(100)  NOT NULL,
  target_amount   FLOAT         NOT NULL,
  current_amount  FLOAT         DEFAULT 0,
  icon            VARCHAR(10)   DEFAULT '🎯',
  created_at      DATETIME      DEFAULT NOW(),
  FOREIGN KEY (couple_id) REFERENCES couples(id)
);

-- 基金投入记录表
CREATE TABLE fund_contributions (
  id          VARCHAR(36)   PRIMARY KEY,
  fund_id     VARCHAR(36)   NOT NULL,
  user_id     VARCHAR(36)   NOT NULL,
  amount      FLOAT         NOT NULL,
  note        VARCHAR(200),
  created_at  DATETIME      DEFAULT NOW(),
  FOREIGN KEY (fund_id) REFERENCES funds(id)
);

-- 账单表
CREATE TABLE transactions (
  id          VARCHAR(36)   PRIMARY KEY,
  couple_id   VARCHAR(36)   NOT NULL,
  paid_by     VARCHAR(36)   NOT NULL,
  amount      FLOAT         NOT NULL,
  category    VARCHAR(50)   NOT NULL,
  description VARCHAR(200),
  split_type  ENUM('equal','payer_full','other_full','fund') DEFAULT 'equal',
  photo_url   VARCHAR(500),
  mood        VARCHAR(100),
  created_at  DATETIME      DEFAULT NOW(),
  FOREIGN KEY (couple_id) REFERENCES couples(id)
);

-- 恋爱罚单表
CREATE TABLE penalties (
  id            VARCHAR(36)   PRIMARY KEY,
  couple_id     VARCHAR(36)   NOT NULL,
  issuer_id     VARCHAR(36)   NOT NULL,
  offender_id   VARCHAR(36)   NOT NULL,
  reason        VARCHAR(200)  NOT NULL,
  penalty_type  VARCHAR(20)   NOT NULL DEFAULT 'money',
  amount        FLOAT,
  action        VARCHAR(200),
  is_done       BOOLEAN       DEFAULT FALSE,
  done_at       DATETIME,
  created_at    DATETIME      DEFAULT NOW(),
  FOREIGN KEY (couple_id) REFERENCES couples(id)
);
```

### 4.2 查询规范

```sql
-- ✅ 配对表查询必须双向 OR，否则漏查
SELECT * FROM couples
WHERE user1_id = ? OR user2_id = ?;
```

---

## 五、配对码核心逻辑

### 5.1 流程图

```
用户 A                         Redis                        用户 B
  │                              │                              │
  │── 1. 检查是否已配对 ─────────>│                              │
  │── 2. 清除旧配对码 ───────────>│ DEL pair:{oldCode}           │
  │── 3. 生成新配对码 ───────────>│ SET pair:123456 = userA (5m) │
  │── 4. 记录当前码 ─────────────>│ SET pair:user:A = 123456(5m) │
  │<─ 5. 返回 123456 ────────────│                              │
  │                              │<── 6. 检查 B 是否已配对 ──────│
  │                              │<── 7. GETDEL pair:123456 ─────│
  │                              │    （原子操作，取出并删除）    │
  │                              │──── 返回 userA ─────────────>│
  │                              │         8. 验证双方均未配对   │
  │                              │         9. 写入 couples 表    │
  │<──────────────── 10. WebSocket 通知双方配对成功 ────────────>│
```

### 5.2 生成配对码

```python
@router.post("/couple/generate")
async def generate_pair_code(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    # 检查是否已有伴侣
    existing = get_couple_by_user(current_user.id, db)
    if existing:
        raise HTTPException(400, "你已有伴侣，请先解除配对")

    # 清除旧配对码
    old_code = await redis.get(f"pair:user:{current_user.id}")
    if old_code:
        await redis.delete(f"pair:{old_code}")

    # 生成新配对码
    code = str(random.randint(100000, 999999))
    await redis.setex(f"pair:{code}", 300, current_user.id)
    await redis.setex(f"pair:user:{current_user.id}", 300, code)

    return {"code": code, "expires_in": 300}
```

### 5.3 确认配对

```python
@router.post("/couple/confirm")
async def confirm_pair(
    body: ConfirmPairRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    # GETDEL 原子操作，防止并发竞争
    partner_id = await redis.getdel(f"pair:{body.code}")
    if not partner_id:
        raise HTTPException(400, "配对码无效或已过期")
    if partner_id == current_user.id:
        raise HTTPException(400, "不能和自己配对")

    # 双重校验
    if get_couple_by_user(partner_id, db) or get_couple_by_user(current_user.id, db):
        raise HTTPException(400, "其中一方已有伴侣，配对失败")

    # 写入数据库
    create_couple(user1_id=partner_id, user2_id=current_user.id, db=db)
    await redis.delete(f"pair:user:{partner_id}")

    return {"message": "配对成功"}
```

---

## 六、开发阶段计划

### 6.1 里程碑总览

```
Week 1       Python + FastAPI 基础学习
Week 2─3     后端 API 全部开发完成
Week 4       部署到服务器，接口联调测试
Week 5─8     Uni-app 微信小程序开发
Week 9─10    小程序适配完善 + 提审
Week 11+     Flutter App 开发
```

### 6.2 详细排期

#### ✅ 第一阶段 · 后端基础（已完成）

- [x] Python + FastAPI 项目搭建
- [x] MySQL + Redis 环境配置
- [x] Alembic 数据库迁移
- [x] 手机号登录（邮箱验证码）
- [x] JWT 单 Token 认证中间件
- [x] 配对码生成与确认
- [x] 纪念日 CRUD
- [x] 相册上传 + 查询
- [x] 愿望清单 CRUD

#### ✅ 第二阶段 · 互动功能（已完成）

- [x] 心情同步接口
- [x] 聊天消息接口
- [x] 足迹地图接口
- [x] 时光胶囊接口
- [x] 80+ 单元测试全部通过

#### ✅ 第三阶段 · 特色功能（已完成）

- [x] AI 恋爱月刊（对接 DeepSeek API）
- [x] 心愿基金（共同储蓄目标）
- [x] 恋爱账单（双向记账）
- [x] 恋爱罚单（趣味惩罚）
- [x] Docker 部署配置

#### 📱 第四阶段 · 前端开发（待启动）

- [ ] Uni-app 项目初始化，封装请求库
- [ ] 登录 / 注册页
- [ ] 配对流程页（生成码 + 输入码 + 配对成功）
- [ ] 首页（恋爱天数 + 纪念日倒计时）
- [ ] 共享相册（上传 + 时间线）
- [ ] 愿望清单
- [ ] 心情同步
- [ ] 聊天页面
- [ ] 时光胶囊 + 足迹地图
- [ ] AI 月刊展示
- [ ] 恋爱存折（基金 + 账单 + 罚单）
- [ ] 个人设置

#### 📋 第五阶段 · 小程序收尾

- [ ] 微信后台配置合法域名（必须备案 HTTPS）
- [ ] WebSocket 接入（聊天实时通信）
- [ ] 小程序订阅消息模板申请（纪念日提醒）
- [ ] 全流程测试 + Bug 修复
- [ ] 提交微信审核

#### 📲 第六阶段 · Flutter App

- [ ] Flutter 项目初始化，Riverpod 状态管理
- [ ] 复用全部后端 API，重写 UI 层
- [ ] FCM + APNs 推送通知接入
- [ ] 安卓 APK 打包，提交华为 / 应用宝
- [ ] iOS 证书申请 + App Store 提审

---

## 七、部署方案

### 7.1 服务器配置

```
CPU：    2 核
内存：   4G
系统盘： 50G
数据盘： 100G（专门存图片）
带宽：   5M
系统：   Ubuntu 22.04 LTS
费用：   腾讯云 / 阿里云学生机，约 200 元以内/年
```

内存占用参考：

```
MySQL      →  约 800MB
Redis      →  约 200MB
FastAPI    →  约 200MB
Nginx      →  约 50MB
系统本身   →  约 500MB
─────────────────────
合计       ≈  1.75G     剩余 2G+ 余量，充裕
```

### 7.2 目录结构

```
/app
├── backend/               # FastAPI 源码
├── uploads/               # 图片本地存储（初期）
└── nginx/
    └── nginx.conf
```

### 7.3 Nginx 配置

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

    # WebSocket（第二阶段）
    location /ws/ {
        proxy_pass http://127.0.0.1:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 本地图片访问
    location /uploads/ {
        alias /app/uploads/;
    }
}

# HTTP 重定向 HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}
```

### 7.4 启动命令

```bash
# 启动 FastAPI
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2

# systemd 配置路径（保持后台运行，重启自动恢复）
# /etc/systemd/system/click_app.service
```

---

## 八、已知风险与解决方案

| 风险点 | 严重程度 | 解决方案 |
|--------|----------|----------|
| 配对码并发竞争 | 🔴 高 | Redis `GETDEL` 原子操作 ✅ |
| 已配对用户再配对 | 🔴 高 | 生成码和确认码两端均校验 ✅ |
| 重复生成配对码 | 🟡 中 | `pair:user:{id}` 追踪当前码，生成前清除旧码 ✅ |
| 短信验证码被刷 | 🟡 中 | Redis 限频 60 秒 + 验证码 5 次失败锁定 ✅ |
| 相册权限泄露 | 🔴 高 | 查询图片时必须带 couple_id 校验 ✅ |
| 图片占满磁盘 | 🟡 中 | 上传时压缩 + 缩略图 + 10MB 大小限制 ✅ |
| 恶意文件上传 | 🔴 高 | 扩展名白名单 + Pillow 内容验证 ✅ |
| JWT 密钥泄露 | 🔴 高 | 启动时校验密钥强度，拒绝不安全默认值 ✅ |
| CORS 跨域滥用 | 🟡 中 | 环境变量配置允许的域名，不使用通配符 ✅ |
| Swagger 文档泄露 | 🟡 中 | `DEBUG_MODE` 控制，生产环境默认关闭 ✅ |
| 错误信息泄露内部细节 | 🟡 中 | 统一错误返回，敏感信息仅记录日志 ✅ |
| 验证码暴力破解 | 🟡 中 | 5 次失败后锁定，强制重新获取 ✅ |
| 微信小程序域名备案 | 🟡 中 | 域名提前备案，配置 HTTPS 白名单 |
| WebSocket 小程序兼容 | 🟡 中 | 指定 `transports: ['websocket']`，提前验证 |
| 小程序推送机制特殊 | 🟡 中 | 单独申请订阅消息模板，与 App 推送分开实现 |
| Flutter 与小程序代码分离 | 🟠 中 | 后端 API 全部复用，仅 UI 层分离，可控 |
| iOS 上架成本 | 🟢 低 | 提前申请 Apple 开发者账号（$99/年） |
| App 上架资质（未成年） | 🟡 中 | 软著著作权归本人，备案 + 商店账号由家长配合 |

---

## 附录

### A. 短信成本估算

| 阶段 | 预估月发送量 | 月费用 |
|------|------------|--------|
| 开发测试 | 固定码，不发真实短信 | 0 元 |
| 上线初期（< 100 对） | ~200 条 | ~6 元 |
| 成长期（~1000 对） | ~2000 条 | ~64 元 |

### B. 环境变量清单

```env
# 数据库
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/click_app

# Redis
REDIS_URL=redis://localhost:6379

# JWT（必须修改！生成命令：openssl rand -hex 32）
JWT_SECRET=your-secret-key
JWT_EXPIRE_DAYS=7

# CORS 允许的前端域名（逗号分隔，留空不允许跨域）
CORS_ORIGINS=https://yourdomain.com,http://localhost:5173

# 调试模式（生产环境设为 false）
DEBUG_MODE=false

# 开发模式（验证码固定为 123456，生产环境切勿开启）
DEV_MODE=false

# 阿里云短信
ALIYUN_ACCESS_KEY=your-key
ALIYUN_ACCESS_SECRET=your-secret
ALIYUN_SMS_SIGN=你的短信签名
ALIYUN_SMS_TEMPLATE=SMS_xxxxxxx

# 邮箱验证码（QQ 邮箱 SMTP）
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USER=your_email@qq.com
SMTP_PASSWORD=your_smtp_password
SMTP_FROM=your_email@qq.com

# 图片存储（初期本地，后期换 MinIO）
UPLOAD_DIR=/app/uploads
UPLOAD_BASE_URL=https://yourdomain.com/uploads

# DeepSeek API（AI 月刊）
DEEPSEEK_API_KEY=your-api-key

# MinIO（第二阶段启用）
# MINIO_ENDPOINT=localhost
# MINIO_PORT=9000
# MINIO_ACCESS_KEY=minioadmin
# MINIO_SECRET_KEY=minioadmin
# MINIO_BUCKET=couple-app

# FCM（第三阶段启用）
# FCM_SERVER_KEY=your-fcm-key
```

### C. APK 上架资质清单

```
必须准备：
├── 软件著作权（1~3个月，建议开发同期申请）
├── App 备案（工信部，约 20 个工作日）
├── 公安备案（约 10 个工作日）
├── 隐私政策页面
└── 测试账号（提供给审核员）

未成年开发者：
├── 软著著作权 → 可填本人（未成年人可持有著作权）
└── 备案 + 商店账号 → 由家长配合完成

优先上架：
├── 华为应用市场（覆盖最广）
└── 应用宝（腾讯，覆盖次之）
```

---

*文档版本：v1.3 · 最后更新：2026 年 5 月*
