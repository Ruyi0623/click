# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

"咔哒" (Kada) — 情侣私密空间 App，记录情侣日常（纪念日、照片、心愿、心情、时间胶囊、足迹地图、AI 杂志、情侣基金、情侣日记）。前后端均已实现。

## Tech Stack

- **Backend:** Python 3.12 + FastAPI + SQLAlchemy 2.0 + Alembic + Redis + MySQL 8
- **Frontend:** Uni-app 3.0 + Vue 3.4 + TypeScript + Pinia 3.0 + SCSS，目标平台微信小程序
- **AI:** DeepSeek API（OpenAI 兼容）用于杂志生成
- **Deploy:** Docker Compose（mysql, redis, app, nginx 四容器）

## Commands

### 远程服务器执行

远程连接信息不得写入仓库。将主机、用户和认证信息保存在本机环境变量或安全的机密管理工具中，再通过项目根目录的 `deploy.sh` 同步代码并执行远程命令：

```bash
# 仅同步文件
./deploy.sh

# 同步后执行命令
./deploy.sh "docker compose ps"
./deploy.sh "docker compose exec app alembic upgrade head"
```

### 本地开发（可选）

```bash
# 后端本地开发
cd backend && source venv/bin/activate
uvicorn main:app --reload                    # localhost:8000

# 测试（SQLite 内存库，需本地 Redis 运行中）
pytest                                       # 全部测试
pytest tests/test_auth.py                    # 单个文件
pytest -k "test_login"                       # 按名称匹配

# 数据库迁移（读取 DATABASE_URL 环境变量，覆盖 alembic.ini 默认值）
alembic upgrade head                         # 执行迁移
alembic revision --autogenerate -m "描述"    # 生成新迁移
```

### 前端开发

```bash
cd frontend/miniapp
npm run dev:mp-weixin                        # 微信小程序开发模式
npm run build:mp-weixin                      # 编译到 dist/build/mp-weixin/
npm run type-check                           # TypeScript 类型检查
```

### Docker 部署（远程服务器）

```bash
# 启动服务
docker-compose up -d

# 重建并重启
docker-compose build && docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看容器状态
docker-compose ps

# 重启服务
docker-compose restart

# 停止服务
docker-compose down
```

## Architecture

### 后端三层结构

所有业务模块遵循 routers → schemas → models 三层分离，services/ 放跨模块业务逻辑：

```
routers/       → 路由层：URL 映射 + 请求处理，调用 models 层直接操作 DB
schemas/       → Pydantic 模型：请求体/响应体校验
models/        → SQLAlchemy ORM：数据库表映射，UUID 主键
services/      → 独立服务：sms.py（验证码）、storage.py（文件上传+缩略图）、magazine.py（AI 生成）、wechat.py（微信 jscode2session）
utils/         → 工具函数：password.py（bcrypt 哈希/验证）
```

### 认证与数据隔离

- 所有业务接口通过 `Depends(get_current_user)` 注入当前用户（JWT Bearer，HS256，7天有效期）
- 所有业务接口通过 `get_couple()` 校验情侣关系，未配对用户返回 400
- 新增业务路由必须同时使用这两个依赖，确保数据隔离

### 登录方式

支持三种登录方式（`routers/auth.py`）：
- **微信登录** — `/wx-login`：小程序 wx.login 获取 code，后端调用微信 jscode2session 换取 openid
- **账号密码** — `/login-password`：用户名 + bcrypt 密码哈希
- **手机验证码** — `/login`：短信验证码（DEV_MODE 下固定 123456）

User 模型关键字段：`wx_openid`、`username`、`password_hash`、`email`、`birthday`

### 路由注册模式

每个 router 模块导出一个 `APIRouter` 实例（带 prefix），在 `main.py` 中统一注册到 `/api` 下。当前 15 个路由：auth, couple, anniversary, photo, wish, mood, message, magazine, fund, transaction, penalty, footprint, capsule, collection, diary。

### 数据库模型关系

核心模型使用 UUID 主键，通过 `couple_id` 实现数据隔离：
- `Couple` — 情侣关系，关联 user1/user2
- `Diary` — 日记，含 `DiaryPhoto`（照片）、`DiaryLike`（点赞）、`DiaryComment`（评论）
- `Photo` — 相册照片，按 `couple_id` 分目录存储，`Collection` 为合集
- `Magazine` — AI 月刊，含 `status` 字段（success/failed），每月自动生成上月月刊
- `MonthlyBudget` — 按月预算，`couple_id` + `month` 唯一约束

### 定时任务

月刊自动生成：服务器 cron 每月1日北京时间 10:00/14:00/20:00 触发 `POST /api/magazines/auto-generate`（10:00 首次，14:00/20:00 重试失败的）。配置文件：`/etc/cron.d/magazine-auto-generate`。

### 文件存储

上传文件按 `couple_id` 分目录存放，自动生成缩略图。Nginx 通过 `/uploads/` 路径提供静态文件服务（30天缓存）。

### Nginx 架构

双层 Nginx：宝塔 Nginx（宿主机，处理 SSL）→ Docker Nginx（容器，反向代理到 FastAPI）。`X-Forwarded-Proto` 使用 `$http_x_forwarded_proto` 透传，确保 FastAPI 的重定向生成正确的 HTTPS URL。FastAPI 设置 `redirect_slashes=False` 避免 307 重定向问题。

