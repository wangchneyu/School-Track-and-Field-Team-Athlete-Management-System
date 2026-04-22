#!/bin/bash

# 生产级运行脚本
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
ENVIRONMENT=${ENVIRONMENT:-production}
PORT=${PORT:-8000}
WORKERS=${WORKERS:-4}
LOG_LEVEL=${LOG_LEVEL:-info}

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

log_debug() {
    if [ "$LOG_LEVEL" = "debug" ]; then
        echo -e "${BLUE}[DEBUG]${NC} $1"
    fi
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 未安装"
        exit 1
    fi
    
    if ! command -v pip &> /dev/null; then
        log_error "pip 未安装"
        exit 1
    fi
    
    if ! command -v uvicorn &> /dev/null; then
        log_warn "uvicorn 未安装，正在安装..."
        pip install uvicorn[standard]
    fi
    
    log_info "依赖检查通过"
}

# 检查环境变量
check_environment() {
    log_info "检查环境变量..."
    
    if [ ! -f .env ]; then
        log_error ".env 文件不存在"
        exit 1
    fi
    
    # 加载环境变量
    export $(grep -v '^#' .env | xargs)
    
    # 检查关键变量
    if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "your-secret-key-here-change-in-production" ]; then
        log_error "SECRET_KEY 未正确设置"
        exit 1
    fi
    
    if [ -z "$DB_PASSWORD" ] || [ "$DB_PASSWORD" = "your-password-here" ]; then
        log_error "DB_PASSWORD 未正确设置"
        exit 1
    fi
    
    log_info "环境变量检查通过"
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."
    
    mkdir -p logs
    mkdir -p data
    mkdir -p backups
    
    # 设置权限
    chmod 755 logs data backups
    
    log_info "目录创建完成"
}

# 数据库检查
check_database() {
    log_info "检查数据库连接..."
    
    # 等待数据库启动
    for i in {1..30}; do
        if python -c "
import sys
sys.path.append('/app')
from app.core.database import db_manager
try:
    with db_manager.get_session() as session:
        print('Database connection successful')
    exit(0)
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
" 2>/dev/null; then
        log_info "数据库连接成功"
        return 0
    fi
        
        if [ $i -eq 30 ]; then
            log_error "数据库连接失败，请检查数据库服务"
            exit 1
        fi
        
        sleep 2
        log_debug "等待数据库启动... ($i/30)"
    done
}

# 运行数据库迁移
run_migrations() {
    log_info "运行数据库迁移..."
    
    python -m alembic upgrade head
    
    if [ $? -eq 0 ]; then
        log_info "数据库迁移完成"
    else
        log_error "数据库迁移失败"
        exit 1
    fi
}

# 初始化数据
init_data() {
    log_info "初始化基础数据..."
    
    python -c "
import sys
sys.path.append('/app')
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
        
        # 更新密码（如果需要）
        if existing_admin.password_hash != get_password_hash('admin123'):
            existing_admin.password_hash = get_password_hash('admin123')
            db.commit()
            print('管理员密码已更新')
        
finally:
    db.close()
"
    
    log_info "基础数据初始化完成"
}

# 启动应用
start_app() {
    log_info "启动应用..."
    
    # 设置环境变量
    export PYTHONPATH=/app
    export PYTHONUNBUFFERED=1
    
    # 启动应用
    if [ "$ENVIRONMENT" = "production" ]; then
        log_info "以生产模式启动..."
        exec uvicorn app.main:app \
            --host 0.0.0.0 \
            --port $PORT \
            --workers $WORKERS \
            --log-level $LOG_LEVEL \
            --access-log \
            --access-log-file logs/access.log \
            --error-log-file logs/error.log
    else
        log_info "以开发模式启动..."
        exec uvicorn app.main:app \
            --host 0.0.0.0 \
            --port $PORT \
            --reload \
            --log-level debug
    fi
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    for i in {1..10}; do
        if curl -f http://localhost:$PORT/health > /dev/null 2>&1; then
            log_info "健康检查通过"
            return 0
        fi
        
        if [ $i -eq 10 ]; then
            log_error "健康检查失败"
            exit 1
        fi
        
        sleep 2
        log_debug "等待应用启动... ($i/10)"
    done
}

# 主函数
main() {
    echo "🚀 启动 School Athletics Management System"
    echo "📋 环境: $ENVIRONMENT"
    echo "🌐 端口: $PORT"
    echo "👥 工作进程: $WORKERS"
    echo "📊 日志级别: $LOG_LEVEL"
    echo ""
    
    check_dependencies
    check_environment
    create_directories
    check_database
    
    # 检查是否需要运行迁移
    if [ "$1" = "migrate" ]; then
        run_migrations
    fi
    
    # 检查是否需要初始化数据
    if [ "$2" = "init" ]; then
        init_data
    fi
    
    # 启动应用
    start_app &
    
    # 等待应用启动
    sleep 5
    
    # 健康检查
    if health_check; then
        echo ""
        log_info "🎉 应用启动成功！"
        echo ""
        echo "📋 访问信息："
        echo "   应用地址: http://localhost:$PORT"
        echo "   API文档: http://localhost:$PORT/docs"
        echo "   健康检查: http://localhost:$PORT/health"
        echo ""
        echo "🔧 管理命令："
        echo "   查看日志: tail -f logs/access.log"
        echo "   查看错误: tail -f logs/error.log"
        echo "   停止服务: Ctrl+C"
        echo ""
        echo "👤 默认管理员账户："
        echo "   用户名: admin"
        echo "   密码: admin123"
        echo ""
        
        # 保持脚本运行
        wait
    else
        log_error "应用启动失败"
        exit 1
    fi
}

# 运行主函数
main "$@"