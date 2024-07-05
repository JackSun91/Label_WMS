import streamlit as st
import streamlit_antd_components as sac
import pandas as pd
from my_query import dc_query, stock_df_query,stock_df_query_with_filter

def use_stock_query(conn):
    st.write("**查询条件**")    
    with st.container(border=True):
        stock_df = stock_df_query(conn)
        #st.dataframe(stock_df)

        col =st.columns([2,5,2])
        with col[0]:
            sap_code = st.text_input("**SAP物料码**[套件码或外胎码]",key="sap_code")
        with col[1]:
            # 获取 'channel' 列的唯一值，并转换为列表  
            unique_channels = stock_df["channel"].unique().tolist()               
            channel = st.multiselect("**市场**", unique_channels,default=unique_channels,placeholder="请至少选择一个市场")
        with col[2]:
            unique_origin = stock_df["origin"].unique().tolist()               
            origin = st.multiselect("**产地**", unique_origin,default=unique_origin,placeholder="请至少选择一个产地")              

        col2 =st.columns([2,7])
        with col2[0]:
            lb_code = st.text_input("**标签物料码**",key="lb_code")
        with col2[1]:
            unique_brand = stock_df["brand"].unique().tolist()
            brand = st.multiselect("**品牌**", unique_brand,default=unique_brand,placeholder="请至少选择一个品牌") 

    if len(channel) == 0 or len(brand) == 0:
        st.warning("[市场]、[品牌]2个属性,每个属性都必须至少选择一个！")
        col = st.columns([1,7])
        with col[0]:
            st.button('查询',type="primary",use_container_width=True,disabled=True)

    else:
        col = st.columns([1,7])
        with col[0]:
            if st.button('查询',type="primary",use_container_width=True):
                if len(sap_code) == 0:
                    sap_pc = ""
                    if len(lb_code) == 0:
                        lb_code = ""
                    elif len(lb_code) == 12:
                        lb_code = lb_code
                    else:
                        st.toast("标签物料码必须为12位！")

                elif len(sap_code)== 10:                    
                    try:
                        sap_pc = str(dc_query(conn, sap_code)["BOM组件"][0])
                    except:                        
                        st.toast("SAP物料码不存在！")
                    if len(lb_code) == 0:
                        lb_code = ""
                    elif len(lb_code) == 12:
                        lb_code = lb_code
                    else:
                        st.toast("标签物料码必须为12位！")                    
                else:
                    st.toast("SAP物料码必须为10位！")


        with col[1]:
            try:
                df = stock_df_query_with_filter(conn, sap_pc, lb_code,channel, brand, origin)
                df["sap_pc"] = df["sap_pc"].astype(str)
                df = df[df["stock_num"]!=0]
                num =df["stock_num"].sum()
                count =df.shape[0]
                sac.alert("**共查询到**"+str(count)+"**条记录**，**合计库存**"+str(num)+"**个标签**",banner=True)
            except:
                sac.alert("未查到有效数据，请检查查询条件后重新查询！")            
                
        try:
            df.columns = ["SAP外胎码","市场","品牌","产地","标签物料码","标签物料描述","库存数量","库位"]
            st.dataframe(df,hide_index=True,use_container_width=True)
        except:
            pass
