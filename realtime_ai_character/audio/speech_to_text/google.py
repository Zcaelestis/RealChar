#使用Goolge Cloud 语音识别,将语音转换为文本
#导入相关库和模块
from google.cloud import speech # 导入google.cloud模块中的speech库
import types                    # 导入types模块

from realtime_ai_character.audio.speech_to_text.base import SpeechToText     #从base.py中导入SpeechToText类
from realtime_ai_character.logger import get_logger                          #日志
from realtime_ai_character.utils import Singleton, timed                     # 导入 Singleton 和 timed 装饰器

logger = get_logger(__name__) #创建logger对象,用于记录日志

#定义配置，包含 'web' 和 'terminal' 两个平台的配置信息，如编码格式、采样率等
config = types.SimpleNamespace(**{
    'web': {
        'encoding': speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
        'sample_rate_hertz': 48000,
        'language_code': 'en-US',
        'max_alternatives': 1,
        'enable_automatic_punctuation': True,
    },
    'terminal': {
        'encoding': speech.RecognitionConfig.AudioEncoding.LINEAR16,
        'sample_rate_hertz': 44100,
        'language_code': 'en-US',
        'max_alternatives': 1,
        'enable_automatic_punctuation': True,
    },
})

#定义Google类,继承SpeechToText类,重写transcribe方法
class Google(Singleton, SpeechToText): 
    def __init__(self):
        super().__init__()
        logger.info("Setting up [Google Speech to Text]...")
        self.client = speech.SpeechClient()  

    @timed 
    #定义transcribe 方法 根据平台和其他参数配置语音识别
    def transcribe(
        self, audio_bytes, platform, prompt="", language="en-US", suppress_tokens=[-1]
    ) -> str: #
        batch_config = speech.RecognitionConfig({
            'speech_contexts': [speech.SpeechContext(phrases=prompt.split(','))],
            **config.__dict__[platform]})
        batch_config.language_code = language
        if language != 'en-US': 
            batch_config.alternative_language_codes = ['en-US'] #如果指定的语言不是美式英文，那么将美式英文设置为备选语言
        response = self.client.recognize(
            config=batch_config,
            audio=speech.RecognitionAudio(content=audio_bytes)
        )                                                       #调用将语音转换为文本的API,返回结果 
        if not response.results:
            return ''                                               #如果没有结果，返回空字符串
        result = response.results[0]
        if not result.alternatives:
            return ''
        return result.alternatives[0].transcript
