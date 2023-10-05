import datetime

from pydantic import BaseModel
from realtime_ai_character.database.base import Base
from sqlalchemy import Column, String, DateTime, Unicode
from sqlalchemy.inspection import inspect
from typing import Optional

# 定义了一个 Memory 类，用于存储用户记忆的信息
class Memory(Base):
    __tablename__ = "memory"

    memory_id = Column(String(64), primary_key=True)
    user_id = Column(String(50), nullable=True)
    source_session_id = Column(String(50), nullable=True)
    content = Column(Unicode(65535), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)
#定义了一个to_dict方法,将用户记忆信息转换为字典
    def to_dict(self):
        return {
            c.key:
            getattr(self, c.key).isoformat() if isinstance(
                getattr(self, c.key), datetime.datetime) else getattr(
                    self, c.key)
            for c in inspect(self).mapper.column_attrs
        }
#定义了save方法,将用户记忆信息保存到数据库中
    def save(self, db):
        db.add(self)
        db.commit()

# 定义了一个 MemoryRequest 类，用于接收用户记忆的请求
class EditMemoryRequest(BaseModel):
    memory_id: str
    source_session_id: Optional[str] = None
    content: Optional[str] = None
