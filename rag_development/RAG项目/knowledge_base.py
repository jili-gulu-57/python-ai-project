import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import datetime
import config_data as config
import hashlib

def check_md5(md5_str:str):
    """检查传入的md5字符串是否已经被处理过"""
    if not os.path.exists(config.md5_path):
        open(config.md5_path,"w",encoding="utf-8").close()
        return False
    else:
        for line in open(config.md5_path,"r",encoding="utf-8").readlines():
            if line.strip()==md5_str:
                return True

        return  False

def save_md5(md5_str):
    """将传入的md5字符串记录下来"""
    with open(config.md5_path,"a",encoding="utf-8") as f:
        f.write(md5_str+'\n')

def get_string_md5(input_str,encoding="utf-8"):
    """获取传入字符串的md5"""
    str_bytes=input_str.encode(encoding=encoding)

    md5_obj=hashlib.md5()
    md5_obj.update(str_bytes)
    md5_hex=md5_obj.hexdigest()
    return md5_hex

class KnowledgeBaseService:
    def __init__(self):
        self.embedding = OpenAIEmbeddings(
            model="text-embedding-v4",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
            dimensions=1024,
            encoding_format="float",
            chunk_size=10,
            check_embedding_ctx_length=False
        )
        os.makedirs(config.persist_directory,exist_ok=True)

        self.chroma=Chroma(
            collection_name=config.collection_name,
            embedding_function=self.embedding,
            persist_directory=config.persist_directory
        )
        self.spliter=RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=config.separators,
            length_function=len
        )

    def upload_by_str(self,data:str,filename,force:bool=False):
        """将传入的字符串进行向量化，并存入向量数据库中"""
        md5_hex=get_string_md5(data)
        md5_exists=check_md5(md5_hex)
        if md5_exists and not force:
            return "数据已存在，无需重复添加"

        if len(data)>config.min_split_char_number:
            knowledge_chunks=self.spliter.split_text(data)
        else:
            knowledge_chunks=[data]

        metadata={
            "source":filename,
            "create_time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator":"Qiii"
        }

        self.chroma.add_texts(
            knowledge_chunks,
            metadatas=[metadata for _ in knowledge_chunks]
        )
        if not md5_exists:
            save_md5(md5_hex)
        return "文件上传成功"

if __name__=="__main__":
    r1=get_string_md5("你好")
    r2=get_string_md5("你好")
    r3=get_string_md5("你好1")

    print(r1)
    print(r2)
    print(r3)
    print(check_md5(r1))
    print(check_md5(r2))
    print(check_md5(r3))