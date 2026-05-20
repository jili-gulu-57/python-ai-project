import json
import os
from datetime import datetime
from pathlib import Path

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

APP_DIR = Path(__file__).resolve().parent
os.chdir(APP_DIR)

from knowledge_base import KnowledgeBaseService  # noqa: E402
from rag import RagService  # noqa: E402


SESSION_DIR = APP_DIR / "integrated_sessions"
CHAT_HISTORY_DIR = APP_DIR / "chat_history"


def generate_session_id() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def init_state():
    defaults = {
        "messages": [
            {
                "role": "assistant",
                "content": "你好，我是企业知识库智能助理。你可以先上传知识文件，再开始多轮提问。",
            }
        ],
        "current_session": generate_session_id(),
        "assistant_name": "知识库智能助理",
        "assistant_style": "专业、简洁、可靠",
        "mode": "知识库问答",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def save_session():
    SESSION_DIR.mkdir(exist_ok=True)
    data = {
        "current_session": st.session_state.current_session,
        "assistant_name": st.session_state.assistant_name,
        "assistant_style": st.session_state.assistant_style,
        "mode": st.session_state.mode,
        "messages": st.session_state.messages,
    }
    path = SESSION_DIR / f"{st.session_state.current_session}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_session_list():
    if not SESSION_DIR.exists():
        return []
    return sorted(
        [path.stem for path in SESSION_DIR.glob("*.json")],
        reverse=True,
    )


def load_session(session_id: str):
    path = SESSION_DIR / f"{session_id}.json"
    if not path.exists():
        st.warning("会话文件不存在")
        return

    data = json.loads(path.read_text(encoding="utf-8"))
    st.session_state.current_session = data.get("current_session", session_id)
    st.session_state.assistant_name = data.get("assistant_name", "知识库智能助理")
    st.session_state.assistant_style = data.get("assistant_style", "专业、简洁、可靠")
    st.session_state.mode = data.get("mode", "知识库问答")
    st.session_state.messages = data.get("messages", [])


def delete_session(session_id: str):
    session_file = SESSION_DIR / f"{session_id}.json"
    history_file = CHAT_HISTORY_DIR / session_id
    if session_file.exists():
        session_file.unlink()
    if history_file.exists():
        history_file.unlink()
    if st.session_state.current_session == session_id:
        st.session_state.current_session = generate_session_id()
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "已新建会话。你可以继续围绕知识库进行多轮提问。",
            }
        ]


@st.cache_resource
def get_rag_service():
    return RagService()


@st.cache_resource
def get_kb_service():
    return KnowledgeBaseService()


def to_langchain_messages(messages):
    converted = []
    for message in messages:
        role = message["role"]
        content = message["content"]
        if role == "user":
            converted.append(HumanMessage(content=content))
        elif role == "assistant":
            converted.append(AIMessage(content=content))
    return converted


def stream_normal_chat(rag_service: RagService, prompt: str):
    system_prompt = (
        f"你叫{st.session_state.assistant_name}，性格是{st.session_state.assistant_style}。"
        "你正在和用户进行多轮聊天。回答要自然、清晰，如果问题需要企业资料，提醒用户切换到知识库问答模式。"
    )
    history = to_langchain_messages(st.session_state.messages[:-1][-12:])
    messages = [SystemMessage(content=system_prompt), *history, HumanMessage(content=prompt)]

    for chunk in rag_service.chat_model.stream(messages):
        if chunk.content:
            yield chunk.content


def stream_rag_answer(rag_service: RagService, prompt: str):
    session_config = {
        "configurable": {
            "session_id": st.session_state.current_session,
        }
    }
    yield from rag_service.chain.stream({"input": prompt}, session_config)


def render_sidebar():
    with st.sidebar:
        st.header("控制台")

        if st.button("新建会话", use_container_width=True):
            save_session()
            st.session_state.current_session = generate_session_id()
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "新会话已创建。可以上传资料或直接提问。",
                }
            ]
            st.rerun()

        st.caption(f"当前会话：{st.session_state.current_session}")

        st.subheader("对话模式")
        st.session_state.mode = st.radio(
            "选择回答方式",
            ["知识库问答", "普通聊天"],
            index=0 if st.session_state.mode == "知识库问答" else 1,
            horizontal=True,
            label_visibility="collapsed",
        )

        st.subheader("助理配置")
        st.session_state.assistant_name = st.text_input(
            "助理名称",
            value=st.session_state.assistant_name,
        )
        st.session_state.assistant_style = st.text_input(
            "回答风格",
            value=st.session_state.assistant_style,
        )

        st.subheader("知识库")
        uploaded_file = st.file_uploader(
            "上传 UTF-8 文本文件",
            type=["txt", "md", "csv"],
            accept_multiple_files=False,
        )
        force_reindex = st.checkbox("强制重新写入")

        if uploaded_file and st.button("写入知识库", type="primary", use_container_width=True):
            try:
                text = uploaded_file.getvalue().decode("utf-8")
            except UnicodeDecodeError:
                st.error("文件不是 UTF-8 编码，请另存为 UTF-8 后再上传。")
            else:
                with st.spinner("正在切分文本并写入向量库..."):
                    result = get_kb_service().upload_by_str(
                        text,
                        uploaded_file.name,
                        force=force_reindex,
                    )
                    get_rag_service.clear()
                st.success(result)

        st.subheader("历史会话")
        for session_id in load_session_list():
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(session_id, key=f"load_{session_id}", use_container_width=True):
                    load_session(session_id)
                    st.rerun()
            with col2:
                if st.button("删", key=f"delete_{session_id}", use_container_width=True):
                    delete_session(session_id)
                    st.rerun()


def main():
    st.set_page_config(
        page_title="企业知识库多轮智能问答系统",
        page_icon="AI",
        layout="wide",
    )
    init_state()
    render_sidebar()

    st.title("企业知识库多轮智能问答系统")
    st.caption("多轮对话 + RAG 检索增强 + 知识库来源展示")

    try:
        rag_service = get_rag_service()
    except Exception as exc:
        st.error(f"初始化模型或向量库失败：{exc}")
        st.stop()

    for message in st.session_state.messages:
        st.chat_message(message["role"]).write(message["content"])

    prompt = st.chat_input("请输入问题")
    if not prompt:
        return

    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    chunks = []
    try:
        if st.session_state.mode == "知识库问答":
            rewritten_query = rag_service.rewrite_query(prompt, st.session_state.current_session)
            docs = rag_service.retrieve_documents(rewritten_query)
            with st.expander("本轮检索详情", expanded=False):
                st.markdown(f"**检索问题：** {rewritten_query}")
                if docs:
                    for index, doc in enumerate(docs, start=1):
                        source = doc.metadata.get("source", "未知来源")
                        st.markdown(f"**片段 {index} | {source}**")
                        st.write(doc.page_content)
                else:
                    st.warning("知识库没有检索到相关片段。")

            stream = stream_rag_answer(rag_service, prompt)
        else:
            stream = stream_normal_chat(rag_service, prompt)

        with st.chat_message("assistant"):
            response = st.write_stream(chunks.append(chunk) or chunk for chunk in stream)

        final_answer = response if isinstance(response, str) else "".join(chunks)
        st.session_state.messages.append({"role": "assistant", "content": final_answer})
        save_session()
    except Exception as exc:
        st.error(f"回答失败：{exc}")
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": f"回答失败：{exc}",
            }
        )
        save_session()


if __name__ == "__main__":
    main()
