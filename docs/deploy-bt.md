# 咔哒 (Click) 宝塔面板部署指南

> 适用于已有云服务器（已安装宝塔面板）的用户，通过 Docker Compose 部署
> 
> **架构**：宝塔 Nginx（80/443，处理 HTTPS）→ Docker Nginx（8080）→ FastAPI（8000）

---

## 一、安装宝塔面板

### 1.1 SSH 连接服务器

```bash
ssh root@你的服务器IP
```

### 1.2 安装宝塔（Ubuntu）

```bash
wget -O install.sh https://download.bt.cn/install/install_lts.sh && sudo bash install.sh ed8484bec
```

> 安装完成后会输出：
> - **外网面板地址**：`http://你的IP:8888/随机安全入口`
> - **username**：管理员账号
> - **password**：管理员密码
>
> ⚠️ **请务必保存好这些信息**，首次登录需要绑定宝塔账号

### 1.3 安装宝塔（CentOS）

```bash
wget -O install.sh https://download.bt.cn/install/install_lts.sh && sh install.sh ed8484bec
```

### 1.4 首次登录

1. 浏览器打开外网面板地址
2. 绑定宝塔账号（手机号注册即可）
3. 进入面板后**不要安装推荐的 LNMP 套件**（我们用 Docker）

---

## 二、安装 Docker

### 2.1 通过宝塔安装

1. 左侧菜单 → **Docker** → 如果提示未安装，点击 **立即安装**
2. 等待安装完成（约 2-3 分钟）

### 2.2 或手动安装（推荐）

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | bash -s docker

# 启动 Docker 并设置开机自启
systemctl start docker
systemctl enable docker

# 安装 Docker Compose（宝塔自带的可能版本较旧）
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 验证
docker --version
docker-compose --version
```

### 2.3 免 sudo 配置（可选）

```bash
sudo usermod -aG docker ubuntu   # 替换为你的用户名
# 重新登录 SSH 生效
```

---

## 三、上传项目

> ⚠️ 上传时**排除 `backend/venv/` 目录**，它是本地虚拟环境，服务器不需要且会导致上传失败

### 3.1 方式一：Git Clone（推荐）

```bash
cd /www/wwwroot/
git clone https://github.com/你的用户名/qlkj.git
```

### 3.2 方式二：宝塔面板上传

1. 左侧菜单 → **文件**
2. 进入 `/www/wwwroot/` 目录
3. 点击 **上传** → 选择本地的 `qlkj` 文件夹
4. 上传前删除或跳过 `backend/venv/` 目录

### 3.3 方式三：SCP 传输（排除 venv）

```bash
# 在本地终端执行（打包时排除 venv）
cd /mnt/d/项目
tar --exclude='qlkj/backend/venv' \
    --exclude='qlkj/backend/__pycache__' \
    --exclude='qlkj/backend/.pytest_cache' \
    --exclude='qlkj/backend/test.db' \
    -czf qlkj.tar.gz qlkj/

# 上传并解压
scp qlkj.tar.gz root@你的服务器IP:/www/wwwroot/
ssh root@你的服务器IP "cd /www/wwwroot && tar -xzf qlkj.tar.gz"
```

---

## 四、配置环境变量

### 4.1 生成 JWT 密钥

```bash
cd /www/wwwroot/qlkj
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
# 输出类似：aBcDeFgHiJkLmNoPqRsTuVwXyZ0123456789...（复制备用）
```

### 4.2 创建生产环境 .env

```bash
cat > .env << 'EOF'
# MySQL（Docker 内部通信，密码自定义）
MYSQL_ROOT_PASSWORD=替换为你的强密码

# JWT（必填！应用无法启动如果没有此配置）
JWT_SECRET=替换为上面生成的密钥
JWT_EXPIRE_DAYS=7

# 上传文件访问地址（有域名填域名，没域名填 IP+端口）
UPLOAD_BASE_URL=http://你的服务器IP:8080/uploads

# CORS 允许的前端域名（逗号分隔，必填！否则前端无法调用 API）
CORS_ORIGINS=https://你的域名

# 调试模式（生产环境保持 false，开启后可访问 /docs Swagger 文档）
DEBUG_MODE=false

