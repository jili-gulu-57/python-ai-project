import langchain_community,os
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import CSVLoader
from langchain_chroma import Chroma


# print(os.getenv("DASHSCOPE_API_KEY"))

# embedding = OpenAIEmbeddings(
#     model="text-embedding-v4",
#     api_key=os.getenv("DASHSCOPE_API_KEY"),
#     base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
# )

embedding = OpenAIEmbeddings(
    model="text-embedding-v4",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    dimensions=1024,
    encoding_format="float",
    chunk_size=10,
    check_embedding_ctx_length=False
)

vector_store = Chroma(
    collection_name="school_faq",
    embedding_function=embedding,
    persist_directory="./chroma_db"
)

loader=CSVLoader(
    file_path="data/school_faq.csv",
    encoding="utf-8",
    csv_args={
        "delimiter":","
    }
)

documents=loader.load()

vector_store.add_documents(
    documents= documents,
    ids=["id"+str(i) for i in range(len(documents))]
)

# vector_store.delete(["id1"])

result=vector_store.similarity_search(
    "人工智能导论课程什么时候上课",
    k=2
)

print(result)