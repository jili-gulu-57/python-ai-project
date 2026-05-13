# 导入模块
from idlelib.outwin import file_line_pats

#1.导入模块--------------------------------------------------------
import streamlit as st  #创作网页、输入框、按钮、聊天框、侧边栏
import os   #读取环境变量、创建文件夹、文件操作
from openai import OpenAI   #Deepseek完全兼容OpenAI API格式
from datetime import datetime   #生成会话ID，保存聊天时间
import json #序列化保存会话信息，反序列化读取出来
#------------------------------------------------------------------

#整体逻辑：页面初始化  ->状态初始化 ->会话管理 ->侧边栏操作 ->聊天请求

#2.设置页面的配置项-------------------------------------------------
st.set_page_config(
    page_title="AI伙伴",  # 标题
    page_icon=":robot_face:",   #表情
    layout="wide",  #布局
    initial_sidebar_state="expanded"    #侧边栏状态
)
#------------------------------------------------------------------

#3.工具函数----------------------------------------------------------
#生成会话id函数
def generate_session_id():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

#保存会话信息为json格式函数
def save_session():
    if st.session_state.current_session:
        session_data = {
            "nick_name": st.session_state.nick_name,
            "nature": st.session_state.nature,
            "current_session": st.session_state.current_session,
            "messages": st.session_state.messages
        }

        if not os.path.exists("sessions"):
            os.mkdir("sessions")

        # 保存会话数据
        with open(f"sessions/{st.session_state.current_session}.json", "w",encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

#加载历史会话列表函数
def load_session_list():
    session_list=[]
    if os.path.exists("sessions"):
        file_list=os.listdir("sessions")
        for filename in file_list:
            if filename.endswith(".json"):
                session_list.append(filename[:-5])
    session_list.sort(reverse=True) #按时间倒序排序
    return session_list

#加载指定会话信息函数
def load_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            # 读取会话数据
            with open(f"sessions/{session_name}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.messages = session_data["messages"]
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.nature = session_data["nature"]
                st.session_state.current_session = session_name
    except Exception:
        st.error("加载会话失败!")

# 删除会话信息函数
def delete_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            os.remove(f"sessions/{session_name}.json") # 删除文件
            # 如果删除的是当前会话, 则需要更新消息列表
            if session_name == st.session_state.current_session:
                st.session_state.messages = []
                st.session_state.current_session = generate_session_id()
    except Exception:
        st.error("删除会话失败!")
#------------------------------------------------------------------

#4.初始化session_state状态-------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

#昵称
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "小A"

#性格
if "nature" not in st.session_state:
    st.session_state.nature = "沉稳可靠"

#会话标识
if "current_session" not in st.session_state:
    st.session_state.current_session=generate_session_id()

#-----------------------------------------------------------------------

#5.主页面展示 -----------------------------------------------------------

#大标题
st.title("AI伙伴")
#Logo
st.logo("resources/logo.png")

#渲染历史聊天信息
st.text(f"会话名称：{st.session_state.current_session}")
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

#-------------------------------------------------------------------------

#6.创建AI客户端------------------------------------------------------------
client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")
#-------------------------------------------------------------------------

#7.左侧侧边栏控制面板------------------------------------------------------
with st.sidebar:
    #会话信息
    st.subheader("AI控制面板")

    #新建会话
    if(st.button("+ 新建会话",width="stretch")):
        #1.保存当前会话
        save_session()

        #2.创建新的会话
        if st.session_state.messages:
            st.session_state.messages=[]
            st.session_state.current_session = generate_session_id()
            save_session()
            st.rerun()

    #历史会话信息
    st.text("历史会话")
    session_list=load_session_list()
    for session in session_list:
        col1,col2=st.columns([4,1])
        with col1:
             if st.button(session,width="stretch",icon="📜", key=f"load_{session}", type="primary" if session == st.session_state.current_session else "secondary"):
                 load_session(session)
                 st.rerun()
        with col2:
            if st.button("",width="stretch",icon="❌", key=f"delete_{session}"):
                delete_session(session)
                st.rerun()

    #伙伴信息
    st.subheader("伙伴信息")
    #昵称输入框
    nick_name=st.text_input("昵称：",placeholder="请输入昵称",value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name=nick_name

    #性格输入框
    nature=st.text_input("性格",placeholder="请输入昵称",value=st.session_state.nature)
    if nature:
        st.session_state.nature = nature
#----------------------------------------------------------------------------

#8.聊天输入和消息回复------------------------------------------------------------
prompt=st.chat_input("请输入您的问题：")
if prompt:
    st.chat_message("user").write(prompt)   #消息回显
    #保存用户提示词到会话状态
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 系统提示词
    system_prompt = "你叫%s，现在你是用户的伙伴，你的性格是%s，请遵守这些要求和用户交流" % (
        st.session_state.nick_name,
        st.session_state.nature
    )
    #请求大模型
    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {"role": "system", "content":system_prompt},
            {"role": "user", "content": prompt},
        ],
        stream=False,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )
    #保存AI回复到会话状态
    st.session_state.messages.append({"role": "assistant", "content":response.choices[0].message.content})

    # print(response.choices[0].message.content)
    st.chat_message("assistant").write(response.choices[0].message.content)
#----------------------------------------------------------------------------