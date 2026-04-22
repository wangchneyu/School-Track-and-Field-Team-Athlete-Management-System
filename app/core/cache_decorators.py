from functools import wraps
from typing import Any, Callable, Dict, Optional
from fastapi import HTTPException, status
from datetime import timedelta
import logging
from app.core.cache import CacheManager

logger = logging.getLogger(__name__)


def cache_response(ttl: int = 300, key_prefix: str = "api"):
    """
    缓存API响应装饰器
    
    Args:
        ttl: 缓存过期时间（秒）
        key_prefix: 缓存键前缀
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 尝试从缓存获取
            cache_key = f"{key_prefix}:{func.__name__}"
            cached_data = CacheManager.get_api_response(cache_key, kwargs)
            
            if cached_data is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_data
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 缓存结果
            CacheManager.cache_api_response(cache_key, kwargs, result, ttl)
            logger.debug(f"Cached result for {cache_key}")
            
            return result
        
        return wrapper
    return decorator


def cache_user_data(ttl: int = 3600):
    """
    缓存用户数据装饰器
    
    Args:
        ttl: 缓存过期时间（秒）
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从kwargs中获取user_id
            user_id = kwargs.get('user_id')
            if not user_id:
                return await func(*args, **kwargs)
            
            # 尝试从缓存获取
            cached_data = CacheManager.get_user_data(user_id)
            if cached_data is not None:
                logger.debug(f"Cache hit for user {user_id}")
                return cached_data
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 缓存结果
            if result is not None:
                CacheManager.cache_user_data(user_id, result, ttl)
                logger.debug(f"Cached result for user {user_id}")
            
            return result
        
        return wrapper
    return decorator


def cache_athlete_data(ttl: int = 1800):
    """
    缓存运动员数据装饰器
    
    Args:
        ttl: 缓存过期时间（秒）
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从kwargs中获取athlete_id
            athlete_id = kwargs.get('athlete_id')
            if not athlete_id:
                return await func(*args, **kwargs)
            
            # 尝试从缓存获取
            cached_data = CacheManager.get_athlete_data(athlete_id)
            if cached_data is not None:
                logger.debug(f"Cache hit for athlete {athlete_id}")
                return cached_data
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 缓存结果
            if result is not None:
                CacheManager.cache_athlete_data(athlete_id, result, ttl)
                logger.debug(f"Cached result for athlete {athlete_id}")
            
            return result
        
        return wrapper
    return decorator


def cache_event_data(ttl: int = 7200):
    """
    缓存赛事数据装饰器
    
    Args:
        ttl: 缓存过期时间（秒）
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从kwargs中获取event_id
            event_id = kwargs.get('event_id')
            if not event_id:
                return await func(*args, **kwargs)
            
            # 尝试从缓存获取
            cached_data = CacheManager.get_event_data(event_id)
            if cached_data is not None:
                logger.debug(f"Cache hit for event {event_id}")
                return cached_data
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 缓存结果
            if result is not None:
                CacheManager.cache_event_data(event_id, result, ttl)
                logger.debug(f"Cached result for event {event_id}")
            
            return result
        
        return wrapper
    return decorator


def rate_limit(limit: int = 100, window: int = 60, key_prefix: str = "rate_limit"):
    """
    速率限制装饰器
    
    Args:
        limit: 限制请求数
        window: 时间窗口（秒）
        key_prefix: 限制键前缀
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成限制键
            client_ip = kwargs.get('request').client.host if 'request' in kwargs else "unknown"
            limit_key = f"{key_prefix}:{client_ip}"
            
            # 检查速率限制
            if not CacheManager.cache_rate_limit(limit_key, window, limit):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def invalidate_cache(*keys: str):
    """
    缓存失效装饰器
    
    Args:
        keys: 要清除的缓存键
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 清除缓存
            for key in keys:
                if key == 'user':
                    user_id = kwargs.get('user_id')
                    if user_id:
                        CacheManager.delete_user_data(user_id)
                elif key == 'athlete':
                    athlete_id = kwargs.get('athlete_id')
                    if athlete_id:
                        CacheManager.delete_athlete_data(athlete_id)
                elif key == 'event':
                    event_id = kwargs.get('event_id')
                    if event_id:
                        CacheManager.delete_event_data(event_id)
                elif key == 'api':
                    CacheManager.delete_api_response(func.__name__)
            
            logger.debug(f"Invalidated cache for keys: {keys}")
            return result
        
        return wrapper
    return decorator


class CacheDependency:
    """FastAPI依赖注入的缓存管理"""
    
    @staticmethod
    def get_cache_stats():
        """获取缓存统计信息"""
        return CacheManager.get_cache_stats()
    
    @staticmethod
    def clear_user_cache(user_id: int):
        """清除用户缓存"""
        return CacheManager.delete_user_data(user_id)
    
    @staticmethod
    def clear_athlete_cache(athlete_id: int):
        """清除运动员缓存"""
        return CacheManager.delete_athlete_data(athlete_id)
    
    @staticmethod
    def clear_event_cache(event_id: int):
        """清除赛事缓存"""
        return CacheManager.delete_event_data(event_id)
    
    @staticmethod
    def clear_api_cache():
        """清除API缓存"""
        return CacheManager.delete_api_response("")
    
    @staticmethod
    def clear_all_cache():
        """清除所有缓存"""
        # 这里可以扩展为清除所有类型的缓存
        CacheManager.delete_api_response("")
        logger.info("All cache cleared")