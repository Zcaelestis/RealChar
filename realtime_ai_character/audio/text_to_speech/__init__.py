import os

from realtime_ai_character.audio.text_to_speech.base import TextToSpeech # 从base.py中导入TextToSpeech类

#定义了get_text_to_speech()函数,返回TextToSpeech的实例,以获取文本转语音的功能,tts参数指定使用哪个引擎
def get_text_to_speech(tts: str = None) -> TextToSpeech:
    if not tts: #如果没有tts,check TEXT_TO_SPEECH_USE 环境变量,默认为ELEVEN_LABS
        tts = os.getenv('TEXT_TO_SPEECH_USE', 'ELEVEN_LABS')
    if tts == 'ELEVEN_LABS': #如果使用ELEVEN_LABS,导入并初始化ELEVEN_LABS,返回一个ELEVEN_LABS的实例
        from realtime_ai_character.audio.text_to_speech.elevenlabs import ElevenLabs
        ElevenLabs.initialize()
        return ElevenLabs.get_instance()
    elif tts == 'GOOGLE_TTS': #如果使用GOOGLE_TTS,导入并初始化GOOGLE_TTS,返回一个GOOGLE_TTS的实例
        from realtime_ai_character.audio.text_to_speech.google_cloud_tts import GoogleCloudTTS
        GoogleCloudTTS.initialize()
        return GoogleCloudTTS.get_instance()
    elif tts == 'UNREAL_SPEECH': #如果使用UNREAL_SPEECH,导入并初始化UNREAL_SPEECH,返回一个UNREAL_SPEECH的实例
        from realtime_ai_character.audio.text_to_speech.unreal_speech import UnrealSpeech
        UnrealSpeech.initialize()
        return UnrealSpeech.get_instance()
    elif tts == 'EDGE_TTS': #如果使用EDGE_TTS,导入并初始化EDGE_TTS,返回一个EDGE_TTS的实例
        from realtime_ai_character.audio.text_to_speech.edge_tts import EdgeTTS
        EdgeTTS.initialize()
        return EdgeTTS.get_instance()
    else: #如果使用的文本转语音引擎不是上面四种,则返回"Unknown text to speech engine"
        raise NotImplementedError(f'Unknown text to speech engine: {tts}')
