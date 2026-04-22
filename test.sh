#!/bin/bash

# 生产级测试脚本
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🧪 开始测试 School Athletics Management System"
echo "=================================================="

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

log_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

# 测试计数器
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 测试结果函数
test_result() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if [ $1 -eq 0 ]; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
        log_info "✅ 测试通过: $2"
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
        log_error "❌ 测试失败: $2"
    fi
}

# 检查服务状态
check_service() {
    log_test "检查服务状态..."
    
    # 检查应用是否运行
    if curl -f http://localhost:8001/health > /dev/null 2>&1; then
        test_result 0 "应用服务正常"
    else
        test_result 1 "应用服务异常"
        return 1
    fi
    
    # 检查API文档
    if curl -f http://localhost:8001/docs > /dev/null 2>&1; then
        test_result 0 "API文档可访问"
    else
        test_result 1 "API文档不可访问"
    fi
}

# 测试API端点
test_api_endpoints() {
    log_test "测试API端点..."
    
    # 测试健康检查
    if curl -f http://localhost:8001/health > /dev/null 2>&1; then
        test_result 0 "健康检查端点"
    else
        test_result 1 "健康检查端点"
    fi
    
    # �试API版本
    if curl -f http://localhost:8001/api/v1/health > /dev/null 2>&1; then
        test_result 0 "API版本健康检查"
    else
        test_result 1 "API版本健康检查"
    fi
}

# 测试数据库连接
test_database() {
    log_test "测试数据库连接..."
    
    # 测试数据库连接
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
        test_result 0 "数据库连接"
    else
        test_result 1 "数据库连接"
    fi
}

# 测试认证功能
test_authentication() {
    log_test "测试认证功能..."
    
    # 测试登录接口
    LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
        -H "Content-Type: application/json" \
        -d '{"username": "admin", "password": "admin123"}')
    
    if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
        test_result 0 "管理员登录"
    else
        test_result 1 "管理员登录"
    fi
}

# 测试API响应格式
test_api_response_format() {
    log_test "测试API响应格式..."
    
    # 测试健康检查响应格式
    HEALTH_RESPONSE=$(curl -s http://localhost:8001/health)
    
    if echo "$HEALTH_RESPONSE" | grep -q "status"; then
        test_result 0 "健康检查响应格式"
    else
        test_result 1 "健康检查响应格式"
    fi
    
    # 测试错误响应格式
    ERROR_RESPONSE=$(curl -s -X GET http://localhost:8001/api/v1/nonexistent)
    
    if echo "$ERROR_RESPONSE" | grep -q "error"; then
        test_result 0 "错误响应格式"
    else
        test_result 1 "错误响应格式"
    fi
}

# 测试CORS
test_cors() {
    log_test "测试CORS..."
    
    # 测试CORS头部
    CORS_RESPONSE=$(curl -s -I -X OPTIONS http://localhost:8001/api/v1/health \
        -H "Origin: http://localhost:3000" \
        -H "Access-Control-Request-Method: GET" \
        -H "Access-Control-Request-Headers: Content-Type")
    
    if echo "$CORS_RESPONSE" | grep -q "Access-Control-Allow-Origin"; then
        test_result 0 "CORS配置"
    else
        test_result 1 "CORS配置"
    fi
}

# 测试安全头部
test_security_headers() {
    log_test "测试安全头部..."
    
    # 测试安全头部
    HEADERS_RESPONSE=$(curl -s -I http://localhost:8001/health)
    
    SECURITY_HEADERS_COUNT=0
    
    if echo "$HEADERS_RESPONSE" | grep -q "X-Content-Type-Options"; then
        SECURITY_HEADERS_COUNT=$((SECURITY_HEADERS_COUNT + 1))
    fi
    
    if echo "$HEADERS_RESPONSE" | grep -q "X-Frame-Options"; then
        SECURITY_HEADERS_COUNT=$((SECURITY_HEADERS_COUNT + 1))
    fi
    
    if echo "$HEADERS_RESPONSE" | grep -q "X-XSS-Protection"; then
        SECURITY_HEADERS_COUNT=$((SECURITY_HEADERS_COUNT + 1))
    fi
    
    if [ $SECURITY_HEADERS_COUNT -ge 2 ]; then
        test_result 0 "安全头部"
    else
        test_result 1 "安全头部"
    fi
}

# 测试性能
test_performance() {
    log_test "测试性能..."
    
    # 测试响应时间
    START_TIME=$(date +%s%N)
    curl -f http://localhost:8001/health > /dev/null 2>&1
    END_TIME=$(date +%s%N)
    
    RESPONSE_TIME=$((($END_TIME - $START_TIME) / 1000000))
    
    if [ $RESPONSE_TIME -lt 1000 ]; then
        test_result 0 "响应时间 (${RESPONSE_TIME}ms)"
    else
        test_result 1 "响应时间 (${RESPONSE_TIME}ms)"
    fi
    
    # 测试并发请求
    CONCURRENT_REQUESTS=10
    PARALLEL_SUCCESS=0
    
    for i in $(seq 1 $CONCURRENT_REQUESTS); do
        curl -f http://localhost:8001/health > /dev/null 2>&1 &
        if [ $? -eq 0 ]; then
            PARALLEL_SUCCESS=$((PARALLEL_SUCCESS + 1))
        fi
    done
    
    wait
    
    if [ $PARALLEL_SUCCESS -eq $CONCURRENT_REQUESTS ]; then
        test_result 0 "并发请求 ($CONCURRENT_REQUESTS)"
    else
        test_result 1 "并发请求 ($PARALLEL_SUCCESS/$CONCURRENT_REQUESTS)"
    fi
}

# 测试数据库查询
test_database_queries() {
    log_test "测试数据库查询..."
    
    # 测试用户查询
    if python -c "
import sys
sys.path.append('/app')
from app.db.session import SessionLocal
from app.models.user import User

db = SessionLocal()
try:
    user = db.query(User).filter(User.username == 'admin').first()
    if user and user.role == 'admin':
        print('Admin user found')
        exit(0)
    else:
        print('Admin user not found')
        exit(1)
except Exception as e:
    print(f'Database query failed: {e}')
    exit(1)
finally:
    db.close()
" 2>/dev/null; then
        test_result 0 "数据库查询"
    else
        test_result 1 "数据库查询"
    fi
}

# 生成测试报告
generate_report() {
    echo ""
    echo "📊 测试报告"
    echo "=================================================="
    echo "总测试数: $TOTAL_TESTS"
    echo "通过测试: $PASSED_TESTS"
    echo "失败测试: $FAILED_TESTS"
    echo "成功率: $((PASSED_TESTS * 100 / TOTAL_TESTS))%"
    echo ""
    
    if [ $FAILED_TESTS -eq 0 ]; then
        log_info "🎉 所有测试通过！系统已准备好投入生产环境。"
        return 0
    else
        log_error "❌ 有 $FAILED_TESTS 个测试失败，请检查系统配置。"
        return 1
    fi
}

# 主函数
main() {
    # 检查应用是否运行
    if ! curl -f http://localhost:8001/health > /dev/null 2>&1; then
        log_error "应用未运行，请先启动应用"
        exit 1
    fi
    
    # 运行测试
    check_service
    test_api_endpoints
    test_database
    test_authentication
    test_api_response_format
    test_cors
    test_security_headers
    test_performance
    test_database_queries
    
    # 生成报告
    generate_report
}

# 运行主函数
main "$@"