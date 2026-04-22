from pathlib import Path
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import api_router
from app.core.config import get_settings
from app.core.exceptions import global_exception_handler
from app.core.database import db_manager
from app.core.transaction import TransactionManager
from app.db.base import Base
from app.db.session import engine
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.security_middleware import SecurityMiddleware

# 配置日志
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT,
    filename=settings.LOG_FILE
)
logger = logging.getLogger(__name__)

# 创建事务管理器
transaction_manager = TransactionManager(db_manager)

# Create database tables on startup. Alembic should manage this in production.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
    description="School Athletics Management System API",
    version="1.0.0"
)

# 添加日志中间件
app.add_middleware(LoggingMiddleware)

# 添加安全中间件
app.add_middleware(SecurityMiddleware)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# 添加全局异常处理器
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(api_router, prefix=settings.API_V1_STR)

# Serve Vue frontend build output
PROJECT_ROOT = Path(__file__).resolve().parent.parent
vue_dist = PROJECT_ROOT / "vue-frontend" / "dist"

if vue_dist.exists():
    if (vue_dist / "assets").exists():
        app.mount("/assets", StaticFiles(directory=vue_dist / "assets"), name="vue-assets")
    if (vue_dist / "images").exists():
        app.mount("/images", StaticFiles(directory=vue_dist / "images"), name="vue-images")


@app.get("/", include_in_schema=False)
async def root_redirect() -> RedirectResponse:
    """Send browsers to the Vue frontend or API docs."""
    if vue_dist.exists():
        return RedirectResponse(url="/app")
    return RedirectResponse(url=f"{settings.API_V1_STR}/docs")


@app.get("/login", include_in_schema=False)
@app.get("/admin/{rest:path}", include_in_schema=False)
@app.get("/athlete/{rest:path}", include_in_schema=False)
@app.get("/app", include_in_schema=False)
async def serve_vue_spa() -> "Response":
    """Serve the Vue SPA index.html for all frontend routes."""
    from fastapi.responses import FileResponse

    if vue_dist.exists():
        return FileResponse(vue_dist / "index.html")
    return RedirectResponse(url=f"{settings.API_V1_STR}/docs")


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "environment": settings.ENVIRONMENT}


@app.get("/metrics")
async def metrics():
    """指标端点（可选）"""
    if settings.ENABLE_METRICS:
        return {"metrics": "available"}
    return {"metrics": "disabled"}
