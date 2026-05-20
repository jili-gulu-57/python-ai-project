import os

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI

model=ChatOpenAI(
    model="qwen-max",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
)

strparser=StrOutputParser()
jsonparser=JsonOutputParser()

first_prompt=PromptTemplate.from_template(
    "我的姓名缩写是：{name}，请按照这个格式{moral}，帮我起个网名，并解释含义,封装成JSON格式返回，要求key是name，value是moral。"
)

second_prompt=PromptTemplate.from_template(
    "网名：{name}，请帮我解析含义"
)

chain=first_prompt|model|jsonparser|second_prompt|model|strparser

res=chain.invoke({"name":"WQ","moral":"Zenith Zenith Crown (ZZC)，寄语：巅峰之上，冠冕璀璨"})

print(res)