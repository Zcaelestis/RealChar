import datetime #导入datetime模块

from sqlalchemy import Column, String, DateTime, Unicode 
from pydantic import BaseModel
from realtime_ai_character.database.base import Base
from typing import Optional

# 定义了一个 Feedback 类，用于存储用户反馈的信息
class Feedback(Base): 
    __tablename__ = "feedbacks" #定义了table name是feedbacks
#list of columns of the table contains: message_id...
    message_id = Column(String(64), primary_key=True)
    session_id = Column(String(50), nullable=True)
    user_id = Column(String(50), nullable=True)
    server_message_unicode = Column(Unicode(65535), nullable=True)
    feedback = Column(String(100), nullable=True)
    comment = Column(Unicode(65535), nullable=True)
    created_at = Column(DateTime(), nullable=False)
#定义了一个to_dict方法,将用户反馈信息转换为字典
    def to_dict(self):
        return {
            c.key:
            getattr(self, c.key).isoformat() if isinstance(  
                getattr(self, c.key), datetime.datetime) else getattr(
                    self, c.key)
            for c in inspect(self).mapper.column_attrs
        } #如果value是datetime.datetime类型,则将其转换为isoformat,iterate over all columns and return a dict
#定义了save方法,将用户反馈信息保存到数据库中
    def save(self, db):
        db.add(self) #add the object to the session
        db.commit()  #commit the session

# 定义了一个 FeedbackRequest 类，用于接收用户反馈的请求
class FeedbackRequest(BaseModel):
    message_id: str
    session_id: Optional[str] = None
    server_message_unicode: Optional[str] = None
    feedback: Optional[str] = None
    comment: Optional[str] = None
