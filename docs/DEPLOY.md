# 咔哒应用部署指南

## 部署方式

### 方式一：Docker 部署（推荐）

#### 1. 服务器要求

- 操作系统：Ubuntu 20.04+ / CentOS 7+ / Debian 10+
- 内存：2GB 以上
- 硬盘：20GB 以上
- 端口：80, 443, 8000

#### 2. 安装 Docker

**Ubuntu/Debian:**
```bash
# 更新包索引
sudo apt update

# 安装依赖
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# 添加 Docker GPG 密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加 Docker 源
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 将当前用户添加到 docker 组（可选）
sudo usermod -aG docker $USER
```

**CentOS:**
```bash
# 安装依赖
sudo yum install -y yum-utils

# 添加 Docker 源
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装 Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker
```

#### 3. 部署应用

```bash
# 克隆项目
git clone <your-repo-url> /opt/click
cd /opt/click

# 配置环境变量
cp .env.example .env
vi .env
```

**.env 配置说明:**
```bash
# 数据库密码（务必修改）
MYSQL_ROOT_PASSWORD=your_secure_password

# JWT 密钥（务必修改为随机字符串，可用命令生成：openssl rand -hex 32）
JWT_SECRET=$(openssl rand -hex 32)

# 应用访问地址
UPLOAD_BASE_URL=http://your-domain.com/uploads

# CORS 允许的前端域名（逗号分隔，留空则不允许跨域）
CORS_ORIGINS=https://your-domain.com,http://localhost:5173

# 调试模式（生产环境设为 false，开启后可访问 /docs Swagger 文档）
DEBUG_MODE=false

# 开发模式（验证码固定为 123456，生产环境切勿开启）
DEV_MODE=false

# 邮箱配置
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USER=your_email@qq.com
SMTP_PASSWORD=your_smtp_password
SMTP_FROM=your_email@qq.com

# DeepSeek API
DEEPSEEK_API_KEY=your_deepseek_api_key
```

```bash
# 运行部署脚本
./deploy.sh
```

#### 4. 常用命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 更新应用
git pull
docker-compose build
docker-compose up -d
docker-compose exec app alembic upgrade head
```

---

### 方式二：传统部署

#### 1. 安装依赖

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv mysql-server redis-server nginx

# 启动 MySQL 和 Redis
sudo systemctl start mysql
sudo systemctl start redis
```

#### 2. 配置 MySQL

```bash
# 登录 MySQL
sudo mysql

# 创建数据库和用户
CREATE DATABASE click_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'click'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON click_app.* TO 'click'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 3. 部署应用

```bash
# 进入项目目录
cd /opt/click/backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
vi .env
```

**.env 配置:**
```bash
DATABASE_URL=mysql+pymysql://click:your_password@localhost:3306/click_app
REDIS_URL=redis://localhost:6379
JWT_SECRET=your_secret_key
...
```

```bash
# 运行数据库迁移
alembic upgrade head

# 测试运行
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### 4. 配置 Systemd 服务

```bash
sudo vi /etc/systemd/system/click-app.service
```

```ini
[Unit]
Description=Click App
After=network.target mysql.service redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/click/backend
Environment="PATH=/opt/click/backend/venv/bin"
ExecStart=/opt/click/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 启动服务
sudo systemctl daemon-reload
sudo systemctl start click-app
sudo systemctl enable click-app
```

#### 5. 配置 Nginx

```bash
sudo vi /etc/nginx/sites-available/click
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /uploads/ {
        alias /opt/click/backend/uploads/;
        expires 30d;
    }
}
```

```bash
# 启用配置
sudo ln -s /etc/nginx/sites-available/click /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## SSL 证书配置（HTTPS）

### 使用 Let's Encrypt（免费）

```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 使用自签名证书（测试用）

```bash
# 生成证书
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem
```

---

## 域名配置

1. 在域名服务商添加 A 记录指向服务器 IP
2. 等待 DNS 生效（通常 10 分钟 - 24 小时）
3. 配置 SSL 证书

---

## 监控和维护

### 查看日志
```bash
# Docker 方式
docker-compose logs -f app

# 传统方式
sudo journalctl -u click-app -f
```

### 数据库备份
```bash
# Docker 方式
docker-compose exec mysql mysqldump -u root -p click_app > backup_$(date +%Y%m%d).sql

# 传统方式
mysqldump -u root -p click_app > backup_$(date +%Y%m%d).sql
```

### 数据库恢复
```bash
# Docker 方式
docker-compose exec -T mysql mysql -u root -p click_app < backup.sql

# 传统方式
mysql -u root -p click_app < backup.sql
```

---

## 常见问题

### 1. 端口被占用
```bash
# 查看端口占用
sudo lsof -i :80
sudo lsof -i :8000

# 停止占用进程
sudo kill <PID>
```

### 2. 数据库连接失败
- 检查 MySQL 是否运行：`sudo systemctl status mysql`
- 检查密码是否正确
- 检查防火墙设置

### 3. 权限问题
```bash
# 修复上传目录权限
sudo chown -R www-data:www-data /opt/click/backend/uploads
sudo chmod -R 755 /opt/click/backend/uploads
```

### 4. 内存不足
```bash
# 查看内存使用
free -h

# 添加 swap 分区
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```
