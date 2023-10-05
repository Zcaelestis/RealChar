import os 
from functools import cache  # 缓存函数的返回值,避免重复计算

from langchain.chat_models.base import BaseChatModel # 从base.py中导入BaseChatModel类

from realtime_ai_character.llm.base import LLM # realtime_ai_character.llm.base module中导入LLM类语言模型

# 从环境变量中获取llm模型,并根据model的值,选择使用哪个llm模型
def get_llm(model="gpt-3.5-turbo-16k") -> LLM: 

    # checking if model starts with 'gpt',then use OpenaiLlm;if model starts with 'claude',then use AnthropicLlm; 
    # if model contains 'localhost',then use LocalLlm; if model contains 'llama',then use AnysacleLlm,else raise ValueError

    if model.startswith('gpt'): 
        from realtime_ai_character.llm.openai_llm import OpenaiLlm # 从openai_llm.py中导入OpenaiLlm类
        return OpenaiLlm(model=model) # 返回一个OpenaiLlm的实例
    elif model.startswith('claude'):   # 如果model以claude开头,则使用AnthropicLlm 
        from realtime_ai_character.llm.anthropic_llm import AnthropicLlm # 从anthropic_llm.py中导入AnthropicLlm类
        return AnthropicLlm(model=model) # 返回一个AnthropicLlm的实例
    elif "localhost" in model:
        # Currently use llama2-wrapper to run local llama models
        local_llm_url = os.getenv('LOCAL_LLM_URL', '')
        if local_llm_url:
            from realtime_ai_character.llm.local_llm import LocalLlm
            return LocalLlm(url=local_llm_url)
        else:
            raise ValueError('LOCAL_LLM_URL not set')
    elif "llama" in model:
        # Currently use Anyscale to support llama models
        from realtime_ai_character.llm.anyscale_llm import AnysacleLlm
        return AnysacleLlm(model=model)
    else:
        raise ValueError(f'Invalid llm model: {model}')


@cache # 缓存函数的返回值,避免重复计算
# 定义了get_chatmodel_from_env()函数,返回BaseChatModel instance基于环境变量中的llm模型,以实现对话功能
def get_chatmodel_from_env() -> BaseChatModel: # Checking if environment variables are set,then use the corresponding llm model
    """GPT-4 has the best performance while generating system prompt.""" 
    if os.getenv('OPENAI_API_KEY'):                # chat_open_ai of the LLM instance
        return get_llm(model='gpt-4').chat_open_ai # returned by get_llm function with 'gpt-4' model name
    elif os.getenv('ANTHROPIC_API_KEY'):            # chat_anthropic of the LLM instance
        return get_llm(model='claude-2').chat_anthropic # returned by get_llm function with 'claude-2' model name
    elif os.getenv('ANYSCALE_API_KEY'):             # chat_anyscale of the LLM instance
        return get_llm(model='meta-llama/Llama-2-70b-chat-hf').chat_open_ai
    elif os.getenv('LOCAL_LLM_URL'):                # chat_open_ai of the LLM instance
        return get_llm(model=os.getenv('LOCAL_LLM_URL')).chat_open_ai  # returned by get_llm function with 'LOCAL_LLM_URL' model name
    raise ValueError('No llm api key found in env')  # if no llm api key found in env,raise ValueError
