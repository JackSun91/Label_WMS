import streamlit as st
import streamlit_antd_components as sac
from my_query import dc_query,dc_df_query, master_record_add,lb_query, master_record_update,master_record_delete,stock_record_add,stock_record_update,inbound_record_add,inbound_record_update

def use_master_data(conn, current_user,channel_dic,origin_dic):
    st.write("**标签信息**")
    with st.container(border=True):        
        col0 = st.columns([5,5])
        with col0[0]:
            unique_sap_code = dc_df_query(conn)["物料"].unique().tolist()
            sap_code = st.selectbox("**SAP物料码**【套件码或外胎码】", options=unique_sap_code, index=None, key="sap_code")
            sap_code = str(sap_code)
            #sap_code = st.text_input("**SAP物料码**【套件码或外胎码】")
        with col0[1]:
            if len(sap_code) == 0:
                sap_pc = st.text_input("**SAP外胎码**", value="",disabled=True)
            else:
                try:
                    sap_pc = st.text_input("**SAP外胎码**", value=dc_query(conn, sap_code)["BOM组件"][0],disabled=True)
                except:
                    sap_pc = st.text_input("**SAP外胎码**", value="",disabled=True)
        
        col1 = st.columns([7,3])
        with col1[0]:
            try:
                sap_dc = st.text_input("**物料描述**", value=dc_query(conn, sap_pc)["组件描述"][0],disabled=True)
            except:
                sap_dc = st.text_input("**物料描述**", value="",disabled=True)
        with col1[1]:
            try:
                brand = st.text_input("**品牌**", value=sap_dc.split("\\")[1],disabled=True)
            except:
                brand = st.text_input("**品牌**", value="",disabled=True)
        
        col4 = st.columns([7,3])
        with col4[0]:
            channel = st.radio(label="**市场**",options=["","国内","出口","欧盟","巴西","韩国"],index=0,horizontal=True)
            st.success("市场代码：不限(00)，国内(01)，出口(02)，欧盟(03)，巴西(04)，韩国(05)")
        with col4[1]:
            origin = st.radio(label="**产地**",options=["JZ","TY"],index=0,horizontal=True)
            st.success("产地代码：JZ(00)，TY(01)")

        
        col2 = st.columns([3,7])
        with col2[0]:
            if sap_dc == "":           
                lb_code = st.text_input("**标签物料号**【SAP外胎码+市场代码+产地代码】", value="",disabled=True)
                lb_dc_value = ""
            else:
                lb_code = st.text_input("**标签物料号**【SAP外胎码+市场代码+产地代码】", value = int(sap_pc)*10000 + channel_dic[channel]*100+ origin_dic[origin],disabled=True)
                if channel == "":
                    lb_dc_value = sap_dc +  "(" + origin + ")"
                else:
                    lb_dc_value = sap_dc + "(" + channel + "+" + origin + ")"
        with col2[1]:
            lb_dc = st.text_input("**标签物料描述**【物料描述+(市场+产地)】", value = lb_dc_value,disabled=True)
        
        col3 = st.columns([3,4,3])
        with col3[0]:
            try:
                start_location = st.text_input("**期初库存位置**【货架码-层码-位置码】", value=lb_query(conn, sap_pc, channel, origin)["start_location"][0])
            except:
                start_location = st.text_input("**期初库存位置**【货架码-层码-位置码】", value="货架码-层码-位置码")  

        with col3[1]:
            try:
                start_stock = st.text_input("**期初库存**", value=lb_query(conn, sap_pc, channel, origin)["start_stock"][0])
            except:
                start_stock = st.text_input("**期初库存**", value=0)
    
        
        with col3[2]:
            if lb_code == "":
                lb_status = st.text_input("**主数据状态**",value="")
            else:
                try:
                    if len(lb_query(conn, sap_pc, channel, origin)) >0:
                        # print(lb_query(conn, lb_code))
                        lb_status = st.text_input("**主数据状态**",value="已存在",disabled=True)
                    else:
                        lb_status = st.text_input("**主数据状态**",value="不存在",disabled=True) 
                except:
                    lb_status = st.text_input("**主数据状态**",value="不存在",disabled=True)

    if lb_status == "已存在":
        col = st.columns([1,1,1,1,4])
        with col[0]:
            if st.button('新增',type="primary",use_container_width=True,disabled=True):
                if len(sap_pc) != 10 or sap_dc == '' :
                    st.toast("数据错误，请核对相关数据后再此尝试！")
        with col[1]:
            if st.button('修改',type="primary",use_container_width=True):
                master_record_update(conn, sap_code,sap_pc,sap_dc,channel,origin,lb_code,lb_dc,start_stock,start_location,current_user)
                stock_record_update(conn, sap_pc, channel, origin,lb_code, lb_dc, start_stock, start_location, current_user)
                inbound_record_update(conn,sap_pc,sap_dc,brand,channel,origin, lb_code,lb_dc,start_stock,start_location,current_user)
        with col[2]:
            if st.button('删除',type="primary",use_container_width=True,disabled=True):
                # 主数据是系统成立的基础，理论上不应该出现删除按钮，因为删除操作应该由管理员操作，而非用户操作
                master_record_delete(conn, sap_pc,channel, origin)
    else:
        col = st.columns([1,1,1,1,4])
        with col[0]:        
            if st.button('新增',type="primary",use_container_width=True):
                if len(sap_pc) != 10 or sap_dc == '' :
                    st.toast("数据错误，请核对相关数据后再此尝试！")
                else:
                    master_record_add(conn, sap_code,sap_pc,sap_dc,channel,origin,lb_code,lb_dc,start_stock,start_location,current_user)
                    stock_record_add(conn, sap_pc, channel, origin,lb_code, lb_dc, start_stock, start_location,"期初库存",current_user)
                    inbound_record_add(conn,sap_pc,sap_dc,brand,channel,origin,lb_code,lb_dc,start_stock,start_location,"期初库存","创建",current_user)
        with col[1]:
            st.button('修改',type="primary",use_container_width=True,disabled=True)
        with col[2]:
            st.button('删除',type="primary",use_container_width=True,disabled=True)
