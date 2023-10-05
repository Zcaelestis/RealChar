import asyncio                      #导入了asyncio模块,异步网络操作model?
import edge_tts                     #导入edge_tts模块 可以用于处理文本
from edge_tts import VoicesManager  #从edge_tts模块中导入VoicesManager类,用于管理voices

from realtime_ai_character.logger import get_logger                               #导入get_logger函数,用于记录日志
from realtime_ai_character.utils import Singleton, timed                          #导入Singleton和timed decorator
from realtime_ai_character.audio.text_to_speech.base import TextToSpeech          #从base.py中导入TextToSpeech类

logger = get_logger(__name__)   #初始化logger对象,用于记录日志
DEBUG = False 


# 使用microsoft Edge TTS 的功能生成aduio,overall followings: stream() -> generate_audio(),
# 其中stream()方法用于生成streaming audio from text and send the audio to websocket, 
# generate_audio()方法用于generating audio from text and return as bytes. 同时依赖communicate class to handle TTS conversion.
class EdgeTTS(Singleton, TextToSpeech):
    def __init__(self):
        super().__init__() #call the parent class
        logger.info("Initializing [EdgeTTS] voices...") #

    @timed #timed decorator
    #定义了stream()方法,generating streaming audio from text and send the audio to websocket, 
    # Args: 
    # text 被转录数据, 
    # websocket: stream the aduio to websocket
    # tts_event: event to singal when geneation complete
    # voice_id: 语音id, 
    # first_sentence: 是否use a dif voice for the 1st sentence
    # language: text language.
    async def stream(self, text, websocket, tts_event: asyncio.Event, voice_id="",
                     first_sentence=False, language='en-US') -> None:
        if DEBUG:
            return   #如果是debug模式,直接返回
        # 创建一个instance of VoicesManager,用于管理voices,select a voice from voices based on Gender and Language
        voices = await VoicesManager.create()  
        voice = voices.find(Gender="Male", Language="en")[0] # 从voices中找到符合条件的voice
        
        # create a Communicate object from edge_tts,用于生成音频
        communicate = edge_tts.Communicate(text, voice["Name"]) 
        messages = [] # 创建一个空列表
        # 从communicate中获取message,如果message的type是audio,则将message的data添加到messages中
        async for message in communicate.stream():   
            if message["type"] == "audio":          
                # Choose to accmulate the audio data because
                # the stream packets are broken when playback.
                messages.extend(message["data"])     
        
        await websocket.send_bytes(bytes(messages))  # 将messages中的数据转换为bytes,并发送到websocket


    # 定义了generate_audio()方法,generating audio from text and return as bytes,
    # Args有text,voice_id,language
    async def generate_audio(self, text, voice_id = "", language='en-US') -> bytes: 
        voices = await VoicesManager.create()                   # 创建一个instance of VoicesManager,用于管理voices
        voice = voices.find(Gender="Male", Language="en")[0]    # 从voices中找到符合条件的voice
        communicate = edge_tts.Communicate(text, voice["Name"]) #set up a Communicate object from edge_tts
        messages = []
        async for message in communicate.stream():              # 从communicate中获取message,如果message的type是audio,则将message的data添加到messages中
                messages.extend(message["data"])
        return bytes(messages)                      # return the audio data as bytes

