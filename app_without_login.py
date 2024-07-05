import streamlit as st
import sqlite3
import streamlit_antd_components as sac
from datetime import datetime, timedelta
import calendar
from my_query import user_query
from my_pages.master_data import use_master_data
from my_pages.bom_data import use_bom_data
from my_pages.inbound_data import use_inbound_data
from my_pages.inbound_query import use_inbound_query
from my_pages.outbound_data import use_outbound_data
from my_pages.outbound_query import use_outbound_query
from my_pages.stock_query import use_stock_query


st.set_page_config("Label WMS",page_icon="🏭",layout="wide")

# 建立数据库连接
try:
    conn = sqlite3.connect('lwms.db')
    #st.success("数据库链接成功！")
except:
    st.warning("数据库链接失败，请检查网络！")

credentials = user_query(conn)

# 隐藏右边的菜单以及页脚, 去掉Deploy按钮
hide_st_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
        </style>
        """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Sidebar顶格设置
st_sidebar_style =f"""
    <style>
    .stApp .main .block-container{{padding:0px 50px}}
    .stApp [data-testid='stSidebar']>div:nth-child(1)>div:nth-child(2){{padding-top:60px}}
    iframe{{display:block;}}
    .stRadio div[role='radiogroup']>label{{margin-right:5px}}
    </style>
    """
st.markdown(st_sidebar_style, unsafe_allow_html=True)

if "auth_status" not in st.session_state:
    st.session_state["auth_status"] = 1

if "sap_pc" not in st.session_state:
    st.session_state["sap_pc"] = ''

default_date = datetime.today() - timedelta(days=90)
if "start_date" not in st.session_state:
    st.session_state["start_date"] = default_date    

if "end_date" not in st.session_state:
    st.session_state["end_date"] = datetime.today()  
    

auth_status = st.session_state["auth_status"]

if "auth_user" not in st.session_state:
    st.session_state["auth_user"] = "系统"
name = st.session_state["auth_user"]


current_user = st.session_state["auth_user"]   

# 定义渠道字典
channel_dic = {'':0,'国内':1,'出口':2,'欧盟':3,'巴西':4,'韩国':5}
# 定义产地字典
origin_dic = {'JZ':0, 'TY':1}

now = datetime.now()
this_month_start = datetime(now.year, now.month, 1)
this_month_end = datetime(now.year, now.month, calendar.monthrange(now.year, now.month)[1])

# 标签格式定义
modified = sac.Tag('变更', color='blue', bordered=False)
new = sac.Tag('新推', color='green', bordered=False)
deprecated = sac.Tag('废弃', color='orange', bordered=False)
redesign = sac.Tag('重构', color='purple', bordered=False)
user_tag = sac.Tag(current_user, color='green', bordered=False)
quit = sac.Tag('注销', color='red', bordered=False)

with st.sidebar.container():
    # 使用 st.markdown 和内联 CSS 来创建居中的标题  
    centered_subheader = """  
    <div style="text-align:center; font-size:25px; font-weight:bold; color: rgb(255,75,75);">  
        Label WMS
    </div>  
    """  
    st.markdown(centered_subheader, unsafe_allow_html=True)
    menu = sac.menu([
        sac.MenuItem(f'当前用户：', icon="list",tag=user_tag,disabled=True),
        sac.MenuItem("库存查询",icon="box-fill"),
        sac.MenuItem("入库管理",icon="box-fill", children=[
            sac.MenuItem("物料入库",icon="box-arrow-in-left"),
            sac.MenuItem("入库信息查询",icon="search"),
            sac.MenuItem("入库统计分析",icon="kanban",disabled=True)
            ]),
        sac.MenuItem("出库管理",icon="box-fill", children=[
            sac.MenuItem("物料出库",icon="box-arrow-right"),
            sac.MenuItem("出库信息查询",icon="search"),
            sac.MenuItem("出库统计分析",icon="kanban",disabled=True)
            ]),
        sac.MenuItem("主数据维护",icon="database-fill-gear",children=[
            sac.MenuItem("标签定义",icon="bookmark-plus"),
            sac.MenuItem("套外关系维护",icon="distribute-horizontal")
            ]),
        sac.MenuItem('退出登录', icon="box-arrow-right",tag=quit),       
    ],index=1,open_all=True)

# st.subheader("标签管理系统",divider="red")
if menu == "库存查询":
    use_stock_query(conn)
elif menu == "物料入库":
    use_inbound_data(conn, current_user,channel_dic,origin_dic)
elif menu == "入库信息查询":
    use_inbound_query(conn,this_month_start,this_month_end)
elif menu == "入库统计分析":
    pass
elif menu == "物料出库":
    use_outbound_data(conn, current_user,channel_dic,origin_dic)
elif menu == "出库信息查询":
    use_outbound_query(conn,this_month_start,this_month_end)
elif menu == "出库统计分析":
    pass
elif menu == "标签定义":
    use_master_data(conn, current_user,channel_dic, origin_dic)
elif menu == "套外关系维护":
    use_bom_data(conn)
elif menu == '退出登录':
    with st.spinner("加载中……"):
        st.session_state["auth_status"] = 1
        st.rerun()