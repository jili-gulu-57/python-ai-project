#配置环境变量
from zipp.glob import separate

md5_path="./md5.txt"

#Chroma
collection_name="rag"
persist_directory="./chroma_db"

#spliter
chunk_size=1000
chunk_overlap=100
separators=["\n\n", "\n", ".", "!", "?"," ",","]
min_split_char_number=1000  #文本分割起始值

#文档检索
similarity_threshold=2

embedding_model="text-embedding-v4"
chat_model="qwen-max"

session_config = {
    "configurable": {
        "session_id": "user_001"
    }
}




