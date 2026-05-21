import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

import config_data as config
from file_history_store import get_history
from vector_stores import VectorStoreService


class RagService:
    """Knowledge-base QA service with multi-turn, history-aware retrieval."""

    def __init__(self):
        self.vector_store_service = VectorStoreService(
            embedding=OpenAIEmbeddings(
                model=config.embedding_model,
                api_key=os.getenv("DASHSCOPE_API_KEY"),
                base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
                dimensions=1024,
                chunk_size=10,
                check_embedding_ctx_length=False,
            )
        )
        self.chat_model = ChatOpenAI(
            model=config.chat_model,
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
            temperature=0.1,
        )
        self.query_rewrite_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是企业知识库检索助手。请结合历史对话，把用户最新问题改写成一个"
                    "完整、明确、适合向量检索的中文问题。只输出改写后的问题，不要解释。",
                ),
                MessagesPlaceholder("history"),
                ("user", "{input}"),
            ]
        )
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是企业知识库多轮问答助手。你必须优先根据参考资料回答用户问题，"
                    "不要凭空编造。如果资料不足，请明确说明知识库中没有检索到足够依据。",
                ),
                (
                    "system",
                    "回答要求：\n"
                    "1. 先给出直接结论；\n"
                    "2. 需要时分点说明；\n"
                    "3. 如果参考资料包含来源，请在回答末尾列出参考来源；\n"
                    "4. 历史对话只用于理解上下文，不能替代知识库资料。",
                ),
                ("system", "参考资料：\n{context}"),
                MessagesPlaceholder("history"),
                ("user", "{input}"),
            ]
        )
        self.chain = self.__get_chain()

    def rewrite_query(self, question: str, session_id: str = "user_001") -> str:
        """Rewrite a follow-up question by using the stored conversation history."""
        history = get_history(session_id).messages
        if not history:
            return question

        rewrite_chain = self.query_rewrite_prompt | self.chat_model | StrOutputParser()
        return rewrite_chain.invoke({"input": question, "history": history[-8:]})

    def retrieve_documents(self, query: str):
        """Query the vector database for UI preview or debugging."""
        retriever = self.vector_store_service.get_retriever()
        return retriever.invoke(query)

    def __get_chain(self):
        retriever = self.vector_store_service.get_retriever()

        def format_documents(docs):
            if not docs:
                return "无相关参考资料"

            formatted = []
            for index, doc in enumerate(docs, start=1):
                source = doc.metadata.get("source", "未知来源")
                formatted.append(
                    f"[资料{index}] 来源：{source}\n{doc.page_content}"
                )
            return "\n\n".join(formatted)

        def build_retrieval_query(value: dict) -> str:
            history = value.get("history", [])
            question = value["input"]
            if not history:
                return question

            rewrite_chain = self.query_rewrite_prompt | self.chat_model | StrOutputParser()
            return rewrite_chain.invoke({"input": question, "history": history[-8:]})

        def format_for_prompt(value):
            return {
                "input": value["input"]["input"],
                "history": value["input"]["history"],
                "context": value["context"],
            }

        chain = (
            {
                "input": RunnablePassthrough(),
                "context": RunnableLambda(build_retrieval_query)
                | retriever
                | format_documents,
            }
            | RunnableLambda(format_for_prompt)
            | self.prompt_template
            | self.chat_model
            | StrOutputParser()
        )

        return RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history",
        )


if __name__ == "__main__":
    session_config = {"configurable": {"session_id": "user_001"}}
    result = RagService().chain.invoke(
        {"input": "什么时候可以去图书馆借书"},
        session_config,
    )
    print(result)
