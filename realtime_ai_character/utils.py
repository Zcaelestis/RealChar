import asyncio
from dataclasses import field
from time import perf_counter
from typing import List, Optional, Callable

from langchain.schema import AIMessage, BaseMessage, HumanMessage, SystemMessage
from pydantic.dataclasses import dataclass
from starlette.websockets import WebSocket, WebSocketState
from sqlalchemy.orm import Session
from realtime_ai_character.models.interaction import Interaction
from realtime_ai_character.logger import get_logger

# 用于存储角色信息,包括id,name,llm_system_prompt,llm_user_prompt....
@dataclass
class Character:
    character_id: str
    name: str
    llm_system_prompt: str
    llm_user_prompt: str
    source: str = ''
    location: str = ''
    voice_id: str = ''
    author_name: str = ''
    author_id: str = ''
    avatar_id: Optional[str] = ''
    visibility: str = ''
    tts: Optional[str] = ''
    data: Optional[dict] = None

# 用于存储对话历史信息,包括系统提示,用户信息,ai信息....
@dataclass
class ConversationHistory:
    system_prompt: str = ''
    user: list[str] = field(default_factory=list)
    ai: list[str] = field(default_factory=list)
# 构建函数用于迭代对话历史信息,返回系统提示,用户信息,ai信息
    def __iter__(self):
        yield self.system_prompt
        for user_message, ai_message in zip(self.user, self.ai):
            yield user_message
            yield ai_message
# 构建函数用于将对话历史信息存储到数据库中
    def load_from_db(self, session_id: str, db: Session):
        conversations = db.query(Interaction).filter(Interaction.session_id == session_id).all() # 通过session_id获取数据库中的所有Interaction
        for conversation in conversations: # 遍历所有Interaction,将用户信息和ai信息存储到数据库中
            self.user.append(conversation.client_message_unicode)
            self.ai.append(conversation.server_message_unicode)

#构建一个basemessage list从对话历史信息中
def build_history(conversation_history: ConversationHistory) -> List[BaseMessage]:
    history = []
    for i, message in enumerate(conversation_history): # 遍历对话历史信息,如果是第一次对话,则返回系统提示,否则返回对话历史信息
        if i == 0: # 如果是第一次对话,则返回系统提示
            history.append(SystemMessage(content=message))
        elif i % 2 == 0: # 如果是偶数,则返回用户信息
            history.append(AIMessage(content=message))
        else: # 如果是奇数,则返回ai信息
            history.append(HumanMessage(content=message))
    return history  # 返回对话历史信息
#构建一个singleton类
class Singleton:
    _instances = {}
#使用static access method for getting a instance
    @classmethod
    def get_instance(cls, *args, **kwargs):
        """ Static access method. """
        if cls not in cls._instances:
            cls._instances[cls] = cls(*args, **kwargs)

        return cls._instances[cls]
#使用static access method for initializing a instance
    @classmethod
    def initialize(cls, *args, **kwargs):
        """ Static access method. """
        if cls not in cls._instances:
            cls._instances[cls] = cls(*args, **kwargs)

#构建一个connection manager类,用于管理websocket连接
class ConnectionManager(Singleton):
    def __init__(self):
        self.active_connections: List[WebSocket] = []
#链接websocket的函数
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
#断开websocket的函数
    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"Client #{id(websocket)} left the chat")
        # await self.broadcast_message(f"Client #{id(websocket)} left the chat")
#发送消息的函数
    async def send_message(self, message: str, websocket: WebSocket):
        if websocket.application_state == WebSocketState.CONNECTED:
            await websocket.send_text(message)
#广播消息的函数
    async def broadcast_message(self, message: str):
        for connection in self.active_connections:
            if connection.application_state == WebSocketState.CONNECTED:
                await connection.send_text(message)

#获取connection manager的函数
def get_connection_manager():
    return ConnectionManager.get_instance()

#构建一个timer类,用于计时
class Timer(Singleton):
    def __init__(self):
        self.start_time: dict[str, float] = {}
        self.elapsed_time = {}
        self.logger = get_logger("Timer")
#开始计时的函数
    def start(self, id: str):
        self.start_time[id] = perf_counter()
#记录时间的函数
    def log(self, id: str, callback: Optional[Callable] = None):
        if id in self.start_time:
            elapsed_time = perf_counter() - self.start_time[id]
            del self.start_time[id]
            if id in self.elapsed_time:
                self.elapsed_time[id].append(elapsed_time)
            else:
                self.elapsed_time[id] = [elapsed_time]
            if callback:
                callback()
#报告时间的函数
    def report(self):
        for id, t in self.elapsed_time.items():
            self.logger.info(
                f"{id:<30s}: {sum(t)/len(t):.3f}s [{min(t):.3f}s - {max(t):.3f}s] "
                f"({len(t)} samples)"
            )
#重置时间的函数
    def reset(self):
        self.start_time = {}
        self.elapsed_time = {}

#获取timer的函数
def get_timer() -> Timer:
    return Timer.get_instance()

#计时decorator
def timed(func):
    if asyncio.iscoroutinefunction(func):
        async def async_wrapper(*args, **kwargs):
            timer = get_timer()
            timer.start(func.__qualname__)
            result = await func(*args, **kwargs)
            timer.log(func.__qualname__)
            return result
        return async_wrapper
    else:
        def sync_wrapper(*args, **kwargs):
            timer = get_timer()
            timer.start(func.__qualname__)
            result = func(*args, **kwargs)
            timer.log(func.__qualname__)
            return result
        return sync_wrapper