### 前端架构

```
frontend/miniapp/src/
├── pages/          → 26 个页面（3 个 Tab 页 + 23 个子页面）
├── components/     → 12 个 Kd* 组件（ActionSheet, Button, Calendar, Card, Countdown, CoupleHeader, Dialog, Empty, Icon, Markdown, MoodPicker, PhotoGrid）
├── api/            → 14 个 API 模块，每个对应一个后端路由，封装 uni.request
├── stores/         → 2 个 Pinia store（auth: token/用户信息，couple: 情侣信息/天数）
├── utils/          → request.ts（HTTP 客户端+JWT+401 处理）、date.ts、markdown.ts
├── styles/         → variables.scss（设计系统）、mixins.scss、animations.scss
├── static/         → SVG 图标集（icons/, icons-pink/, icons-white/）+ tabbar PNG
├── pages.json      → 路由配置 + tabBar 定义（3 tab: 首页/相册/我的）
└── App.vue         → 全局入口：登录校验 + 情侣状态路由
```

前端设计系统（`styles/variables.scss`）：粉色主色调、8px 间距网格、圆角体系、粉色投影、12 个动画类。日记模块使用独立的胶片暖色系（`#C9875D` 焦糖棕、`#F8F3ED` 奶油纸背景）。

页面路径与后端路由一一对应，`api/` 模块的 TypeScript 接口与后端 `schemas/` 对齐。

### 测试体系

- `conftest.py` 提供：SQLite 内存库替代 MySQL、Redis flush 隔离、TestClient、`auth_headers` fixture
- `DEV_MODE=true` 时验证码固定为 `123456`，测试环境自动启用
- 每个业务模块对应一个 `test_*.py` 文件

## Environment Variables

- Docker 部署：根目录 `.env`（从 `.env.example` 复制）
- 本地开发：`backend/.env`（从 `backend/.env.example` 复制）

关键变量：`DATABASE_URL`、`REDIS_URL`、`JWT_SECRET`、`CORS_ORIGINS`、`DEV_MODE`、`DEBUG_MODE`、`DEEPSEEK_API_KEY`、`UPLOAD_DIR`、`WECHAT_APPID`、`WECHAT_SECRET`

`DEBUG_MODE=true` 暴露 Swagger 文档 `/docs`。`DEV_MODE=true` 启用固定验证码。

## Key Files

- `backend/main.py` — 应用入口，注册路由 + CORS + 静态文件挂载
- `backend/auth.py` — JWT 认证核心（token 创建/解析/get_current_user 依赖）
- `backend/database.py` — SQLAlchemy engine + Redis client + get_db/get_redis 依赖
- `backend/tests/conftest.py` — 测试基础设施（fixtures）
- `./deploy.sh` — 远程部署脚本（rsync 文件同步 + 远程命令执行），位于项目根目录
- `frontend/miniapp/src/utils/request.ts` — 前端 HTTP 客户端（JWT 注入、401 拦截、文件上传）
- `frontend/miniapp/src/styles/variables.scss` — 前端设计系统（颜色、间距、圆角、阴影、动画）
- `frontend/miniapp/src/pages.json` — 页面路由 + tabBar 配置
- `docs/API文档.md` — 完整 REST API 接口文档
- `docs/DEPLOY.md` — 部署指南

## AI 模型使用注意

- **图像识别任务**：使用 `mimov2.5`（非 pro 版本），因为 2.5pro 没有多模态能力

## 业务规则

### 恋爱月刊
- 每月1日自动生成上月月刊（cron 定时任务）
- 成功生成后不可重新生成，不可删除
- 失败可手动重试，最多3次，3次全失败则锁定
- 生成数据包含：心情、日记、纪念日、愿望、账单、罚单、基金、足迹、时光胶囊

### 情侣日记
- 朋友圈风格 feed 流，支持照片（最多9张）、点赞、评论
- 删除日记时同步清理：diary_photos + photos 记录 + 磁盘文件 + 点赞 + 评论

### 账单
- 按 `happened_at`（消费日期）筛选，兜底 `created_at`
- 每月独立预算（`MonthlyBudget` 表），无月度预算时显示「未设置」

### 解除配对
- 删除所有共享数据（照片文件、日记、月刊、账单等）
- 删除用户账号（含头像文件）
- 清除本地登录状态

## 远程部署规范

本项目通过 SSH 连接远程服务器进行文件同步和命令执行，必须严格遵守以下规则：

1. **禁止使用 `cat 文件 | ssh ... 'cat > 文件'` 这种管道方式传输文件**，无论文件大小或数量。
2. **禁止手写零散的 scp 命令**逐个传文件。
3. 所有文件同步必须通过 rsync 完成，统一使用项目根目录下的 `./deploy.sh` 脚本。
4. 所有远程命令执行（重启服务、跑构建、跑测试等）也必须通过 `./deploy.sh "命令"` 完成，不要直接 ssh 进去执行零散命令。
5. 如果 `./deploy.sh` 不存在，先创建该脚本（基于 rsync + SSH ControlMaster 连接复用），再使用它，不要绕过去用其他临时方案。
6. 如果同步或执行命令时遇到工具不存在（如服务器没装 rsync）等问题，先告知用户并询问如何处理，不要自行退化为 cat/scp 等方式。
