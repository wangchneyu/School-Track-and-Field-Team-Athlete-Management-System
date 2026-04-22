from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from app.core.cache import CacheManager
from app.core.cache_decorators import CacheDependency

router = APIRouter()


@router.get("/cache/stats")
async def get_cache_stats():
    """获取缓存统计信息"""
    return CacheDependency.get_cache_stats()


@router.delete("/cache/user/{user_id}")
async def clear_user_cache(user_id: int):
    """清除用户缓存"""
    result = CacheDependency.clear_user_cache(user_id)
    return {"message": "User cache cleared", "success": result}


@router.delete("/cache/athlete/{athlete_id}")
async def clear_athlete_cache(athlete_id: int):
    """清除运动员缓存"""
    result = CacheDependency.clear_athlete_cache(athlete_id)
    return {"message": "Athlete cache cleared", "success": result}


@router.delete("/cache/event/{event_id}")
async def clear_event_cache(event_id: int):
    """清除赛事缓存"""
    result = CacheDependency.clear_event_cache(event_id)
    return {"message": "Event cache cleared", "success": result}


@router.delete("/cache/api")
async def clear_api_cache():
    """清除API缓存"""
    result = CacheDependency.clear_api_cache()
    return {"message": "API cache cleared", "success": result}


@router.delete("/cache/all")
async def clear_all_cache():
    """清除所有缓存"""
    CacheDependency.clear_all_cache()
    return {"message": "All cache cleared", "success": True}


@router.get("/cache/health")
async def cache_health_check():
    """缓存健康检查"""
    stats = CacheDependency.get_cache_stats()
    return {
        "status": "healthy" if stats.get('redis_connected') else "degraded",
        "redis_connected": stats.get('redis_connected', False),
        "memory_info": stats.get('memory_info', {}),
        "keys_count": sum(stats.get('keys_by_prefix', {}).values())
    }