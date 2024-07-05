import os
import streamlit as st
import streamlit_antd_components as sac
import pandas as pd
from my_query import dc_query, lb_df_query,lb_query, inbound_record_add, inbound_record_add_lotsize,stock_record_add,stock_add_lotsize

def use_inbound_data(conn, current_user,channel_dic,origin_dic):
    st.write("**标签信息**")
    with st.container(border=True):
        col0 = st.columns([5,5])
        with col0[0]:            
            sap_code = st.text_input("**SAP物料码**[套件码或外胎码]")

        with col0[1]:
            if len(sap_code) == 0:
                #sap_pc = st.text_input("**SAP外胎码**", value="")
                unique_sap_pc = lb_df_query(conn)["sap_pc"].unique().tolist()
                sap_pc = st.selectbox("**SAP外胎码**", options=unique_sap_pc, index=None, key="sap_pc")
                sap_pc = str(sap_pc)
            else:
                try:
                    sap_pc = st.text_input("**SAP外胎码**", value=dc_query(conn, sap_code)["BOM组件"][0],disabled=True)
                except:
                    unique_sap_pc = lb_df_query(conn)["sap_pc"].unique().tolist()
                    sap_pc = st.selectbox("**SAP外胎码**", options=unique_sap_pc, index=None, key="sap_pc")
                    sap_pc = str(sap_pc)
        
        col1 = st.columns([7,3])
        with col1[0]:
            try:
                sap_pc_dc = st.text_input("**物料描述**", value=dc_query(conn, sap_pc)["组件描述"][0],disabled=True)
            except:
                sap_pc_dc = st.text_input("**物料描述**", value="",disabled=True)
        with col1[1]:
            try:
                brand = st.text_input("**品牌**", value=sap_pc_dc.split("\\")[1],disabled=True)
            except:
                brand = st.text_input("**品牌**", value="",disabled=True)
        
        col4 = st.columns([7,3])
        with col4[0]:
            channel = st.radio(label="**市场**",options=["","国内","出口","欧盟","巴西","韩国"],index=0,horizontal=True)
            st.success("市场代码：不限(00)，国内(01)，出口(02)，欧盟(03)，巴西(04)，韩国(05)")
        with col4[1]:
            origin = st.radio(label="**产地**",options=["JZ","TY"],index=0,horizontal=True)
            st.success("产地代码：JZ(00)，TY(01)")   

        col2 = st.columns([4,6])
        with col2[0]:
            if sap_pc_dc == "":           
                lb_code = st.text_input("**标签物料号**【SAP外胎码+市场代码+产地代码】", value="",disabled=True)
                lb_dc_value = ""
            else:
                lb_code = st.text_input("**标签物料号**【SAP外胎码+市场代码+产地代码】", value = int(sap_pc)*10000 + channel_dic[channel]*100+ origin_dic[origin],disabled=True)
                if channel == "":
                    lb_dc_value = sap_pc_dc +  "(" + origin + ")"
                else:
                    lb_dc_value = sap_pc_dc + "(" + channel + "+" + origin + ")"
        with col2[1]:
            lb_dc = st.text_input("**标签物料描述**【物料描述+(市场+产地)】", value = lb_dc_value,disabled=True)
        
        
        if lb_code == "":
            lb_status = "不存在"
            # st.warning("标签信息未定义，请先完成'主数据维护→标签定义'步骤！")
        else:
            try:
                if len(lb_query(conn, sap_pc, channel,origin)) >0:
                    # print(lb_query(conn, lb_code))
                    lb_status = "已存在"
                else:
                    lb_status = "不存在"
                    st.warning("标签信息未定义，请先完成'主数据维护→标签定义'步骤！")
            except:
                lb_status = "不存在"
                st.warning("标签信息未定义，请先完成'主数据维护→标签定义'步骤！")

    if lb_status == "已存在":
        st.write("**入库信息**")
        with st.container(border=True):
            col3 = st.columns([3,3,3])
            with col3[0]:
                try:
                    start_location = str(lb_query(conn, sap_pc, channel,origin)["start_location"][0])
                    inbound_location = st.text_input("**入库货位**【货架码-层码-位置码】",value=start_location)
                except:
                    inbound_location = st.text_input("**入库货位**【货架码-层码-位置码】",value="货架码-层码-位置码")
            with col3[1]:
                inbound_num = st.number_input("**入库数量**",value=0)
            with col3[2]:                
                if inbound_num >=0:
                    inbound_type = st.selectbox("**入库类型**",["正常入库","退库"],index=0)
                else:
                    inbound_type = st.selectbox("**入库类型**",["正常入库","退库"],index=1)
            inbound_remark = st.text_input("备注")
        
        if len(sap_pc) == 10 and inbound_num != 0 and inbound_location != "":
            col = st.columns([1,1,1,1,4])
            with col[0]:
                if st.button('入库',type="primary",use_container_width=True):
                    inbound_record_add(conn,sap_pc,sap_pc_dc,brand,channel,origin,lb_code,lb_dc,inbound_num,inbound_location,inbound_type,inbound_remark,current_user)
                    stock_record_add(conn, sap_pc, channel, origin,lb_code, lb_dc, inbound_num, inbound_location,inbound_type,current_user)
        else:
            st.warning("请选择入库数量、入库货位和入库类型！")
            col = st.columns([1,1,1,1,4])
            with col[0]:
                st.button('入库',type="primary",use_container_width=True,disabled=True)
    
    
    sac.divider("批量导入入库数据",align='start',color='red')
    with st.expander("**注意：批量导入功能暂未开放，请联系管理员！**"):
        template_dir = "templates"  
        template_file_path = os.path.join(template_dir, "inbound_data_template.xlsx")  
        st.download_button("下载模板",type="primary",data=open(template_file_path, "rb").read(),file_name="inbound_data_template.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        try:
            upload_data = st.file_uploader("请选择要上传的文件：",type=["xlsx"],key="inbound_data_upload")
            if upload_data is not None:
                df = pd.read_excel(upload_data,sheet_name="inbound")
                if len(df) == 0:
                    st.error("上传文件为空！")
                else:
                    st.dataframe(df)
                    st.success("文件已上传！")
                    if st.button("导入数据",type="primary",key="inbound_data_button"):
                        progress_text = "数据导入中，请稍等..."
                        my_bar = st.progress(0, text=progress_text)
                        error_list = []
                        for i in range(len(df)):
                            sap_pc = str(df.iloc[i]["SAP外胎码"])

                            # sap_pc_dc = str(df.iloc[i]["sap_pc_dc"])
                            value = df.iloc[i]["物料描述"]  
                            if pd.isnull(value):  # 检查值是否为 NaN  
                                sap_pc_dc = ""  
                            else:  
                                sap_pc_dc = str(value)

                            # brand = str(df.iloc[i]["brand"])
                            value = df.iloc[i]["品牌"]  
                            if pd.isnull(value):  # 检查值是否为 NaN  
                                brand = ""  
                            else:  
                                brand = str(value)                
                            
                            #channel = str(df.iloc[i]["channel"])
                            value = df.iloc[i]["市场"]  
                            if pd.isnull(value):  # 检查值是否为 NaN  
                                channel = ""  
                            else:  
                                channel = str(value)

                            value = df.iloc[i]["产地"]  
                            if pd.isnull(value):  # 检查值是否为 NaN  
                                origin = ""  
                            else:  
                                origin = str(value)

                            #lb_code = str(df.iloc[i]["lb_code"])
                            value = df.iloc[i]["标签物料码"]  
                            if pd.isnull(value):  # 检查值是否为 NaN  
                                lb_code = ""  
                            else:  
                                lb_code = str(value)

                            #lb_dc = str(df.iloc[i]["lb_dc"])
                            value = df.iloc[i]["标签物料描述"] 
                            if pd.isnull(value):  # 检查值是否为 NaN  
                                lb_dc = ""  
                            else:  
                                lb_dc = str(value)

                            # inbound_num = int(df.iloc[i]["inbound_num"])
                            if pd.isnull(df.iloc[i]["入库数量"]):  
                                # 如果为 NaN，你可以选择设置一个默认值，比如 0 或者抛出一个更具体的错误  
                                inbound_num = 0  # 或者你可以抛出一个错误，或者做其他处理  
                            else:  
                                # 如果不是 NaN，则转换为整数  
                                inbound_num = int(df.iloc[i]["入库数量"])  
                            
                            #inbound_location = str(df.iloc[i]["inbound_location"])
                            value = df.iloc[i]["入库库位"]  
                            if pd.isnull(value):  # 检查值是否为 NaN  
                                inbound_location = ""  
                            else:  
                                inbound_location = str(value)

                            #inbound_type = str(df.iloc[i]["inbound_type"])
                            value = df.iloc[i]["入库类型"] 
                            if pd.isnull(value):  # 检查值是否为 NaN  
                                inbound_type = ""  
                            else:  
                                inbound_type = str(value)

                            #inbound_remark = str(df.iloc[i]["inbound_remark"])
                            value = df.iloc[i]["入库备注"] 
                            if pd.isnull(value):  # 检查值是否为 NaN  
                                inbound_remark = ""  
                            else:  
                                inbound_remark = str(value)

                            # print(sap_code,sap_dc,sap_pc,sap_pc_dc)
                            if  len(lb_code) != 14 or len(sap_pc) != 10 or origin not in ["JZ","TY"] or inbound_num <= 0 or inbound_location == "" or inbound_type not in ["正常入库","退库"] :
                                #st.error(f"第{i}行数据错误，请核对相关数据后再此尝试！")
                                # 已经在数据库中添加了约束ck_inbound_location_not_null，所以这里不用再重复检查了
                                error_list.append([sap_pc,sap_pc_dc,brand,channel,origin,lb_code,lb_dc,inbound_num,inbound_location,inbound_type,inbound_remark,"数据错误或不完整！请核对数据！"])
                                #error_list = inbound_record_add_lotsize(conn,sap_pc,sap_pc_dc,brand,channel,origin,lb_code,lb_dc,inbound_num,inbound_location,inbound_type,inbound_remark,current_user, error_list)
                                #stock_add_lotsize(conn, sap_pc, channel, origin, lb_code, lb_dc, inbound_num, inbound_location,inbound_type,current_user)
                            else:
                                error_list = inbound_record_add_lotsize(conn,sap_pc,sap_pc_dc,brand,channel,origin,lb_code,lb_dc,inbound_num,inbound_location,inbound_type,inbound_remark,current_user, error_list)
                                stock_add_lotsize(conn, sap_pc, channel, origin, lb_code, lb_dc, inbound_num, inbound_location,inbound_type,current_user)
                            my_bar.progress((i+1)/len(df), text=progress_text)
                        my_bar.empty()

                        try:
                            if len(df)-len(error_list) != 0:
                                st.success(f"共{len(df)-len(error_list)}条数据导入成功！")            
                            if len(error_list) != 0:
                                st.error(f"共{len(error_list)}条数据导入失败！清单如下：")
                                df_error = pd.DataFrame(error_list,columns=["SAP外胎码","物料描述","品牌","市场","产地","标签物料码","标签物料描述","入库数量","入库库位","入库类型","入库备注","错误信息"])
                                st.dataframe(df_error,hide_index=True)
                                #st.dataframe(error_list,hide_index=True)
                        except:
                            st.success(f"共{len(df)}条数据导入成功！")
        except:
            st.error("上传文件格式错误！请使用指定模板上传！")
            

