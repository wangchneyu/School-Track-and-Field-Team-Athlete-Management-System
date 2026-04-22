from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.security import SecuritySettings
import time
import asyncio
from collections import defaultdict

security_settings = SecuritySettings()


class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件"""
    
    def __init__(self, app):
        super().__init__(app)
        self.rate_limiter = defaultdict(list)
        self.bearer_auth = HTTPBearer()
    
    async def dispatch(self, request: Request, call_next):
        # 执行速率限制检查
        if not await self._check_rate_limit(request):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        # 对于需要认证的端点，检查JWT
        if request.url.path.startswith("/api/v1"):
            try:
                credentials = await self.bearer_auth(request)
                # 这里可以添加JWT验证逻辑
            except HTTPException:
                # 对于某些端点允许匿名访问
                if request.url.path in ["/api/v1/auth/login"]:
                    pass
                else:
                    raise
        
        response = await call_next(request)
        
        # 添加安全头部
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response
    
    async def _check_rate_limit(self, request: Request) -> bool:
        """检查速率限制"""
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # 清理过期的请求记录
        self.rate_limiter[client_ip] = [
            timestamp for timestamp in self.rate_limiter[client_ip]
            if current_time - timestamp < security_settings.RATE_LIMIT_WINDOW
        ]
        
        # 检查是否超过限制
        if len(self.rate_limiter[client_ip]) >= security_settings.RATE_LIMIT_REQUESTS:
            return False
        
        # 记录当前请求
        self.rate_limiter[client_ip].append(current_time)
        return True