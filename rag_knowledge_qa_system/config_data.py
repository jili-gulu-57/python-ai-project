md5_path = "./md5.txt"

# Chroma vector database
collection_name = "rag"
persist_directory = "./chroma_db"

# Text splitter
chunk_size = 1000
chunk_overlap = 100
separators = ["\n\n", "\n", ".", "!", "?", " ", ","]
min_split_char_number = 1000

# Retriever
retriever_k = 4

# Models
embedding_model = "text-embedding-v4"
chat_model = "qwen-max"

session_config = {
    "configurable": {
        "session_id": "user_001",
    }
}
