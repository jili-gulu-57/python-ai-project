import langchain_community,os
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import CSVLoader

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

vector_store=InMemoryVectorStore(
    embedding=embedding
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

vector_store.delete(["id1"])

result=vector_store.similarity_search(
    "Python作业应该怎么提交？",
    k=2
)

print(result)