import os

from langchain_core.chat_history import InMemoryChatMessageHistory #导入内存聊天历史类
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.runnables.history import RunnableWithMessageHistory#给普通chain加上历史会话功能
#自动做：调用chain之前，把历史会话加入prompt里
#调用chain之后，把历史会话保存到内存历史记录里
#根据session_id区分不同会话

model=ChatOpenAI(
    model="qwen-max",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
)

#创建prompt模板
prompt=PromptTemplate.from_template(
    "你需要根据历史对话回应用户问题，对话历史:{chat_history},用户提问:{input}，请回答"
)

#创建输出解析器，把模型输出转换为字符串
str_parser=StrOutputParser()

def print_prompt(full_prompt):
    print("="*20,full_prompt.to_string(),"="*20)
    return full_prompt

base_chain=prompt|print_prompt|model|str_parser

store={}

def get_history(session_id):
    if session_id not in store:
        store[session_id]=InMemoryChatMessageHistory()

    return store[session_id]

conversion_chain=RunnableWithMessageHistory(
    base_chain,
    get_history,
    input_messages_key="input",
    history_messages_key="chat_history"
)

if __name__=='__main__':
    session_config={
        "configurable":{
            "session_id":"user_001"
        }
    }

    # res=conversion_chain.invoke({"input":"小明有两只猫"},session_config)
    # print("第一次执行：",res)
    #
    # res=conversion_chain.invoke({"input":"小红有两只狗"},session_config)
    # print("第二次执行：",res)

    res=conversion_chain.invoke({"input":"一共有几只宠物"},session_config)
    print("第三次执行：",res)


















