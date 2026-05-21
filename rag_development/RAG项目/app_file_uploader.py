import time
import streamlit as st
from knowledge_base import KnowledgeBaseService

#网页标题
st.title("知识库更新服务")

#上传文件
uploader_file=st.file_uploader(
    "请上传txt文件",
    type=['txt'],
    accept_multiple_files=False
)


#状态维护

if "service" not in st.session_state:
    st.session_state["service"]=KnowledgeBaseService()

#上传文件不为空
if uploader_file is not None:
    file_name=uploader_file.name
    file_type=uploader_file.type
    file_size=uploader_file.size/1024

    #二级标题
    st.subheader(f"文件名：{file_name}")
    #正文
    st.write(f"格式：{file_type} | 大小：{file_size:.2f}KB")

    text=uploader_file.getvalue().decode("utf-8")
    st.write(text)

    with st.spinner("正在处理..."):
        time.sleep(1)
        result= st.session_state["service"].upload_by_str(text,file_name)
        st.write(result)