import os
from openai import OpenAI

# 注意: 不同地域的base_url不通用（下方示例使用新加坡地域的base_url）
# - 新加坡: https://dashscope-intl.aliyuncs.com/compatible-mode/v1
# - 美国（弗吉尼亚）: https://dashscope-us.aliyuncs.com/compatible-mode/v1
# - 中国北京: https://dashscope.aliyuncs.com/compatible-mode/v1
# - 中国香港：https://cn-hongkong.dashscope.aliyuncs.com/compatible-mode/v1
# - 德国（法兰克福）: https://{WorkspaceId}.eu-central-1.maas.aliyuncs.com/compatible-mode/v1，请将WorkspaceId替换为业务空间ID
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
)
completion = client.chat.completions.create(
    model="qwen3.6-plus",
    messages=[{"role":"assistant","content":"你是一个可靠的ai助理，回答用户的问题，涉及到不会的请诚实告知，不要胡编乱造"},
        {"role": "user", "content": "你是谁？"}
    ],
    stream=True
)
for chunk in completion:
    print(chunk.choices[0].delta.content, end="",flush= True)

# print(completion.choices[0].message.content)