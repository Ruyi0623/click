# 咔哒 (Click) 开发进度

## 本次更新 (2026-05-30)

### 安全审查修复
- [x] JWT_SECRET 启动校验，拒绝不安全的默认值
- [x] CORS 从环境变量读取，不再使用通配符 `*`
- [x] 生产环境关闭 Swagger 文档（`DEBUG_MODE` 控制）
- [x] 配对码生成改用 `secrets` 模块（密码学安全）
- [x] 验证码生成改用 `secrets` 模块
- [x] 验证码防暴力破解（5 次失败后锁定）
- [x] 不再向前端返回 `dev_code`
- [x] `DEV_MODE` 必须显式开启，不再自动判断
- [x] 文件上传安全：扩展名白名单、10MB 大小限制、Pillow 内容验证
- [x] 错误信息不暴露内部细节（magazine 模块）
- [x] Nginx 添加安全响应头（X-Content-Type-Options、X-Frame-Options 等）

### Docker 部署
- [x] 项目部署到腾讯云服务器（Docker Compose）
- [x] MySQL/Redis 不暴露主机端口（Docker 内部通信）
- [x] Nginx 映射到 8080/8443（避免与宝塔 Nginx 冲突）
- [x] 上传卷共享给 Nginx 容器（图片访问）
- [x] Alembic 支持读取 DATABASE_URL 环境变量
- [x] Dockerfile 使用清华镜像源加速构建

---

## 上次更新 (2026-05-29)

### 环境搭建
- [x] 安装 Python 3.12 虚拟环境
- [x] 使用清华镜像源加速安装依赖
- [x] 安装并配置 MySQL 8，创建 `click_app` 数据库
- [x] 安装并启动 Redis 服务
- [x] 运行 Alembic 数据库迁移，创建 15 张表

### 代码修复
- [x] 修复 schema 文件中的类型注解语法（`date | None` → `Optional[date]`）
- [x] 修复 routers 文件中的类型注解语法
- [x] 解决变量名与类型名冲突问题（`date` 字段 vs `date` 类型）

### 项目重命名
- [x] 项目名从「情侣日常」改为「咔哒 (Click)」
- [x] 数据库名从 `coupleapp` 改为 `click_app`
- [x] 更新 API 文档、计划书、配置文件中的名称

### 服务状态
- [x] FastAPI 服务器运行在 http://localhost:8000
- [x] API 文档：http://localhost:8000/docs
- [x] 健康检查：http://localhost:8000/api/health
- [x] 单元测试：80 个测试全部通过

---

## 已完成功能

### 核心功能
- [x] 用户认证（手机号 + 验证码登录）
- [x] 情侣配对（配对码机制）
- [x] 纪念日管理
- [x] 愿望清单
- [x] 共享相册

### 社交功能
- [x] 心情同步模块 (`/moods`)
- [x] 聊天消息模块 (`/messages`)
- [x] 足迹地图模块 (`/footprints`)

### 特色功能
- [x] AI 恋爱月刊（对接 DeepSeek API）
- [x] 恋爱存折 & 小确幸共同基金
  - 心愿储蓄池
  - 双向记账法
  - 恋爱罚单

---

## 待完成

### 优先级中
- [x] 接入邮箱验证码（QQ 邮箱 SMTP）
- [x] 实现时光胶囊模块 (`/capsules`)

### 优先级低
- [x] 部署到云服务器（Docker 部署完成）
- [ ] 前端开发

### 技术债务
- [ ] 添加 API 请求参数验证测试
- [x] 完善错误处理和日志记录（安全审查已改进）
- [ ] 添加数据库索引优化查询性能
