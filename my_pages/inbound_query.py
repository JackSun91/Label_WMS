import streamlit as st
import streamlit_antd_components as sac
import pandas as pd
from my_query import dc_query, inbound_df_query,inbound_df_query_with_filter

def use_inbound_query(conn,this_month_start,this_month_end):
    st.write("**查询条件**")    
    with st.container(border=True):
        inbound_data_df = inbound_df_query(conn)
        # st.dataframe(inbound_data_df)

        col =st.columns([1,3,1.4,0.6])
        with col[0]:
            sap_code = st.text_input("**SAP物料码**[套件码或外胎码]",key="sap_code")
        with col[1]:
            # 获取 'channel' 列的唯一值，并转换为列表  
            unique_channels = inbound_data_df["channel"].unique().tolist()               
            channel = st.multiselect("**市场**", unique_channels,default=unique_channels,placeholder="请至少选择一个市场") 
 
        with col[2]:
            unique_origin = inbound_data_df["origin"].unique().tolist()               
            origin = st.multiselect("**产地**", unique_origin,default=unique_origin,placeholder="请至少选择一个产地") 
        with col[3]:
            start_date = st.date_input("**开始日期**",value=this_month_start)


        col2 =st.columns([4,1.4,0.6])
        with col2[0]:
            unique_brand = inbound_data_df["brand"].unique().tolist()               
            brand = st.multiselect("**品牌**", unique_brand,default=unique_brand,placeholder="请至少选择一个品牌") 
        with col2[1]:
            unique_inbound_type = inbound_data_df["inbound_type"].unique().tolist()               
            inbound_type = st.multiselect("**入库类型**", unique_inbound_type,default=unique_inbound_type,placeholder="请至少选择一个入库类型") 

        with col2[2]:
            end_date = st.date_input("**结束日期**",value=this_month_end)

    if len(channel) == 0 or len(brand) == 0 or len(origin) == 0 or len(inbound_type) == 0:
        st.warning("[市场]、[品牌]、[产地]、[入库类型]4个属性,每个属性都必须至少选择一个！")
        col = st.columns([1,7])
        with col[0]:
            st.button('查询',type="primary",use_container_width=True,disabled=True)

    else:
        col = st.columns([1,7])
        with col[0]:
            if st.button('查询',type="primary",use_container_width=True):
                if len(sap_code) == 0:
                    sap_pc = ""
                elif len(sap_code)== 10:
                    try:
                        sap_pc = str(dc_query(conn, sap_code)["BOM组件"][0])
                    except:                        
                        st.toast("SAP物料码不存在！")
                else:
                    st.toast("SAP物料码必须为10位！")


        with col[1]:
            #print(sap_pc,channel,origin,start_date,end_date,brand,inbound_type)
            try:                
                df =inbound_df_query_with_filter(conn, sap_pc, channel, origin, start_date, end_date, brand, inbound_type)
                df["sap_pc"] = df["sap_pc"].astype(str)
                num =df["inbound_num"].sum()
                count =df.shape[0]
                sac.alert("**共查询到**"+str(count)+"**条记录**，**合计入库**"+str(num)+"**个标签**",banner=True)
            except:
                sac.alert("未查到有效数据，请检查查询条件后重新查询！")            
                
        try:
            df.columns = ["入库流水号","SAP外胎码","物料描述","品牌","市场","产地","标签物料码","标签物料描述","入库数量","入库库位","入库类型","入库备注","入库时间","入库人员"]
            st.dataframe(df,hide_index=True,use_container_width=True)
        except:
            pass
