from sqlalchemy import Column, Integer, String
from realtime_ai_character.database.base import Base

# 定义了一个 User 类，用于存储用户信息
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)
#定义了一个to_dict方法,将用户信息转换为字典
    def save(self, db):
        db.add(self)
        db.commit()
