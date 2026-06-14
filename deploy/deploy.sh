#!/bin/bash
set -e

echo "=================================="
echo "  黄师傅维修 - 腾讯云部署脚本"
echo "  适用: Ubuntu 22.04"
echo "=================================="

DOMAIN="${1:-}"  # 第一个参数: 你的域名 (如 repair.example.com)
if [ -z "$DOMAIN" ]; then
    echo "❌ 请提供域名!"
    echo "   用法: bash deploy.sh your-domain.com"
    echo "   示例: bash deploy.sh wx.niudanyun.com"
    exit 1
fi

# 1. 系统依赖
echo "[1/7] 安装系统依赖..."
apt update
apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx postgresql postgresql-client

# 2. 代码目录
cd /root/repair-system/backend

# 3. Python 环境
echo "[2/7] 安装 Python 依赖..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install psycopg2-binary

# 4. 配置 PostgreSQL
echo "[3/7] 配置数据库..."
PGPASSWORD=postgres psql -U postgres -c "CREATE DATABASE repair_system ENCODING 'UTF8';" 2>/dev/null || echo "数据库已存在"

# 写入 .env 配置
cat > /root/repair-system/backend/.env << ENVEOF
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/repair_system
SECRET_KEY=$(openssl rand -hex 32)
ACCESS_TOKEN_EXPIRE_MINUTES=1440
UPLOAD_DIR=./uploads
PG_POOL_SIZE=20
PG_MAX_OVERFLOW=40
ENVEOF

# 初始化数据库表 + 种子数据
python seed_data.py

# 5. Systemd 服务
echo "[4/7] 配置系统服务..."
cat > /etc/systemd/system/repair-system.service << SERVICEEOF
[Unit]
Description=黄师傅维修 API Service
After=network.target postgresql.service

[Service]
User=root
WorkingDirectory=/root/repair-system/backend
ExecStart=/root/repair-system/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5
EnvironmentFile=/root/repair-system/backend/.env

[Install]
WantedBy=multi-user.target
SERVICEEOF

systemctl daemon-reload
systemctl enable repair-system
systemctl start repair-system

# 6. Nginx + SSL
echo "[5/7] 配置 Nginx + SSL..."
mkdir -p /root/repair-system/backend/uploads

cat > /etc/nginx/sites-available/repair-system << NGINXEOF
server {
    listen 80;
    server_name $DOMAIN;
    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /uploads/ {
        alias /root/repair-system/backend/uploads/;
    }

    location /static/ {
        alias /root/repair-system/backend/static/;
    }
}
NGINXEOF

ln -sf /etc/nginx/sites-available/repair-system /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# 自动申请 SSL 证书
echo "[6/7] 申请 SSL 证书..."
certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m admin@$DOMAIN || echo "SSL 申请失败，可稍后手动运行: certbot --nginx -d $DOMAIN"

# 7. 更新前端 API 地址
echo "[7/7] 配置完成!"
echo ""
echo "=================================="
echo "  ✅ 部署完成！"
echo "=================================="
echo ""
echo "  访问地址: https://$DOMAIN"
echo "  管理后台: https://$DOMAIN/admin"
echo "  顾客报修: https://$DOMAIN/"
echo ""
echo "  管理员账号: 13800138000 / admin123"
echo "  调度员账号: 13800138001 / 123456"
echo ""
echo "  ===== 微信服务号配置 ===== "
echo ""
echo "  1. 登录微信公众号后台"
echo "     https://mp.weixin.qq.com"
echo ""
echo "  2. 设置 → 公众号设置 → 功能设置"
echo "     - 网页授权域名: $DOMAIN"
echo "     - JS接口安全域名: $DOMAIN"
echo ""
echo "  3. 新建菜单:"
echo "     - 菜单名称: 在线报修"
echo "     - 菜单链接: https://$DOMAIN/"
echo ""
echo "  4. (可选) 菜单加:"
echo "     - 📋 我的工单 → https://$DOMAIN/#track"
echo "     - 💬 联系客服 → https://$DOMAIN/#chat"
echo ""
echo "  ===== 常用命令 ===== "
echo "  systemctl status repair-system     # 服务状态"
echo "  systemctl restart repair-system    # 重启服务"
echo "  journalctl -u repair-system -f     # 查看日志"
echo "  certbot renew                      # 续期证书"
echo ""
