import os
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_openai import ChatOpenAI

# 提示词模板
chat_prompt_template=ChatPromptTemplate.from_messages([
    ("system","你是像李清照一样有才情的诗词家"),
    MessagesPlaceholder("history"),
    ("human","再创作一首")
])

history_data=[
    ("human","来做一首词"),
    ("ai","寻寻觅觅冷冷清清，凄凄惨惨戚戚"),
    ("human","好词，再创作一首")
]

model=ChatOpenAI(
    model="qwen-max",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
)

chain=chat_prompt_template | model

res=chain.invoke({"history":history_data})

print(res.content)