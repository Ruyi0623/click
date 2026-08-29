#!/usr/bin/env bash
# deploy.sh — rsync 文件同步 + 远程命令执行
# 用法:
#   ./deploy.sh              仅同步文件到远程服务器
#   ./deploy.sh "命令"       同步文件后在远程执行指定命令
#
# 服务器信息通过环境变量提供，避免将凭据写入仓库
: "${REMOTE_USER:?请设置 REMOTE_USER}"
: "${REMOTE_HOST:?请设置 REMOTE_HOST}"
: "${REMOTE_DIR:?请设置 REMOTE_DIR}"
: "${SSH_PASS:?请设置 SSH_PASS}"
# ──────────────────────────────────────────────

set -euo pipefail

LOCAL_DIR="$(cd "$(dirname "$0")" && pwd)"
SSH_OPTS="-o StrictHostKeyChecking=no -o ControlMaster=auto -o ControlPath=/tmp/qlkj-deploy-%C -o ControlPersist=60s"

# 用 sshpass 包裹 ssh/scp/rsync 所需的 ssh 连接
export SSHPASS="$SSH_PASS"
SSH_CMD="sshpass -e ssh $SSH_OPTS"
RSYNC_SSH="$SSH_CMD"

# 排除列表
EXCLUDES=(
  --exclude='.git/'
  --exclude='frontend/'            # 前端不部署到服务器（微信小程序平台）
  --exclude='backend/venv/'
  --exclude='backend/__pycache__/'
  --exclude='backend/.pytest_cache/'
  --exclude='backend/test.db'
  --exclude='.env'
  --exclude='*.pyc'
  --exclude='__pycache__'
  --exclude='.claude/'
  --exclude='CLAUDE.md'
  --exclude='deploy.sh'
)

# ── 同步文件 ──
echo "📦 同步文件到 ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR} ..."
rsync -az --delete --info=progress2 \
  "${EXCLUDES[@]}" \
  --rsync-path="sudo rsync" \
  -e "$RSYNC_SSH" \
  "$LOCAL_DIR/" "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/"
echo "✅ 文件同步完成"

# ── 执行远程命令（如有） ──
if [[ $# -gt 0 ]]; then
  CMD="$*"
  echo "🚀 远程执行: $CMD"
  sshpass -e ssh $SSH_OPTS "${REMOTE_USER}@${REMOTE_HOST}" "cd ${REMOTE_DIR} && sudo $CMD"
fi
