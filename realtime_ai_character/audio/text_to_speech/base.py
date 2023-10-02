from abc import ABC, abstractmethod #导入 abc 模块中的Abstract Base Class module,抽象基类模块
from realtime_ai_character.utils import timed #从realtime_ai_character.utils中导入timed decorator

#定义ABC for TextToSpeech功能,子类继承时重写方法
# 定义TextToSpeech类，该类是抽象类，用于生成音频
class TextToSpeech(ABC): 
    
    # 定义一个抽象方法，用于 streaming aduio and generate aduio
    @abstractmethod
    @timed
    async def stream(self, *args, **kwargs): 
        pass

    async def generate_audio(self,  *args, **kwargs):
        pass
