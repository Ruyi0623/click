# Click · 咔哒

Click（咔哒）是一个面向情侣的私密空间微信小程序全栈项目。它将共同生活中的照片、日记、心情、纪念日、愿望、足迹和财务记录集中在一个轻量的共享空间中，帮助两个人持续沉淀属于自己的关系档案。

项目采用前后端分离架构：前端使用 uni-app 构建微信小程序，也支持 H5 等跨端目标；后端使用 FastAPI 提供 REST API，并通过 MySQL、Redis、Docker Compose 和 Nginx 完成数据存储、缓存、文件服务与部署。

## 功能概览

### 账户与情侣关系

- 支持微信登录、账号密码登录和手机/邮箱验证码登录。
- 支持用户昵称、头像、性别、生日等资料维护。
- 通过情侣绑定码建立共享空间。
- 所有共享业务数据以情侣关系为边界进行隔离。
- 支持解除配对，并按业务规则清理共享数据和本地登录状态。

### 首页与共同记录

- 首页展示情侣信息、相识天数和近期动态。
- 记录每日心情，并保留心情内容和历史变化。
- 创建、编辑和查看纪念日及倒计时。
- 管理共同愿望，跟踪愿望状态。
- 通过时光胶囊保存延迟开启的文字、照片和私密内容。
- 使用地图足迹记录共同去过的地点。

### 相册与情侣日记

- 上传情侣共同照片，并按情侣空间分别存储。
- 创建照片合集，设置合集名称和封面。
- 支持照片在未分组区域与不同合集之间移动。
- 支持全选、批量移动和批量删除照片。
- 情侣日记支持文字、最多 9 张照片、点赞和评论。
- 删除日记时同步处理关联照片、点赞、评论及服务器文件。
- 图片上传后可生成缩略图，并通过 Nginx 提供静态访问。

### 账单、基金与罚单

- 记录共同消费、消费日期、分类、金额和自定义分摊方式。
- 按消费日期查询账单，并兼容历史数据的创建日期。
- 按月份设置共同预算并查看支出统计。
- 管理情侣共同基金，支持充值、提现和流水明细。
- 创建恋爱罚单，记录金额、照片和备注。
- 查看账单、基金和罚单的汇总信息，辅助情侣进行共同财务管理。

### 恋爱月刊

- 按月汇总心情、日记、纪念日、愿望、账单、罚单、基金、足迹和时光胶囊等数据。
- 通过 DeepSeek 生成个性化的月度回顾内容。
- 月刊具有生成状态、失败重试次数和失败锁定规则。
- 支持定时任务自动生成上月月刊，也支持对失败任务进行重试。

## 技术栈

### 前端

- Vue 3
- TypeScript
- uni-app 3
- Vite
- Pinia
- Sass / SCSS
- uview-plus
- Iconify

### 后端

- Python 3.12
- FastAPI
- Uvicorn
- SQLAlchemy 2
- Pydantic
- Alembic
- MySQL 8
- Redis 7
- JWT（HS256）
- Pillow
- HTTPX
- OpenAI SDK（用于调用兼容接口）

### 部署

- Docker Compose
- Nginx
- 容器化 FastAPI 应用
- MySQL 数据库
- Redis 缓存与验证码存储

## 项目结构

```text
.
├── backend/
│   ├── main.py                 # FastAPI 应用入口、路由注册和静态文件挂载
│   ├── auth.py                 # JWT 创建、解析和当前用户依赖
│   ├── database.py             # SQLAlchemy、MySQL/SQLite 和 Redis 连接
│   ├── models/                 # SQLAlchemy 数据模型
│   ├── schemas/                # Pydantic 请求与响应模型
│   ├── routers/                # 按业务模块拆分的 API 路由
│   ├── services/               # 验证码、文件、微信和月刊服务
│   ├── utils/                  # 密码等通用工具
│   ├── alembic/                # 数据库迁移脚本
│   └── tests/                  # 后端接口测试
├── frontend/
│   ├── miniapp/
│   │   ├── src/api/            # 前端 API 封装
│   │   ├── src/components/     # Kd 前缀公共组件
│   │   ├── src/pages/          # 页面和业务流程
│   │   ├── src/stores/         # Pinia 状态管理
│   │   ├── src/styles/         # 设计变量、混入和动画
│   │   ├── src/static/         # 图标和静态资源
│   │   ├── src/App.vue         # 应用启动、登录态和配对态处理
│   │   └── src/pages.json      # 页面路由和 TabBar 配置
│   └── *.md                    # 前端设计和规划资料
├── docs/                       # API、部署和安全文档
├── nginx/                      # Nginx 配置
├── docker-compose.yml          # 本地/生产服务编排
├── .env.example                # 根目录环境变量模板
└── LICENSE
```

## 后端模块

后端路由按照业务领域拆分，公共 API 前缀为 `/api`：

| 模块 | 说明 |
| --- | --- |
| `auth` | 注册、登录、验证码、微信登录和用户资料 |
| `couple` | 情侣绑定、配对信息和解除配对 |
| `anniversary` | 纪念日和倒计时 |
| `photo` | 图片上传、查询、删除和批量操作 |
| `collection` | 相册合集和照片移动 |
| `diary` | 情侣日记、照片、点赞和评论 |
| `mood` | 每日心情记录 |
| `wish` | 共同愿望 |
| `message` | 情侣消息 |
| `capsule` | 时光胶囊 |
| `footprint` | 地图足迹 |
| `fund` | 共同基金和资金贡献 |
| `transaction` | 账单、分摊和月度预算 |
| `penalty` | 恋爱罚单 |
| `magazine` | 月刊生成、查询和重试 |