# 开发模式（验证码固定为 123456，生产环境切勿开启）
DEV_MODE=false

# 邮箱验证码（QQ 邮箱 SMTP）
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USER=你的QQ邮箱@qq.com
SMTP_PASSWORD=你的QQ邮箱授权码
SMTP_FROM=你的QQ邮箱@qq.com

# DeepSeek API（AI 月刊）
DEEPSEEK_API_KEY=你的DeepSeek密钥
EOF
```

> **注意**：
> - 如果配置了宝塔 Nginx 反代（见第七章），`UPLOAD_BASE_URL` 应改为：
>   ```
>   UPLOAD_BASE_URL=https://你的域名/uploads
>   ```
> - `CORS_ORIGINS` 多个域名用逗号分隔，如：`https://your-app.com,http://localhost:5173`
> - `JWT_SECRET` 如果留空或使用默认值，应用将**拒绝启动**

---

## 五、一键部署

### 5.1 端口说明

| 服务 | 容器端口 | 主机映射 | 说明 |
|------|----------|----------|------|
| MySQL | 3306 | 不映射 | Docker 内部通信，避免与服务器已有 MySQL 冲突 |
| Redis | 6379 | 不映射 | Docker 内部通信 |
| FastAPI | 8000 | 不映射 | 由 Docker Nginx 代理 |
| Nginx | 80/443 | **8080/8443** | 避免与宝塔 Nginx 冲突 |

### 5.2 构建并启动

```bash
cd /www/wwwroot/qlkj
docker-compose up -d --build
```

> 首次构建约 3-5 分钟，取决于服务器带宽。如果慢，检查 Dockerfile 是否已配置国内镜像源。

### 5.3 执行数据库迁移

```bash
# 进入 app 容器
sudo docker exec -it click_app bash

# 执行迁移
alembic upgrade head

# 退出容器
exit
```

### 5.4 验证服务状态

```bash
# 查看所有容器（应该都是 Up 状态）
sudo docker-compose ps

# 测试 API 健康检查（注意用 8080 端口）
curl http://localhost:8080/api/health

# 测试根端点（不应包含 docs 字段，因为生产环境 DEBUG_MODE=false）
curl http://localhost:8080/

# /docs 应返回 404（生产环境已关闭）
curl -o /dev/null -s -w "%{http_code}" http://localhost:8080/docs

# 查看实时日志
sudo docker-compose logs -f app
```

> **注意**：生产环境默认关闭 `/docs` Swagger 文档，这是安全加固的一部分。
> 如需临时调试，可在 `.env` 中设置 `DEBUG_MODE=true` 后重启：`sudo docker-compose restart app`

正常输出：

```
NAME          STATUS
click_mysql   Up
click_redis   Up
click_app     Up
click_nginx   Up
```

---

## 六、安全组配置

### 6.1 云服务商安全组

在腾讯云/阿里云控制台放行以下端口：

| 端口 | 协议 | 用途 |
|------|------|------|
| 22 | TCP | SSH |
| 80 | TCP | HTTP（宝塔 Nginx） |
| 443 | TCP | HTTPS（宝塔 Nginx） |
| 8080 | TCP | Docker Nginx HTTP |
| 8888 | TCP | 宝塔面板 |

### 6.2 宝塔防火墙

1. 左侧菜单 → **安全**
2. 放行端口：`80`、`443`、`8080`、`8888`

### 6.3 浏览器访问

```
http://你的服务器IP:8080/api/health
```

返回 `{"status":"ok"}` 即部署成功 ✅

> 生产环境默认关闭 `/docs` Swagger 文档（安全加固）。
> 如需临时开启，在 `.env` 中设置 `DEBUG_MODE=true` 后重启容器。

---

## 七、配置域名 + HTTPS（推荐）

> 微信小程序**强制要求 HTTPS**，上线前必须配置

### 7.1 域名解析

在域名服务商后台添加 A 记录：

| 主机记录 | 类型 | 记录值 |
|----------|------|--------|
| @ | A | 你的服务器 IP |
| www | A | 你的服务器 IP |

### 7.2 宝塔添加站点

