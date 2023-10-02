import os
from typing import List 

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler #导入StreamingStdOutCallbackHandler
#根据环境变量OPENAI_API_TYPE的值,选择使用哪个语言模型
if os.getenv('OPENAI_API_TYPE') == 'azure':                                     # 如果使用的是 Azure,使用 Azure 的 StreamingStdOutCallbackHandler
    from langchain.chat_models import AzureChatOpenAI
else:
    from langchain.chat_models import ChatOpenAI # 否则使用 OpenAI 的 StreamingStdOutCallbackHandler
from langchain.schema import BaseMessage, HumanMessage #导入BaseMessage,HumanMessage
#从其他模块导入所需要的类和函数
from realtime_ai_character.database.chroma import get_chroma
from realtime_ai_character.llm.base import AsyncCallbackAudioHandler, \
    AsyncCallbackTextHandler, LLM, QuivrAgent, SearchAgent, MultiOnAgent
from realtime_ai_character.logger import get_logger
from realtime_ai_character.utils import Character, timed

logger = get_logger(__name__) #初始化logger记录日志

#openaiLlm类继承了LLM类,并重写了__init__函数,实现了对话功能,定义了项目中的语言模型接口.实现了base.py中的获取模型配置的get_config方法和用于与语言模型进行交互的achat方法。
#使用了数据库get_chroma方法获取相似的文档作为上下文，并通过_generate_context方法生成上下文
class OpenaiLlm(LLM):
    def __init__(self, model):                   #初始化函数,参数有model
        # 根据环境变量OPENAI_API_TYPE的值,选择使用哪个语言模型
        if os.getenv('OPENAI_API_TYPE') == 'azure':
            self.chat_open_ai = AzureChatOpenAI(
                deployment_name=os.getenv(
                    'OPENAI_API_MODEL_DEPLOYMENT_NAME', 'gpt-35-turbo'),
                model=model,
                temperature=0.5,
                streaming=True
            )
        else:
            self.chat_open_ai = ChatOpenAI(
                model=model,
                temperature=0.5,
                streaming=True
            )                                    #if 是azure,使用AzureChatOpenAI,否则使用ChatOpenAI
      # config(配置文件),参数有model,temperature,streaming
        self.config = {
            "model": model,
            "temperature": 0.5,
            "streaming": True
        }
        #初始化数据库以及搜索代理,quivr代理,multion代理
        self.db = get_chroma()
        self.search_agent = SearchAgent()
        self.quivr_agent = QuivrAgent()
        self.multion_agent = MultiOnAgent()
   #获取配置文件config信息
    def get_config(self):
        return self.config
    
    @timed #计时
    #定义异步聊天函数achat,用于generate response from OPENAI API
    async def achat(self,
                    history: List[BaseMessage],
                    user_input: str,
                    user_input_template: str,
                    callback: AsyncCallbackTextHandler,
                    audioCallback: AsyncCallbackAudioHandler,
                    character: Character,
                    useSearch: bool = False,
                    useQuivr: bool = False,
                    useMultiOn: bool = False,
                    quivrApiKey: str = None,
                    quivrBrainId: str = None,
                    metadata: dict = None,
                    *args, **kwargs) -> str:
        #  Generate context
        context = self._generate_context(user_input, character)
        memory_context = self._generate_memory_context(user_id='', query=user_input)
        if memory_context:
            context += ("Information regarding this user based on previous chat: "
            + memory_context + '\n')
        # Get search result if enabled
        if useSearch:
            context += self.search_agent.search(user_input)
        if useQuivr and quivrApiKey is not None and quivrBrainId is not None:
            context += self.quivr_agent.question(
                user_input, quivrApiKey, quivrBrainId)
        if useMultiOn:
            if (user_input.lower().startswith("multi_on") or 
                user_input.lower().startswith("multion")):
                response = await self.multion_agent.action(user_input)
                context += response

        #  Add user input to history
        history.append(HumanMessage(content=user_input_template.format(
            context=context, query=user_input)))

        # Generate response from OPENAI API
        response = await self.chat_open_ai.agenerate(
            [history], callbacks=[callback, audioCallback, StreamingStdOutCallbackHandler()],
            metadata=metadata)
        logger.info(f'Response: {response}')
        return response.generations[0][0].text  
    # 定义_generate_context函数,用于生成上下文
    def _generate_context(self, query, character: Character) -> str:
        # Search for similar documents
        docs = self.db.similarity_search(query)
        docs = [d for d in docs if d.metadata['character_name'] == character.name]
        logger.info(f'Found {len(docs)} documents')
        # Get the context from the documents
        context = '\n'.join([d.page_content for d in docs])
        return context  #返回上下文
    #定义_generate_memory_context函数,用于生成记忆上下文
    def _generate_memory_context(self, user_id: str, query: str) -> str:
        # Not implemented
        pass 