业务接口通常通过 JWT 获取当前用户，再通过情侣关系校验数据访问范围。模型使用 UUID 作为主键，并通过 `couple_id` 关联情侣共享空间。

## 环境配置

不要提交真实环境文件。开发时分别复制对应模板：

```bash
# 后端本地配置
cp backend/.env.example backend/.env

# Docker Compose 配置
cp .env.example .env
```

常用配置项包括：

- `DATABASE_URL`：MySQL 或测试数据库连接地址。
- `REDIS_URL`：Redis 连接地址。
- `JWT_SECRET`：长度足够且随机的 JWT 密钥。
- `JWT_EXPIRE_DAYS`：登录令牌有效期。
- `CORS_ORIGINS`：允许访问 API 的前端来源。
- `UPLOAD_DIR`：上传文件保存目录。
- `UPLOAD_BASE_URL`：上传文件对外访问地址。
- `WECHAT_APPID`、`WECHAT_SECRET`：微信小程序配置。
- `DEEPSEEK_API_KEY`：月刊生成服务的接口密钥。
- `SMTP_*`：邮箱验证码服务配置。
- `DEV_MODE`：本地开发和测试模式开关。
- `DEBUG_MODE`：是否暴露 API 文档。

生产环境必须使用独立密钥，并通过服务器环境变量或机密管理系统注入，不要将服务器地址、登录凭据、数据库密码或第三方密钥写入代码库。

## 本地运行

### 启动后端

后端依赖 MySQL 和 Redis。准备好服务并配置 `backend/.env` 后执行：

```bash
cd backend
python -m venv venv

# Windows
venv\\Scripts\\pip install -r requirements.txt
venv\\Scripts\\alembic upgrade head
venv\\Scripts\\uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Linux/macOS
# source venv/bin/activate
# pip install -r requirements.txt
# alembic upgrade head
# uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

健康检查接口：

```text
GET http://localhost:8000/api/health
```

当 `DEBUG_MODE=true` 时，可访问 FastAPI 文档：

```text
http://localhost:8000/docs
```

### 启动前端

```bash
cd frontend/miniapp
npm ci

# H5 开发
npm run dev:h5

# 微信小程序开发
npm run dev:mp-weixin
```

微信小程序开发需要使用微信开发者工具打开对应的编译目录。前端 API 地址位于 `src/utils/request.ts`，本地联调时应根据环境改为可访问的后端地址，并正确配置后端跨域来源。

## 数据库迁移

迁移文件位于 `backend/alembic/versions/`。首次启动或部署新版本时执行：

```bash
cd backend
alembic upgrade head
```

创建新的迁移文件：

```bash
alembic revision --autogenerate -m "describe the schema change"
```

执行迁移前请备份生产数据库，并检查自动生成的迁移内容，尤其是字段删除、数据转换和索引变更。

## 测试

后端测试使用 pytest，并通过测试夹具隔离数据库和 Redis。测试文件位于 `backend/tests/`，覆盖认证、情侣关系、纪念日、心情、愿望、消息、胶囊、足迹、基金、账单、罚单和月刊等模块。

```bash
cd backend
pytest

# 运行单个模块
pytest tests/test_auth.py

# 按测试名称筛选
pytest -k "login"
```

测试环境会使用独立的 SQLite 测试库，并清理测试 Redis 数据。不要在包含重要业务数据的生产 Redis 或数据库环境中直接运行测试。

## Docker 部署

准备 Docker、Docker Compose 和生产环境变量后，在项目根目录执行：

```bash
cp .env.example .env
# 编辑 .env，填写生产配置

docker compose up -d --build
docker compose exec app alembic upgrade head
docker compose ps
docker compose logs -f app
```

Compose 默认包含以下服务：

- `mysql`：持久化业务数据。
- `redis`：缓存、验证码和临时状态。
- `app`：FastAPI 应用。
- `nginx`：反向代理和上传文件静态服务。

生产部署时应确认 HTTPS 终止位置、`X-Forwarded-Proto` 转发、上传目录权限、数据库备份、Redis 持久化和容器健康状态。部署脚本中的远程连接参数应通过环境变量提供，不能写入版本库。

## 文件与数据安全

- `.env`、数据库文件、缓存目录、Python 字节码和前端构建目录均属于本地或部署产物，不应提交。
- 用户上传文件按情侣空间划分目录保存，删除记录时应同步清理磁盘文件。
- 所有共享资源接口都必须校验当前用户和情侣关系，避免跨情侣空间访问。
- 生产环境应启用 HTTPS，并限制 CORS 来源。
- JWT 密钥、微信密钥、邮件密码和月刊服务密钥应定期轮换。
- 上传接口应限制文件类型、文件大小和图片处理资源消耗。

## 相关文档

- [API 接口文档](./docs/API文档.md)
- [部署指南](./docs/DEPLOY.md)
- [安全检查记录](./docs/API安全防护分析.md)
- [前端开发说明](./frontend/mini-program-plan.md)

## 许可证

本项目遵循仓库中的 [LICENSE](./LICENSE) 文件。