import os
from abc import ABC, abstractmethod #导入 abc 模块中的Abstract Base Class module,抽象基类模块
import requests 
import multion
import asyncio


from langchain.callbacks.base import AsyncCallbackHandler 
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.utilities import GoogleSerperAPIWrapper, SerpAPIWrapper, GoogleSearchAPIWrapper #导入与google搜索相关的apiwrapper

from realtime_ai_character.logger import get_logger
from realtime_ai_character.utils import get_timer, timed

logger = get_logger(__name__) # 记录日志

timer = get_timer()           # 记录时间
# 定义了语言模型的接口,项目中使用的任何语言模型都必须使用该语言模型方法。
StreamingStdOutCallbackHandler.on_chat_model_start = lambda *args, **kwargs: None 

# class AsyncCallbackTextHandler处理基于文本语言模型的回调函数,继承了StreamingStdOutCallbackHandler
class AsyncCallbackTextHandler(AsyncCallbackHandler):
   
 def __init__(self, on_new_token=None, token_buffer=None, on_llm_end=None, *args, **kwargs): 
        super().__init__(*args, **kwargs)   #调用父类的初始化函数
        self.on_new_token = on_new_token    #设置了on_new_token
        self._on_llm_end = on_llm_end       #设置了_on_llm_end 
        self.token_buffer = token_buffer    #设置了token_buffer

    # 定义了on_chat_model_start 异步函数,参数有*args, **kwargs. 
    async def on_chat_model_start(self, *args, **kwargs):
        pass #抽象类用来继承,不用来实例化,所以这里pass

    async def on_llm_new_token(self, token: str, *args, **kwargs): #定义了on_llm_new_token 异步函数,接收新token
        if self.token_buffer is not None:   #如果token_buffer不为空
            self.token_buffer.append(token) #将token添加到token_buffer中
        await self.on_new_token(token)      #调用on_new_token函数

    async def on_llm_end(self, *args, **kwargs):               #定义了on_llm_end 异步函数,结束
        if self._on_llm_end is not None:                       #如果_on_llm_end不为空
            await self._on_llm_end(''.join(self.token_buffer)) #将token_buffer中的token连接起来
            self.token_buffer.clear()                           #清空token_buffer

# Class AsyncCallbackAudioHandler处理基于音频语言模型的回调函数,继承了AsyncCallbackHandler
class AsyncCallbackAudioHandler(AsyncCallbackHandler): 
    
    def __init__(self, text_to_speech=None, websocket=None, tts_event=None, voice_id="",
                 language="en-US", *args, **kwargs):
        super().__init__(*args, **kwargs)
        if text_to_speech is None:
            def text_to_speech(token): return print(
                f'New audio token: {token}')
        self.text_to_speech = text_to_speech
        self.websocket = websocket
        self.current_sentence = ""
        self.voice_id = voice_id
        self.language = language
        self.is_reply = False  # the start of the reply. i.e. the substring after '>'
        self.tts_event = tts_event
        # optimization: trade off between latency and quality for the first sentence
        self.is_first_sentence = True

    async def on_chat_model_start(self, *args, **kwargs):
        pass

    async def on_llm_new_token(self, token: str, *args, **kwargs):
        timer.log("LLM First Token", lambda: timer.start("LLM First Sentence"))
        if (
            not self.is_reply and ">" in token
        ):  # small models might not give ">" (e.g. llama2-7b gives ">:" as a token)
            self.is_reply = True
        elif self.is_reply:
            if token not in {'.', '?', '!'}:
                self.current_sentence += token
            else:
                if self.is_first_sentence:
                    timer.log("LLM First Sentence", lambda: timer.start("TTS First Sentence"))
                await self.text_to_speech.stream(
                    self.current_sentence,
                    self.websocket,
                    self.tts_event,
                    self.voice_id,
                    self.is_first_sentence,
                    self.language)
                self.current_sentence = ""
                if self.is_first_sentence:
                    self.is_first_sentence = False
                timer.log("TTS First Sentence")

    async def on_llm_end(self, *args, **kwargs):
        if self.current_sentence != "":
            await self.text_to_speech.stream(
                self.current_sentence,
                self.websocket,
                self.tts_event,
                self.voice_id,
                self.is_first_sentence,
                self.language)
# SearchAgent类,用于搜索,根据环境变量中的APIKEY选择搜索方式
class SearchAgent:

    def __init__(self):
        self.search_wrapper = None
        if os.getenv('SERPER_API_KEY'):
            self.search_wrapper = GoogleSerperAPIWrapper()
        elif os.getenv('SERPAPI_API_KEY'):
            self.search_wrapper = SerpAPIWrapper()
        elif os.getenv('GOOGLE_API_KEY') and os.getenv('GOOGLE_CSE_ID'):
            self.search_wrapper = GoogleSearchAPIWrapper()
    
    def search(self, query: str) -> str:
        if self.search_wrapper is None:
            logger.warning('Search is not enabled, please set SERPER_API_KEY to enable it.')
        else:
            try:
                search_result: str = self.search_wrapper.run(query)
                search_context = '\n'.join([
                    '---',
                    'Internet search result:',
                    '---',
                    'Question: ' + query,
                    'Search Result: ' + search_result,
                ])
                logger.info(f'Search result: {search_context}')
                # Append to context
                return '\n' + search_context
            except Exception as e:
                logger.error(f'Error when searching: {e}')
        return ''
# QuivrAgent类,用于查询quivrAPI,可以接受query,apiKey,brainId三个参数,返回查询结果
class QuivrAgent:

    def __init__(self):
        pass

    def question(self, query: str, apiKey: str, brainId: str) -> str:
        try:
            url = f"https://api.quivr.app/brains/{brainId}/question_context"
            headers = {"Authorization": f"Bearer {apiKey}"}
            data = {
                "question": query,
            }

            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            quivr_result = response.json()["context"]

            quivr_context = '\n'.join([
                '---',
                'Second brain result:',
                '---',
                'Question: ' + query,
                'Query Result: ' + quivr_result,
            ])
            logger.info(f'Quvir query result: {quivr_context}')
            # Append to context
            return '\n' + quivr_context
        except Exception as e:
            logger.error(f'Error when querying quivr: {e}')
        return ''
#MulitOnAgent类,用于查询MultionAPI,可以接受query一个参数,返回查询结果
class MultiOnAgent:
    def __init__(self):
        self.init = False

    async def action(self, query: str) -> str:
        if not self.init:
            logger.info("Initializing multion agent...")
            multion.login()
            self.init = True
        try:
            await asyncio.wait_for(asyncio.to_thread(multion.new_session, {"input": query}),
                                   timeout=30)
            return ("This query has been handled by a MutliOn agent successfully. "
                    "The result has been delivered to the user. Do not try to complete this "
                    "request. Instead, inform user about the successful execution.")
        except Exception as e:
            logger.error(f'Error when querying multion: {e}')
            return ("The query was attempted by a MutliOn agent, but failed. Inform user about "
                    "this failure.")
#LLM类,用于语言模型,继承了ABC类,抽象基类,定义了接口以及方法:achat, get_config,其中achat方法用于对用户的相应,而get_config方法用于检索和获取语言模型配置
class LLM(ABC):
    @abstractmethod
    @timed
    async def achat(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_config(self):
        pass
