from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from typing import Generator
import logging
import time
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.engine = None
        self.SessionLocal = None
        self._setup_database()
    
    def _setup_database(self):
        """设置数据库连接"""
        # 连接池配置
        engine_options = {
            "pool_pre_ping": True,
            "pool_recycle": self.settings.DB_POOL_RECYCLE,
            "pool_size": self.settings.DB_POOL_SIZE,
            "max_overflow": self.settings.DB_MAX_OVERFLOW,
            "pool_timeout": 30,
            "echo": False,  # 生产环境设置为False
            "future": True,
        }
        
        # SQLite特殊配置
        if self.settings.DB_ENGINE.startswith("sqlite"):
            engine_options["connect_args"] = {"check_same_thread": False}
        else:
            # PostgreSQL配置
            engine_options["pool_pre_ping"] = True
            engine_options["pool_reset_on_return"] = "commit"
        
        # 创建引擎
        self.engine = create_engine(
            self.settings.database_uri,
            **engine_options
        )
        
        # 创建会话工厂
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # 注册事件监听器
        self._register_event_listeners()
    
    def _register_event_listeners(self):
        """注册数据库事件监听器"""
        
        @event.listens_for(self.engine, "engine_connect")
        def receive_connect(dbapi_connection, connection_record):
            """连接建立时的处理"""
            logger.info(f"Database connection established: {connection_record.info}")
        
        @event.listens_for(self.engine, "engine_disconnect")
        def receive_disconnect(dbapi_connection, connection_record):
            """连接断开时的处理"""
            logger.info(f"Database connection disconnected: {connection_record.info}")
        
        @event.listens_for(self.engine, "before_cursor_execute")
        def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """执行SQL前的处理"""
            context._query_start_time = time.time()
        
        @event.listens_for(self.engine, "after_cursor_execute")
        def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """执行SQL后的处理"""
            total_time = time.time() - context._query_start_time
            if total_time > 1.0:  # 记录执行时间超过1秒的查询
                logger.warning(f"Slow query detected: {statement} - {total_time:.2f}s")
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """获取数据库会话"""
        session = self.SessionLocal()
        try:
            yield session
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error: {str(e)}", exc_info=True)
            raise
        finally:
            session.close()
    
    def get_session_dependency(self) -> Generator[Session, None, None]:
        """FastAPI依赖注入的数据库会话"""
        return self.get_session()


# 创建数据库管理器实例
db_manager = DatabaseManager()

# 保持向后兼容性
engine = db_manager.engine
SessionLocal = db_manager.SessionLocal

# 导出依赖注入函数
def get_db() -> Generator[Session, None, None]:
    """FastAPI依赖注入的数据库会话"""
    return db_manager.get_session_dependency()