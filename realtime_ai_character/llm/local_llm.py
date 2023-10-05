from typing import List, Union
# from langchain.callbacks.streaming_stdout import 与streaming和聊天模型有关的类和model
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import BaseMessage, HumanMessage
#导入其他模块中数据库,搜索代理,多代理,计时,日志,角色,语言模型类
from realtime_ai_character.database.chroma import get_chroma
from realtime_ai_character.llm.base import (
    AsyncCallbackAudioHandler,
    AsyncCallbackTextHandler,
    LLM,
    SearchAgent,
)
from realtime_ai_character.logger import get_logger
from realtime_ai_character.utils import Character, timed


logger = get_logger(__name__) #初始化logger记录日志

#定义了localLlm,继承了LLM类,并重写了__init__函数,实现了对话功能,定义了项目中的语言模型接口.实现了base.py中的获取模型配置的get_config方法和用于与语言模型进行交互的achat方法。
class LocalLlm(LLM):
    def __init__(self, url):
        #初始化函数,用于与语言模型进行交互,model为localLLM
        self.chat_open_ai = ChatOpenAI(
            model="Local LLM",
            temperature=0.5,
            streaming=True,
            openai_api_base=url,
            
        )
        self.config = {"model": "Local LLM", "temperature": 0.5, "streaming": True}
        self.db = get_chroma()
        self.search_agent = None
        self.search_agent = SearchAgent()
#获取配置文件config信息
    def get_config(self):
        return self.config

    @timed
    async def achat(
        self,
        history: Union[List[BaseMessage], List[str]],
        user_input: str,
        user_input_template: str,
        callback: AsyncCallbackTextHandler,
        audioCallback: AsyncCallbackAudioHandler,
        character: Character,
        useSearch: bool = False,
        metadata: dict = None,
        *args,
        **kwargs,
    ) -> str:
        # 1. Generate context
        context = self._generate_context(user_input, character)
        # Get search result if enabled, and append to context
        if useSearch:
            context += self.search_agent.search(user_input)
        
        # 2. Add user input to history
        history.append(
            HumanMessage(
                content=user_input_template.format(context=context, query=user_input)
            )
        )

        # 3. Generate response by calling LLM
        response = await self.chat_open_ai.agenerate(
            [history],
            callbacks=[callback, audioCallback, StreamingStdOutCallbackHandler()],
            metadata=metadata,
        )
        logger.info(f"Response: {response}")                            #记录response
        return response.generations[0][0].text                          #返回responsed text

    def _generate_context(self, query, character: Character) -> str:    #定义_generate_context函数,用于生成与character相关的上下文
        docs = self.db.similarity_search(query)                         #调用similarity_search函数,返回与query相关的文档
        docs = [d for d in docs if d.metadata["character_name"] == character.name] #如果文档的metadata中的character_name与character的name相同,则将该文档添加到docs中
        logger.info(f"Found {len(docs)} documents")                     #记录找到的文档数量

        context = "\n".join([d.page_content for d in docs])             #将docs中的文档内容连接起来
        return context                                                  #返回context
