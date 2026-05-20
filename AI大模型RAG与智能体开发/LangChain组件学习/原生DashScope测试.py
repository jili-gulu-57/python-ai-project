import os
import dashscope

dashscope.base_http_api_url = "https://dashscope-intl.aliyuncs.com/api/v1"

dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

response = dashscope.Generation.call(
    model="qwen-plus",
    prompt="你好"
)

print(response)