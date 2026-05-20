import os
from langchain_community.llms.tongyi import Tongyi
from langchain_openai import ChatOpenAI

# model=Tongyi(model="qwen-max")
#
# res=model.invoke(input="请用中文回答：1+1是多少？")
#
# print(res)

# import os
# from langchain_community.llms.tongyi import Tongyi
#
# model = Tongyi(
#     model="qwen-max",
#     dashscope_api_key=os.getenv("DASHSCOPE_API_KEY")
# )
#
# res = model.invoke("1+1等于几")
#
# print(res)

# import os
#
# print(os.getenv("DASHSCOPE_API_KEY"))



#非流式输出

# model = ChatOpenAI(
#     model="qwen-max",
#     api_key=os.getenv("DASHSCOPE_API_KEY"),
#     base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
# )
#
# res = model.invoke("请用中文回答：1+1是多少？")
#
# print(res.content)

#流式输出
model=Tongyi(model="qwen-max")

res=model.invoke(input="请用中文回答：1+1是多少？")

for chunk in res:
    print(chunk.content, end="",flush=True)