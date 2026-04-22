#!/bin/bash

# 生产级部署脚本
set -e

echo "🚀 开始部署 School Athletics Management System..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker和Docker Compose
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装"
        exit 1
    fi
    
    log_info "Docker 和 Docker Compose 检查通过"
}

# 检查环境变量
check_env() {
    if [ ! -f .env ]; then
        log_warn ".env 文件不存在，正在从 .env.example 复制..."
        cp .env.example .env
        log_warn "请编辑 .env 文件并设置正确的配置"
        exit 1
    fi
    
    # 检查关键环境变量
    source .env
    
    if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "your-secret-key-here-change-in-production" ]; then
        log_warn "SECRET_KEY 未设置或使用默认值，请在 .env 文件中设置"
    fi
    
    if [ -z "$DB_PASSWORD" ] || [ "$DB_PASSWORD" = "your-password-here" ]; then
        log_warn "DB_PASSWORD 未设置或使用默认值，请在 .env 文件中设置"
    fi
    
    log_info "环境变量检查通过"
}

# 构建和启动服务
deploy() {
    log_info "停止现有服务..."
    docker-compose down
    
    log_info "构建应用镜像..."
    docker-compose build --no-cache app
    
    log_info "启动服务..."
    docker-compose up -d
    
    log_info "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    log_info "检查服务状态..."
    docker-compose ps
    
    # 检查应用健康状态
    log_info "检查应用健康状态..."
    if curl -f http://localhost:8001/health > /dev/null 2>&1; then
        log_info "应用健康检查通过"
    else
        log_error "应用健康检查失败"
        docker-compose logs app
        exit 1
    fi
}

# 数据库迁移
migrate_db() {
    log_info "运行数据库迁移..."
    docker-compose exec app python -m alembic upgrade head
}

# 初始化数据
init_data() {
    log_info "初始化基础数据..."
    docker-compose exec app python -c "
from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.user import User

db = SessionLocal()
try:
    # 创建管理员用户
    admin = User(
        username='admin',
        password_hash=get_password_hash('admin123'),
        role='admin',
        is_active=True
    )
    
    # 检查是否已存在
    existing_admin = db.query(User).filter(User.username == 'admin').first()
    if not existing_admin:
        db.add(admin)
        db.commit()
        print('管理员用户创建成功')
    else:
        print('管理员用户已存在')
        
finally:
    db.close()
"
}

# 显示访问信息
show_info() {
    log_info "🎉 部署完成！"
    echo ""
    echo "📋 访问信息："
    echo "   应用地址: http://localhost:8001"
    echo "   API文档: http://localhost:8001/docs"
    echo "   健康检查: http://localhost:8001/health"
    echo ""
    echo "🔧 管理命令："
    echo "   查看日志: docker-compose logs -f app"
    echo "   停止服务: docker-compose down"
    echo "   重启服务: docker-compose restart app"
    echo ""
    echo "👤 默认管理员账户："
    echo "   用户名: admin"
    echo "   密码: admin123"
    echo ""
    echo "⚠️  重要提醒："
    echo "   1. 请立即修改默认密码"
    echo "   2. 请在生产环境中使用 HTTPS"
    echo "   3. 请定期备份数据库"
    echo "   4. 请设置适当的防火墙规则"
}

# 主函数
main() {
    log_info "开始部署流程..."
    
    check_docker
    check_env
    
    read -p "是否运行数据库迁移？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        migrate_db
    fi
    
    deploy
    
    read -p "是否初始化基础数据？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        init_data
    fi
    
    show_info
}

# 运行主函数
main "$@"