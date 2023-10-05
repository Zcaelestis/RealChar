# 提供函数 get_speech_to_text()，返回 SpeechToText 的实例,以获取语音转文本的功能
import os # 用于获取环境变量

from realtime_ai_character.audio.speech_to_text.base import SpeechToText # 语音转文本的抽象基类,为 SpeechToText 的子类提供统一的接口


def get_speech_to_text() -> SpeechToText:# 返回 SpeechToText 的实例
    use = os.getenv('SPEECH_TO_TEXT_USE', 'LOCAL_WHISPER') # 获取环境变量 SPEECH_TO_TEXT_USE 的值,默认为 LOCAL_WHISPER
    # 通过环境变量 SPEECH_TO_TEXT_USE 的值,选择使用哪个语音转文本的引擎
    if use == 'GOOGLE': # 如果使用 Google 服务
        from realtime_ai_character.audio.speech_to_text.google import Google # 导入 Google 的语音转文字实现。
        Google.initialize() # 初始化 Google
        return Google.get_instance() #  返回 Google 服务的实例
    elif use == 'LOCAL_WHISPER': #如果使用本地 Whisper 服务
        from realtime_ai_character.audio.speech_to_text.whisper import Whisper # 导入 Whisper
        Whisper.initialize(use='local')
        return Whisper.get_instance() # 返回本地 Whisper 服务的实例
    elif use == 'OPENAI_WHISPER': # 如果使用 OpenAI 的 Whisper 服务
        from realtime_ai_character.audio.speech_to_text.whisper import Whisper # 导入 Whisper
        Whisper.initialize(use='api')# 初始化
        return Whisper.get_instance()# 返回OpenAI 的 Whisper 服务的实例
    else:
        raise NotImplementedError(f'Unknown speech to text engine: {use}') # 如果使用的语音转文本引擎不是上面三种,则异常