1. 左侧菜单 → **网站** → **添加站点**
2. 填入域名，PHP 版本选「纯静态」
3. 点击 **提交**

### 7.3 配置反向代理

1. 点击刚创建的站点名称
2. 点击 **反向代理** → **添加反向代理**

| 配置项 | 值 |
|--------|-----|
| 代理名称 | click_app |
| 目标 URL | `http://127.0.0.1:8080` |
| 发送域名 | `$host` |

3. 点击 **提交**

### 7.4 申请 SSL 证书

1. 点击站点名称 → **SSL** → **Let's Encrypt**
2. 勾选域名，点击 **申请**
3. 申请成功后开启 **强制 HTTPS**

### 7.5 访问验证

```
https://你的域名/api/health
```

返回 `{"status":"ok"}` 即配置成功 ✅

访问流程：

```
用户 → HTTPS 443 → 宝塔 Nginx（SSL 证书）→ 转发到 8080 → Docker Nginx → FastAPI
```

---

## 八、常用运维命令

### 8.1 服务管理

```bash
# 启动所有服务
sudo docker-compose up -d

# 停止所有服务
sudo docker-compose down

# 重启所有服务
sudo docker-compose restart

# 重启单个服务
sudo docker-compose restart app

# 查看实时日志
sudo docker-compose logs -f app

# 查看最近 100 行日志
sudo docker-compose logs --tail 100 app
```

### 8.2 数据库操作

```bash
# 进入 MySQL 命令行
sudo docker exec -it click_mysql mysql -uroot -p click_app

# 备份数据库
sudo docker exec click_mysql mysqldump -uroot -p click_app > backup_$(date +%Y%m%d).sql

# 恢复数据库
sudo docker exec -i click_mysql mysql -uroot -p click_app < backup.sql
```

### 8.3 更新代码

```bash
cd /www/wwwroot/qlkj

# 拉取最新代码（如果是 git 管理）
git pull

# 检查 .env 是否需要新增配置项（参考 .env.example）
# 2025-05 安全更新新增：JWT_SECRET（必填）、CORS_ORIGINS、DEBUG_MODE

# 重新构建并重启
sudo docker-compose up -d --build

# 如果数据库有变更
sudo docker exec -it click_app alembic upgrade head
```

### 8.4 查看资源占用

```bash
# 查看容器资源使用
sudo docker stats

# 查看磁盘使用
df -h

# 清理无用的 Docker 镜像
sudo docker system prune -a
```

---

## 九、定时备份（推荐）

### 9.1 创建备份脚本

```bash
cat > /www/wwwroot/qlkj/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/www/backup/click_app"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# 备份数据库（替换 YOUR_PASSWORD 为实际密码）
docker exec click_mysql mysqldump -uroot -pYOUR_PASSWORD click_app > $BACKUP_DIR/db_$DATE.sql

# 备份上传的图片
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /www/wwwroot/qlkj/backend/uploads/

# 只保留最近 7 天的备份
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "备份完成: $DATE"
EOF

chmod +x /www/wwwroot/qlkj/backup.sh
```

### 9.2 设置定时任务

**方式一：宝塔面板**

1. 左侧菜单 → **计划任务**
2. 类型选 **Shell 脚本**
3. 执行周期选 **每天**，时间选凌晨 3 点
4. 脚本内容填：`/www/wwwroot/qlkj/backup.sh`

**方式二：crontab**

```bash
crontab -e
# 添加以下行（每天凌晨 3 点执行）
0 3 * * * /www/wwwroot/qlkj/backup.sh >> /var/log/click_backup.log 2>&1
```

---

## 十、常见问题

### Q1：docker-compose up 报错 `port is already bound`

MySQL/Redis 已配置为 Docker 内部通信，不映射到主机。如果 Nginx 端口冲突：

```bash
# 检查端口占用
lsof -i :8080

# docker-compose.yml 中已映射为 8080/8443，确保这两个端口没被占用
```

### Q2：MySQL 容器启动失败

```bash
# 查看详细错误
sudo docker-compose logs mysql

# 常见原因：数据卷冲突，可以删除重建（会丢失数据！）
sudo docker-compose down -v
sudo docker-compose up -d --build
```

### Q3：app 容器连接数据库失败

