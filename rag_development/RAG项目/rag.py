from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from file_history_store import get_history
import config_data as config
import os
from vector_stores import VectorStoreService
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI


class RagService:
    def __init__(self):
        self.vector_store_service = VectorStoreService(
            embedding=OpenAIEmbeddings(
                model=config.embedding_model,
                api_key=os.getenv("DASHSCOPE_API_KEY"),
                base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
                dimensions=1024,
                chunk_size=10,
                check_embedding_ctx_length=False
            )
        )
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system","你是知识库问答助手。只能根据参考资料回答用户问题，不要使用常识补充或编造。"),
                ("system","如果参考资料是“无相关参考资料”，或参考资料不足以回答问题，只回答：知识库中没有检索到相关内容，无法根据资料回答。"),
                ("system","参考资料：\n{context}"),
                ("system","历史对话记录如下，仅用于理解上下文，不能替代参考资料。"),
                MessagesPlaceholder("history"),
                ("user","{input}")
            ]
        )
        self.chat_model = ChatOpenAI(
            model=config.chat_model,
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
            temperature=0.1
        )
        self.chain=self.__get_chain()

    def retrieve_documents(self, query:str):
        """查询知识库，便于页面展示本次真正命中的资料。"""
        retriever = self.vector_store_service.get_retriever()
        return retriever.invoke(query)

    def __get_chain(self):
        """获取问答链"""
        retriever = self.vector_store_service.get_retriever()

        def format_documents(docs):
            """格式化文档"""
            if not docs:
                return "无相关参考资料"
            formatted_str=""
            for doc in docs:
                formatted_str+=doc.page_content+"\n"

            return formatted_str

        def format_for_retriever(value:dict)->str:
            return value["input"]

        def format_for_prompttemplate(value):
            new_value={}
            new_value["input"]=value["input"]["input"]
            new_value["context"]=value["context"]
            new_value["history"]=value["input"]["history"]
            return new_value

        chain=(
            {
                "input":RunnablePassthrough(),
                "context":RunnableLambda(format_for_retriever)|retriever|format_documents
            }
            | RunnableLambda(format_for_prompttemplate)
            | self.prompt_template
            | self.chat_model
            |StrOutputParser()
        )

        conversation_chain=RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history"
        )
        return conversation_chain

if __name__=="__main__":
    session_config={
        "configurable":{
            "session_id":"user_001"
        }
    }

    res=RagService().chain.invoke({"input":"什么时候可以去图书馆借书"},session_config)
    print(res)
