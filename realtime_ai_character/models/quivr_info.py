from sqlalchemy import Column, Integer, String
from realtime_ai_character.database.base import Base
from pydantic import BaseModel
from typing import Optional

# 定义了一个 QuivrInfo 类，用于存储用户与Quivr的交互信息
class QuivrInfo(Base):
    __tablename__ = "quivr_info"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(50))
    quivr_api_key = Column(String)
    quivr_brain_id = Column(String)
#定义了一个to_dict方法,将用户与Quivr的交互信息转换为字典
    def save(self, db):
        db.add(self)
        db.commit()
#定义了save方法,将用户与Quivr的交互信息保存到数据库中
class UpdateQuivrInfoRequest(BaseModel):
    quivr_api_key: Optional[str] = None
    quivr_brain_id: Optional[str] = None