```bash
# 确认 MySQL 已启动
sudo docker-compose ps

# 进入 app 容器测试连接
sudo docker exec -it click_app bash
python -c "from database import engine; print(engine.connect())"
```

### Q4：alembic 报错 Connection refused

容器内应使用 Docker 服务名 `mysql` 而非 `localhost`。确保 `alembic/env.py` 已配置读取环境变量：

```python
import os
database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)
```

### Q5：上传图片后无法访问

```bash
# 检查 uploads 目录权限
sudo docker exec -it click_app ls -la /app/uploads/

# 确保 nginx 能读取
sudo docker exec -it click_nginx ls /var/www/uploads/
```

### Q6：宝塔面板打不开

```bash
# 重启宝塔面板
bt restart

# 查看面板信息（含入口地址）
bt default
```

### Q7：Windows 上传 venv 目录报错

`venv` 包含符号链接，Windows 无法处理。上传时排除该目录，或用 Git Clone 方式部署。

---

## 部署检查清单

- [ ] 宝塔面板安装完成，能正常登录
- [ ] Docker 和 Docker Compose 安装完成
- [ ] 项目文件已上传到 `/www/wwwroot/qlkj`（排除 venv）
- [ ] `.env` 文件已创建并填入正确的生产配置
- [ ] `.env` 中 `JWT_SECRET` 已设置为强随机密钥（必填，否则无法启动）
- [ ] `.env` 中 `CORS_ORIGINS` 已设置为前端域名
- [ ] `.env` 中 `DEBUG_MODE` 保持 `false`（生产环境不暴露 /docs）
- [ ] `docker-compose up -d --build` 所有容器正常运行
- [ ] `alembic upgrade head` 数据库迁移完成
- [ ] `curl http://localhost:8080/api/health` 返回 `{"status":"ok"}`
- [ ] `curl http://localhost:8080/docs` 返回 404（安全加固确认）
- [ ] 云服务商安全组已放行 8080 端口
- [ ] （可选）域名已解析，宝塔反向代理已配置
- [ ] （可选）SSL 证书已申请，HTTPS 访问正常
- [ ] （可选）定时备份已配置

---

## 十一、安全加固说明（2025-05 更新）

本次更新修复了以下安全漏洞，部署时请务必检查：

### 新增的必填环境变量

| 变量 | 说明 | 不配置的后果 |
|------|------|-------------|
| `JWT_SECRET` | JWT 签名密钥 | **应用拒绝启动** |
| `CORS_ORIGINS` | 允许的前端域名 | 前端无法跨域调用 API |

### 新增的可选环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DEBUG_MODE` | `false` | 设为 `true` 可临时开启 `/docs` 调试 |
| `DEV_MODE` | `false` | 设为 `true` 验证码固定为 123456（**生产环境切勿开启**） |

### 安全修复内容

- ✅ JWT 密钥强制配置，拒绝不安全的默认值
- ✅ 验证码暴力破解防护（5 次失败后锁定，需重新获取）
- ✅ CORS 收紧为指定域名（不再允许 `*`）
- ✅ 生产环境默认关闭 `/docs` Swagger 文档
- ✅ 文件上传增加扩展名白名单 + Pillow 内容验证 + 大小限制
- ✅ 验证码/配对码使用密码学安全随机数（`secrets` 替代 `random`）
- ✅ Nginx 添加安全响应头（X-Frame-Options, CSP 等）
- ✅ 错误信息脱敏（内部异常不再返回给客户端）

### 已有服务器快速更新

```bash
cd /www/wwwroot/qlkj

# 拉取代码
git pull

# 编辑 .env，新增以下配置：
# JWT_SECRET=（必填，用 python3 -c "import secrets; print(secrets.token_urlsafe(48))" 生成）
# CORS_ORIGINS=https://你的域名
# DEBUG_MODE=false

# 重建并重启
sudo docker-compose up -d --build

# 验证
curl http://localhost:8080/api/health
curl -o /dev/null -s -w "%{http_code}" http://localhost:8080/docs
# 期望：health 返回 ok，docs 返回 404
```

---

*文档版本：v1.2 · 最后更新：2025 年 5 月*
