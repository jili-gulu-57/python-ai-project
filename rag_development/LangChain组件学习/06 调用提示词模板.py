from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from openai import OpenAI
import os

# 示例模板
example_template = PromptTemplate.from_template(
    "单词:{word},反义词:{antonym}"
)

# 示例数据
example_data = [
    {"word": "good", "antonym": "bad"},
    {"word": "happy", "antonym": "sad"},
    {"word": "大", "antonym": "小"},
    {"word": "高", "antonym": "低"}
]
 
# Few Shot 模板
few_shot_template = FewShotPromptTemplate(
    example_prompt=example_template,
    examples=example_data,
    prefix="请给出单词的相反词，提供如下示例：",
    suffix="基于前面的示例，请给出单词的相反词：{input}",
    input_variables=["input"]
)

# 创建 OpenAI 客户端（新加坡节点）
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
)

# 用户输入
user_input = input("请输入单词：")

# 生成 Prompt
prompt_value = few_shot_template.invoke({"input": user_input})
prompt_text = prompt_value.to_string()

# 调用模型
response = client.chat.completions.create(
    model="qwen-plus",
    messages=[
        {
            "role": "user",
            "content": prompt_text
        }
    ]
)

# 输出结果
print(response.choices[0].message.content)