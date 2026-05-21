from langchain_ollama import OllamaLLM

#非流式输出
# model=OllamaLLM(model="qwen2.5:3b")
#
# res = model.invoke("请用中文回答：1+1是多少？")
#
# print(res)

#流式输出
model = OllamaLLM(model="qwen2.5:3b")

res=model.stream(input="你是谁，可以帮我干什么？",stream=True)
for chunk in res:
    print(chunk, end="",flush= True)