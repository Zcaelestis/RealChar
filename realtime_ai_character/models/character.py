from sqlalchemy import Column, String, DateTime, JSON 
from sqlalchemy.inspection import inspect
import datetime
from realtime_ai_character.database.base import Base
from pydantic import BaseModel
from typing import Optional

# 定义了一个 Character 类，用于存储角色的信息
class Character(Base): 
    __tablename__ = "characters" #定义了table name
     #定义了columns of the table
    id = Column(String(), primary_key=True, index=True, nullable=False)  #id是主键,索引,不为空
    name = Column(String(1024), nullable=False)                          #name不为空  
    system_prompt = Column(String(262144), nullable=True)                  
    user_prompt = Column(String(262144), nullable=True)
    text_to_speech_use = Column(String(100), nullable=True)
    voice_id = Column(String(100), nullable=True)
    author_id = Column(String(100), nullable=True)
    visibility = Column(String(100), nullable=True)
    data = Column(JSON(), nullable=True)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)
    tts = Column(String(64), nullable=True)
    avatar_id = Column(String(100), nullable=True) 
    #定义了一个to_dict方法,将角色信息转换为字典
    def to_dict(self):
        return {
            c.key:
            getattr(self, c.key).isoformat() if isinstance(
                getattr(self, c.key), datetime.datetime) else getattr(
                    self, c.key)
            for c in inspect(self).mapper.column_attrs
        }   #key是列名,value是列的值,如果value是datetime.datetime类型,则将其转换为isoformat,否则直接返回value
    #定义了save方法,将角色信息保存到数据库中
    def save(self, db):
        db.add(self)
        db.commit()

# 定义了一个 CharacterRequest 类，用于接收创建角色的请求,包括:name...   
class CharacterRequest(BaseModel):
    name: str                           #name是str类型
    system_prompt: Optional[str] = None #system_prompt是str类型,可选
    user_prompt: Optional[str] = None   #user_prompt是str类型,可选
    tts: Optional[str] = None
    voice_id: Optional[str] = None
    visibility: Optional[str] = None
    data: Optional[dict] = None
    avatar_id: Optional[str] = None

# 定义了一个 EditCharacterRequest 类，用于接收编辑角色的请求
class EditCharacterRequest(BaseModel):
    id: str
    name: Optional[str] = None
    system_prompt: Optional[str] = None
    user_prompt: Optional[str] = None
    text_to_speech_use: Optional[str] = None
    voice_id: Optional[str] = None
    visibility: Optional[str] = None
    data: Optional[dict] = None
    avatar_id: Optional[str] = None

#定义了一个 DeleteCharacterRequest 类，用于接收删除角色的请求
class DeleteCharacterRequest(BaseModel):
    character_id: str
#定义了一个 GeneratePromptRequest 类，用于接收生成提示的请求
class GeneratePromptRequest(BaseModel):
    name: str
    background: Optional[str] = None
