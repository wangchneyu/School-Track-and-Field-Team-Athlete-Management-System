from contextlib import contextmanager
from typing import Generator, Callable, Any, TypeVar
from sqlalchemy.orm import Session
import logging
from app.core.database import DatabaseManager

logger = logging.getLogger(__name__)

T = TypeVar('T')


class TransactionManager:
    """事务管理器"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    @contextmanager
    def transaction(self, session: Session = None) -> Generator[Session, None, None]:
        """事务上下文管理器"""
        if session is None:
            session = self.db_manager.get_session()
        
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Transaction failed: {str(e)}", exc_info=True)
            raise
        finally:
            if session is not None:
                session.close()
    
    def execute_in_transaction(self, func: Callable[[Session], T], session: Session = None) -> T:
        """在事务中执行函数"""
        with self.transaction(session) as trans_session:
            return func(trans_session)