import os
import streamlit as st
import streamlit_antd_components as sac
import pandas as pd
from my_query import dc_query,bom_record_add,bom_record_update,bom_record_delete,bom_record_add_lotsize

def use_bom_data(conn):
    st.write("**套件与外胎信息**")
    with st.container(border=True):           
        col0 = st.columns([3,7])
        with col0[0]:
            sap_code = st.text_input("**SAP物料码**[套件码或外胎码]")
        with col0[1]:
            if len(sap_code) == 0:
                sap_dc = st.text_input("**物料描述**", value="")
            else:
                try:
                    sap_dc = st.text_input("**物料描述**", value=dc_query(conn, sap_code)["物料描述"][0])
                except:
                    sap_dc = st.text_input("**物料描述**", value="")
        col1 = st.columns([3,7])
        with col1[0]:    
            if len(sap_code) == 0:
                sap_pc = st.text_input("**SAP外胎码**", value="")
            else:
                try:
                    sap_pc = st.text_input("**SAP外胎码**", value=dc_query(conn, sap_code)["BOM组件"][0])
                except:
                    sap_pc = st.text_input("**SAP外胎码**", value="")
        with col1[1]:
            if len(sap_code) == 0:
                sap_pc_dc = st.text_input("**组件描述**", value="")
            else:
                try:
                    sap_pc_dc = st.text_input("**组件描述**", value=dc_query(conn, sap_code)["组件描述"][0])
                except:
                    sap_pc_dc = st.text_input("**组件描述**", value="")

    if sap_code == "" or sap_dc == "" or sap_pc == "" or sap_pc_dc == "":
        st.success("请完整填写所有必填项！")
        col = st.columns([1,1,1,1,4])
        with col[0]:
            st.button('新增',type="primary",use_container_width=True,disabled=True)
        with col[1]:
            st.button('修改',type="primary",use_container_width=True,disabled=True)
        with col[2]:
            st.button('删除',type="primary",use_container_width=True,disabled=True)
    elif len(dc_query(conn, sap_code)) != 0:
        col = st.columns([1,1,1,1,4])
        with col[0]:        
            st.button('新增',type="primary",use_container_width=True,disabled=True)
        with col[1]:
            if st.button('修改',type="primary",use_container_width=True):
                if len(sap_code) != 10 or len(sap_pc) != 10 :
                    st.toast("数据错误，请核对相关数据后再此尝试！")
                else:
                    bom_record_update(conn, sap_code,sap_dc,sap_pc,sap_pc_dc)
        with col[2]:
            if st.button('删除',type="primary",use_container_width=True):
                bom_record_delete(conn, sap_code)
    else:
        col = st.columns([1,1,1,1,4])
        with col[0]:        
            if st.button('新增',type="primary",use_container_width=True):
                if len(sap_code) != 10 or len(sap_pc) != 10 :
                    st.toast("数据错误，请核对相关数据后再此尝试！")
                else:
                    bom_record_add(conn, sap_code,sap_dc,sap_pc,sap_pc_dc)
        with col[1]:
            st.button('修改',type="primary",use_container_width=True,disabled=True)
        with col[2]:
            st.button('删除',type="primary",use_container_width=True,disabled=True)
    
    sac.divider("批量导入套外关系",align='start',color='red')
    with st.expander("**注意：批量导入功能暂未开放，请联系管理员！**"):
        template_dir = "templates"  
        template_file_path = os.path.join(template_dir, "bom_data_template.xlsx")  

        st.download_button("下载模板",type="primary",data=open(template_file_path, "rb").read(),file_name="bom_data_template.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        upload_data = st.file_uploader("请选择要上传的文件：",type=["xlsx"],key="bom_data_upload")
        try:
            if upload_data is not None:
                df = pd.read_excel(upload_data,sheet_name="BOM")
                if len(df) == 0:
                    st.error("上传文件为空！")
                else:
                    # st.dataframe(df)
                    st.success("文件已上传！")
                    if st.button("导入数据",type="primary",key="bom_data_upload_button"):
                        progress_text = "数据导入中，请稍等..."
                        my_bar = st.progress(0, text=progress_text)
                        error_list = []
                        for i in range(len(df)):
                            sap_code = str(df.iloc[i]["物料"])
                            sap_dc = str(df.iloc[i]["物料描述"])
                            sap_pc = str(df.iloc[i]["BOM组件"])
                            sap_pc_dc = str(df.iloc[i]["组件描述"])
                            # print(sap_code,sap_dc,sap_pc,sap_pc_dc)
                            if len(sap_code) != 10 or len(sap_pc) != 10 :
                                st.error(f"第{i}行数据错误，请核对相关数据后再此尝试！")
                                error_list.append([sap_code,sap_dc,sap_pc,sap_pc_dc,"数据错误"])
                            else:
                                error_list = bom_record_add_lotsize(conn, sap_code,sap_dc,sap_pc,sap_pc_dc,error_list)
                            my_bar.progress((i+1)/len(df), text=progress_text)
                        my_bar.empty()
                        if len(df)-len(error_list) != 0:
                            st.success(f"共{len(df)-len(error_list)}条数据导入成功！")            
                        if len(error_list) != 0:
                            st.error(f"共{len(error_list)}条数据导入失败！清单如下：")
                            df_error = pd.DataFrame(error_list,columns=["物料","物料描述","BOM组件","组件描述","错误信息"])
                            st.dataframe(df_error,hide_index=True)

        except:
            st.error("上传文件格式错误！请使用指定模板上传！")


