import os
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

model=ChatOpenAI(
    model="qwen-max",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
)

parser=StrOutputParser()#字符串解析器，将AIMessage类型转换为str类型，做为输入参数给model

prompt=PromptTemplate.from_template(
    "我的姓名缩写是：{name}，请按照这个格式{moral}，帮我起个网民，并解释含义。"
)
# chain=prompt | model | model
chain=prompt | model|parser|model

res=chain.invoke({"name":"WQ","moral":"Zenith Zenith Crown (ZZC)，寄语：巅峰之上，冠冕璀璨"})

print(res.content)







