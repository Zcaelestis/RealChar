from dotenv import load_dotenv #load environment variables from .env file

from realtime_ai_character.logger import get_logger
from realtime_ai_character.utils import Singleton #确保只有一个实例
from realtime_ai_character.database.connection import get_db # 从 database.connection 中导入 get_db 函数吗,用于获取数据库
load_dotenv() #从 .env 文件中加载环境变量
logger = get_logger(__name__) #初始化 logger记录日志

# 定义 MemoryManager 类,继承 Singleton 类,用于manage memory
class MemoryManager(Singleton):
   #构造函数,参数有sql_db
    def __init__(self):
        super().__init__() #calling super class constructor
        self.sql_db = next(get_db()) # 获取数据库连接

    async def process_session(self, session_id: str): # 定义 process_session 函数,用于处理 session with session_id
        # Not implemented.
        pass

    async def similarity_search(self, user_id: str, query: str): # 定义 similarity_search 函数,用于 search for similar documents with user_id and query
        # Not implemented.
        pass

#定义一个函数 get_memory_manager,用于获取 MemoryManager class 的实例
def get_memory_manager():
    return MemoryManager.get_instance() # 返回 MemoryManager class 的实例
#如果module run as main,则执行下面的代码,create a memory manager instance

if __name__ == '__main__':
    manager = MemoryManager.get_instance()
