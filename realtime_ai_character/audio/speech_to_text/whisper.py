import io
import os
import types
import wave

import speech_recognition as sr
from faster_whisper import WhisperModel
from pydub import AudioSegment
from torch.cuda import is_available as is_cuda_available

from realtime_ai_character.audio.speech_to_text.base import SpeechToText
from realtime_ai_character.logger import get_logger
from realtime_ai_character.utils import Singleton, timed

DEBUG = False

logger = get_logger(__name__)

config = types.SimpleNamespace(**{
    'model': os.getenv("LOCAL_WHISPER_MODEL", "base"),
    'language': 'en',
    'api_key': os.getenv("OPENAI_API_KEY"),
})

# Whisper use a shorter version for language code. Provide a mapping to convert
# from the standard language code to the whisper language code.
WHISPER_LANGUAGE_CODE_MAPPING = {
    "en-US": "en",
    "es-ES": "es",
    "fr-FR": "fr",
    "de-DE": "de",
    "it-IT": "it",
    "pt-PT": "pt",
    "hi-IN": "hi",
    "pl-PL": "pl",
    'zh-CN': 'zh',
    'ja-JP': 'jp',
    'ko-KR': 'ko',
}

# 创建一个class to transcribe speech to text using the Whisper model.
class Whisper(Singleton, SpeechToText): 
    
    def __init__(self, use="local"):  # 初始化函数，参数use表示使用local
        super().__init__()
                                      
        if use == "local":             # 如果使用本地模型，则加载local模型
                                        
            device = 'cuda' if is_cuda_available() else 'cpu'  # 判断是否可以使用cuda,可以则使用cuda，否则用cpu
            logger.info(f"Loading [Local Whisper] model: [{config.model}]({device}) ...") # 记录日志
            self.model = WhisperModel(                                                      #load model
                model_size_or_path=config.model,
                device="auto",
                download_root=None,
            )                                                   
                                                             
        self.recognizer = sr.Recognizer()      # 初始化语音识别器 speech_recognition库中的 Recognizer 类，用于语音识别
        self.use = use                           # use which model:local or api
        
        if DEBUG:                                   # 如果是debug模式
            self.wf = wave.open("output.wav", "wb")
            self.wf.setnchannels(1)                     # Assuming mono audio
            self.wf.setsampwidth(2)                     # Assuming 16-bit audio
            self.wf.setframerate(44100)                 # Assuming 44100Hz sample rate

    @timed # 纪录运行时间
    # 定义transcribe方法，将语音转为文本,参数有 audio_bytes转录的语音数据的字节, platform默认的平台是web, prompt提示,默认空, 
    # language默认的语言是en-US suppress_tokens: a list of tokens to suppress from the transcription;
   
    def transcribe(self, audio_bytes, platform, prompt="", language="en-US", suppress_tokens=[-1]):
        logger.info("Transcribing audio...") # 记录日志
        if platform == "web": # web平台
            audio = self._convert_webm_to_wav(audio_bytes, self.use == "local") # 将webm格式的音频转换为wav格式
        else: 
            audio = self._convert_bytes_to_wav(audio_bytes, self.use == "local") 
        if self.use == "local": # local模式
            return self._transcribe(audio, prompt, suppress_tokens=suppress_tokens) # transcribe Audio using local model
        elif self.use == "api": # api模式
            return self._transcribe_api(audio, prompt) # transcribe Audio using API

#transcribe Audio using local whisper model,参数有 audio转录的语音数据, prompt提示,默认空, language默认的语言是en-US 
# suppress_tokens: a list of tokens to suppress from the transcription; return:转成文本
    def _transcribe(self, audio, prompt="", language="en-US", suppress_tokens=[-1]):
        language = WHISPER_LANGUAGE_CODE_MAPPING.get(language, config.language)
        segs, _ = self.model.transcribe(
            audio,
            language=language,
            vad_filter=True,
            initial_prompt=prompt,
            suppress_tokens=suppress_tokens,
        )  
        text = " ".join([seg.text for seg in segs])
        return text
# transcribe Audio using Whisper API,参数有 audio转录的语音数据, prompt提示,默认空, return:转成文本
    def _transcribe_api(self, audio, prompt=""):
        text = self.recognizer.recognize_whisper_api(
            audio,
            api_key=config.api_key,
        )
        return text
# 将webm转成wav格式,参数有 webm格式音频, local,bool:whether return audio as bytes or audio, return:wav格式音频或audio
    def _convert_webm_to_wav(self, webm_data, local=True):
        webm_audio = AudioSegment.from_file(io.BytesIO(webm_data), format="webm")
        wav_data = io.BytesIO() # 创建一个BytesIO对象
        webm_audio.export(wav_data, format="wav") # 将webm格式的音频转换为wav格式
        if local: 
            return wav_data
        with sr.AudioFile(wav_data) as source:  # 记录音频
            audio = self.recognizer.record(source)  
        return audio 
#将bytes转换为wav格式,参数有 audio_bytes转录的语音数据, return:wav格式的音频
    def _convert_bytes_to_wav(self, audio_bytes, local=True):
        if local:
            audio = io.BytesIO(sr.AudioData(audio_bytes, 44100, 2).get_wav_data()) 
            return audio
        return sr.AudioData(audio_bytes, 44100, 2) # 创建一个AudioData对象