 #创建抽象基类,子类继承时重写方法.定义了语音到文本引擎的接口,项目中使用的任何语音到文本引擎都必须使用该转录方法。
from abc import ABC, abstractmethod # 导入 abc 模块中的Abstract Base Class 抽象基类
from realtime_ai_character.utils import timed # 导入实时AI角色的工具包中的 timed 装饰器


class SpeechToText(ABC): #定义 SpeechToText 抽象基类
    @abstractmethod # 方法是抽象的，子类必须重写。
    @timed # 用 timed 装饰器装饰这个方法，timed 装饰器会记录这个方法的运行时间
    def transcribe(
        self, audio_bytes, platform="web", prompt="", language="en-US", suppress_tokens=[-1]
    ) -> str:
         # 定义 transcribe方法，参数有 audio_bytes转录的语音数据的字节, platform默认的平台是web, prompt转录之前的字符串参数,默认空, language默认的语言是美式英语 suppress_tokens指定应该被忽略的，str函数返回转录后的文本

        # platform: 'web' | 'mobile' | 'terminal' # 平台: web/ mobile/terminal
       pass #抽象类用来继承,不用来实例化,所以这里pass
