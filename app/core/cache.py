import json
import time
from typing import Any, Optional, Dict, List
from datetime import timedelta
import redis
from redis.exceptions import RedisError
import logging
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis缓存管理器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """连接Redis服务器"""
        try:
            self.redis_client = redis.Redis(
                host=self.settings.REDIS_HOST,
                port=self.settings.REDIS_PORT,
                db=self.settings.REDIS_DB,
                password=self.settings.REDIS_PASSWORD,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            # 测试连接
            self.redis_client.ping()
            logger.info("Redis连接成功")
        except RedisError as e:
            logger.warning(f"Redis连接失败: {e}, 将使用内存缓存作为备选")
            self.redis_client = None
    
    def _get_key(self, prefix: str, key: str) -> str:
        """生成缓存键"""
        return f"{prefix}:{key}"
    
    def set(self, prefix: str, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """设置缓存"""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._get_key(prefix, key)
            # 序列化复杂对象
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            if expire is None:
                expire = self.settings.CACHE_DEFAULT_TIMEOUT
            
            result = self.redis_client.setex(cache_key, expire, value)
            return bool(result)
        except RedisError as e:
            logger.error(f"Redis缓存设置失败: {e}")
            return False
    
    def get(self, prefix: str, key: str, default: Any = None) -> Any:
        """获取缓存"""
        if not self.redis_client:
            return default
        
        try:
            cache_key = self._get_key(prefix, key)
            value = self.redis_client.get(cache_key)
            
            if value is None:
                return default
            
            # 反序列化复杂对象
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except RedisError as e:
            logger.error(f"Redis缓存获取失败: {e}")
            return default
    
    def delete(self, prefix: str, key: str) -> bool:
        """删除缓存"""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._get_key(prefix, key)
            result = self.redis_client.delete(cache_key)
            return result > 0
        except RedisError as e:
            logger.error(f"Redis缓存删除失败: {e}")
            return False
    
    def exists(self, prefix: str, key: str) -> bool:
        """检查缓存是否存在"""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._get_key(prefix, key)
            return self.redis_client.exists(cache_key) > 0
        except RedisError as e:
            logger.error(f"Redis缓存检查失败: {e}")
            return False
    
    def expire(self, prefix: str, key: str, seconds: int) -> bool:
        """设置缓存过期时间"""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._get_key(prefix, key)
            return bool(self.redis_client.expire(cache_key, seconds))
        except RedisError as e:
            logger.error(f"Redis缓存过期设置失败: {e}")
            return False
    
    def ttl(self, prefix: str, key: str) -> int:
        """获取缓存剩余过期时间"""
        if not self.redis_client:
            return -1
        
        try:
            cache_key = self._get_key(prefix, key)
            return self.redis_client.ttl(cache_key)
        except RedisError as e:
            logger.error(f"Redis缓存TTL获取失败: {e}")
            return -1
    
    def clear_prefix(self, prefix: str) -> int:
        """清除指定前缀的所有缓存"""
        if not self.redis_client:
            return 0
        
        try:
            pattern = f"{prefix}:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except RedisError as e:
            logger.error(f"Redis缓存清除失败: {e}")
            return 0
    
    def incr(self, prefix: str, key: str, amount: int = 1) -> Optional[int]:
        """递增计数器"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = self._get_key(prefix, key)
            return self.redis_client.incrby(cache_key, amount)
        except RedisError as e:
            logger.error(f"Redis计数器递增失败: {e}")
            return None
    
    def decr(self, prefix: str, key: str, amount: int = 1) -> Optional[int]:
        """递减计数器"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = self._get_key(prefix, key)
            return self.redis_client.decrby(cache_key, amount)
        except RedisError as e:
            logger.error(f"Redis计数器递减失败: {e}")
            return None
    
    def get_keys_by_pattern(self, pattern: str) -> List[str]:
        """获取匹配模式的键"""
        if not self.redis_client:
            return []
        
        try:
            return self.redis_client.keys(pattern)
        except RedisError as e:
            logger.error(f"Redis键获取失败: {e}")
            return []
    
    def get_memory_info(self) -> Dict[str, Any]:
        """获取Redis内存信息"""
        if not self.redis_client:
            return {}
        
        try:
            info = self.redis_client.info('memory')
            return {
                'used_memory': info.get('used_memory', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'maxmemory': info.get('maxmemory', 0),
                'maxmemory_human': info.get('maxmemory_human', '0B'),
                'used_memory_peak': info.get('used_memory_peak', 0),
                'used_memory_peak_human': info.get('used_memory_peak_human', '0B'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'total_commands_processed': info.get('total_commands_processed', 0)
            }
        except RedisError as e:
            logger.error(f"Redis内存信息获取失败: {e}")
            return {}


# 全局缓存实例
cache = RedisCache()


class CacheManager:
    """缓存管理器，提供不同类型的缓存操作"""
    
    @staticmethod
    def cache_user_data(user_id: int, data: Dict[str, Any], expire: int = 3600) -> bool:
        """缓存用户数据"""
        return cache.set('user', str(user_id), data, expire)
    
    @staticmethod
    def get_user_data(user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户数据缓存"""
        return cache.get('user', str(user_id))
    
    @staticmethod
    def delete_user_data(user_id: int) -> bool:
        """删除用户数据缓存"""
        return cache.delete('user', str(user_id))
    
    @staticmethod
    def cache_athlete_data(athlete_id: int, data: Dict[str, Any], expire: int = 1800) -> bool:
        """缓存运动员数据"""
        return cache.set('athlete', str(athlete_id), data, expire)
    
    @staticmethod
    def get_athlete_data(athlete_id: int) -> Optional[Dict[str, Any]]:
        """获取运动员数据缓存"""
        return cache.get('athlete', str(athlete_id))
    
    @staticmethod
    def delete_athlete_data(athlete_id: int) -> bool:
        """删除运动员数据缓存"""
        return cache.delete('athlete', str(athlete_id))
    
    @staticmethod
    def cache_event_data(event_id: int, data: Dict[str, Any], expire: int = 7200) -> bool:
        """缓存赛事数据"""
        return cache.set('event', str(event_id), data, expire)
    
    @staticmethod
    def get_event_data(event_id: int) -> Optional[Dict[str, Any]]:
        """获取赛事数据缓存"""
        return cache.get('event', str(event_id))
    
    @staticmethod
    def delete_event_data(event_id: int) -> bool:
        """删除赛事数据缓存"""
        return cache.delete('event', str(event_id))
    
    @staticmethod
    def cache_api_response(endpoint: str, params: Dict[str, Any], data: Any, expire: int = 300) -> bool:
        """缓存API响应"""
        # 生成唯一的缓存键
        param_str = json.dumps(params, sort_keys=True, ensure_ascii=False)
        cache_key = f"{endpoint}:{hash(param_str)}"
        return cache.set('api', cache_key, data, expire)
    
    @staticmethod
    def get_api_response(endpoint: str, params: Dict[str, Any]) -> Any:
        """获取API响应缓存"""
        param_str = json.dumps(params, sort_keys=True, ensure_ascii=False)
        cache_key = f"{endpoint}:{hash(param_str)}"
        return cache.get('api', cache_key)
    
    @staticmethod
    def delete_api_response(endpoint: str) -> int:
        """删除API响应缓存"""
        return cache.clear_prefix('api')
    
    @staticmethod
    def cache_rate_limit(key: str, window: int, limit: int) -> bool:
        """缓存速率限制"""
        # 使用滑动窗口算法
        current_time = int(time.time())
        window_start = current_time - window
        
        # 清理过期的记录
        old_keys = cache.get_keys_by_pattern(f"rate_limit:{key}:*")
        for old_key in old_keys:
            timestamp = int(old_key.split(':')[-1])
            if timestamp < window_start:
                cache.delete('', old_key)
        
        # 检查当前计数
        current_count = cache.incr('rate_limit', f"{key}:{current_time}")
        if current_count is None:
            current_count = 1
            cache.set('rate_limit', f"{key}:{current_time}", current_count, window)
        
        return current_count <= limit
    
    @staticmethod
    def get_cache_stats() -> Dict[str, Any]:
        """获取缓存统计信息"""
        return {
            'redis_connected': cache.redis_client is not None,
            'memory_info': cache.get_memory_info(),
            'keys_by_prefix': {
                'user': len(cache.get_keys_by_pattern('user:*')),
                'athlete': len(cache.get_keys_by_pattern('athlete:*')),
                'event': len(cache.get_keys_by_pattern('event:*')),
                'api': len(cache.get_keys_by_pattern('api:*')),
                'rate_limit': len(cache.get_keys_by_pattern('rate_limit:*'))
            }
        }