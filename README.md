# Click · 咔哒

一个面向情侣的私密空间微信小程序全栈项目，用于共同记录日常、照片、纪念日、心情、心愿、足迹、时光胶囊、账单、基金与 AI 恋爱月刊。

## 技术栈

- **前端：** uni-app、Vue 3、TypeScript、Pinia、Sass
- **后端：** FastAPI、SQLAlchemy、Alembic、MySQL、Redis
- **部署：** Docker Compose、Nginx

## 主要功能

- 手机号/邮箱验证码、账号密码与微信登录
- 情侣绑定及共享资料管理
- 纪念日、心愿、每日心情、聊天消息与时光胶囊
- 相册、照片合集、批量移动与批量删除
- 地图足迹、情侣日记、点赞和评论
- 共同基金、账单统计、月度预算与恋爱罚单
- 基于 DeepSeek 的 AI 恋爱月刊

## 本地开发

### 后端

```bash
cd backend
python -m venv venv
venv\Scripts\pip install -r requirements.txt
# 从 .env.example 创建本地 .env 并填写配置
alembic upgrade head
venv\Scripts\uvicorn main:app --reload
```

### 前端

```bash
cd frontend/miniapp
npm ci
npm run dev:mp-weixin
```

## 部署

Docker Compose 需要在项目根目录创建 `.env`，并配置数据库、Redis、JWT 等变量：

```bash
docker compose up -d --build
docker compose exec app alembic upgrade head
```

请勿提交任何 `.env` 文件、数据库文件、构建产物或服务器凭据。详细接口和部署资料请参阅 [docs](./docs)。
