# This file is used to create a chroma instance for the database, which employs  OpenAIEmbeddings to generate embeddings for text and
# persist them to ./chroma.db. 
import os  
from dotenv import load_dotenv #loan environment variables from .env file
from langchain.vectorstores import Chroma 
from langchain.embeddings import OpenAIEmbeddings
from realtime_ai_character.logger import get_logger  

load_dotenv() #加载环境变量
logger = get_logger(__name__) #初始化logger对象,用于记录日志
# 使用从环境变量OPENAI_API_KEY中获取的API键创建一个OpenAIEmbeddings实例。
# 如果环境变量OPENAI_API_TYPE的值为'azure'，则重新创建一个OpenAIEmbeddings实例并设置参数deployment和chunk_size。
embedding = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY")) # 初始化 OpenAIEmbeddings,使用 OpenAI 的 API
if os.getenv('OPENAI_API_TYPE') == 'azure': # 如果使用的是 Azure,使用 Azure 的 OpenAIEmbeddings
    embedding = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"), deployment=os.getenv(
        "OPENAI_API_EMBEDDING_DEPLOYMENT_NAME", "text-embedding-ada-002"), chunk_size=1)  

# 创建一个chroma instance,参数有collection_name,embedding_function,persist_directory
def get_chroma(): # 定义get_chroma函数,创建并返回一个chroma实例
    
    chroma = Chroma(
        collection_name='llm', # collection_name 为 llm
        embedding_function=embedding, # embedding_function 为 embedding
        persist_directory='./chroma.db' # persist_directory 为 ./chroma.db
    ) 
    return chroma # 返回 chroma 实例