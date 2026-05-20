import os

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda

model=ChatOpenAI(
    model="qwen-max",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
)

strparser=StrOutputParser()

first_prompt=PromptTemplate.from_template(
    "我的姓名缩写是：{name}，请按照这个格式{moral}，帮我起个网名，仅返回网名"
)

second_prompt=PromptTemplate.from_template(
    "网名：{name}，请帮我解析含义"
)

my_func=RunnableLambda(lambda ai_msg:{"name":ai_msg.content})

chain=first_prompt|model|my_func|second_prompt|model|strparser

res=chain.invoke({"name":"WQ","moral":"Zenith Zenith Crown (ZZC)，寄语：巅峰之上，冠冕璀璨"})

print(res)