import streamlit as st

from rag import RagService
from knowledge_base import KnowledgeBaseService
import config_data as config

#标题
st.title("知识库智能问答")
st.divider()    #分隔符

with st.sidebar:
    st.header("知识库")
    uploader_file=st.file_uploader(
        "请上传txt文件",
        type=["txt"],
        accept_multiple_files=False
    )

    if "service" not in st.session_state:
        st.session_state["service"]=KnowledgeBaseService()

    if uploader_file is not None:
        st.caption(f"文件名：{uploader_file.name}")
        st.caption(f"格式：{uploader_file.type} | 大小：{uploader_file.size / 1024:.2f}KB")
        force_reindex=st.checkbox("强制重新写入", help="如果之前上传时卡住了，可勾选后重新生成向量。")

        if st.button("写入知识库", type="primary"):
            try:
                text=uploader_file.getvalue().decode("utf-8")
            except UnicodeDecodeError:
                st.error("文件不是 UTF-8 编码，请先另存为 UTF-8 后再上传。")
            else:
                try:
                    with st.spinner("正在写入知识库..."):
                        result=st.session_state["service"].upload_by_str(text,uploader_file.name,force=force_reindex)
                    st.success(result)
                    st.session_state["rag"]=RagService()
                except Exception as exc:
                    st.error(f"写入知识库失败：{exc}")

if "message" not in st.session_state:
    st.session_state["message"]=[{"role":"assistant","content":"欢迎来到知识库智能问答，请输入问题。"}]

if "rag" not in st.session_state:
    try:
        st.session_state["rag"]=RagService()
    except Exception as exc:
        st.error(f"初始化问答服务失败：{exc}")
        st.stop()

for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])

prompt=st.chat_input("请输入问题：")

if prompt:
    #问题回显
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role":"user","content":prompt})

    ai_res_list=[]
    with st.spinner("正在处理..."):
        try:
            docs=st.session_state["rag"].retrieve_documents(prompt)
            if docs:
                with st.expander("本次检索到的知识库片段", expanded=False):
                    for index, doc in enumerate(docs, start=1):
                        source=doc.metadata.get("source","未知来源")
                        st.markdown(f"**片段 {index}｜{source}**")
                        st.write(doc.page_content)
            else:
                st.warning("本次没有从知识库检索到相关片段。请确认已点击“写入知识库”，必要时勾选“强制重新写入”。")

            res_stream=st.session_state["rag"].chain.stream({"input":prompt},config.session_config)#流式输出

            def capture(generator,cache_list):
                for chunk in generator:
                    cache_list.append(chunk)
                    yield chunk

            st.chat_message("assistant").write_stream(capture(res_stream,ai_res_list))
            st.session_state["message"].append({"role":"assistant","content":"".join(ai_res_list)})
        except Exception as exc:
            st.error(f"问答失败：{exc}")

