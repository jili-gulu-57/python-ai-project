from langchain_classic.chains.question_answering.map_reduce_prompt import messages
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import HumanMessage,AIMessage,SystemMessage
from langchain_ollama import ChatOllama
import os

# print(os.getenv("DASHSCOPE_API_KEY"))

#key是国际站新加坡区域的，tongyi默认请求国内的
# model=ChatTongyi(model="qwen3-max")
#
# messages=[
#     SystemMessage(content="你是一个宋朝诗词家"),
#     HumanMessage(content="创作一首词，词牌名为清平乐")
# ]
#
# res=model.stream(input=messages)
# for chunk in res:
#     print(chunk.content,end="",flush=True)

import os
from openai import OpenAI

#云端模型
# client = OpenAI(
#     api_key=os.getenv("DASHSCOPE_API_KEY").strip(),
#     base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
# )
#
# completion = client.chat.completions.create(
#     model="qwen-max",
#     messages=[
#         {"role": "system", "content": "你是一个宋朝诗词家"},
#         {"role": "user", "content": "创作一首词，词牌名为清平乐"}
#     ],
#     stream=True
# )
#
# for chunk in completion:
#     content = chunk.choices[0].delta.content
#     if content:
#         print(content, end="", flush=True)

#本地模型
model=ChatOllama(model="qwen2.5:3b")

messages=[
    SystemMessage(content="你是一个宋朝诗词家"),
    HumanMessage(content="创作一首词，词牌名为清平乐，主题与春日有关")
]

res=model.stream(input=messages)

for chunk in res:
    print(chunk.content,end="",flush=True)