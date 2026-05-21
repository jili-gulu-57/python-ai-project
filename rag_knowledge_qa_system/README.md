# 企业知识库多轮智能问答系统

这是最新版整合项目，将「RAG 智能问答服务」和「AI 多轮聊天对话服务」合并为一个可运行的 Streamlit 应用。

## 功能

- 上传 `.txt`、`.md`、`.csv` 知识文件
- 文本切分、Embedding、写入 Chroma 向量库
- 支持多轮会话和历史会话管理
- 支持 Query Rewrite，解决追问、省略、指代导致的检索不准
- 支持 RAG 知识库问答和普通聊天双模式
- 支持查看本轮检索问题和召回片段
- 修复只看 `md5.txt` 导致“显示已写入但向量库无内容”的问题

## 目录说明

```text
app.py                  # Streamlit 主入口
rag.py                  # 多轮 RAG 问答链路
knowledge_base.py       # 知识库上传、切分、向量化、去重
vector_stores.py        # Chroma 检索器
file_history_store.py   # LangChain 会话历史
config_data.py          # 模型、向量库、切分参数
requirements.txt        # 运行依赖
md5.txt                 # 文件去重记录，初始为空
demo_data/测试.txt       # 演示知识文件
```

## 启动

```powershell
cd "C:\Users\22632\Desktop\项目与简历\企业知识库多轮智能问答系统_最新版"
python -m pip install -r requirements.txt
$env:DASHSCOPE_API_KEY="你的 API Key"
streamlit run app.py
```

## 演示流程

1. 启动应用。
2. 左侧上传 `demo_data/测试.txt`。
3. 点击「写入知识库」。
4. 在聊天框提问，例如“图书馆什么时候开放”。
5. 展开「本轮检索详情」，查看改写后的检索问题和召回片段。
