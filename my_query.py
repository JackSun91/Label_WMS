import pandas as pd
import streamlit as st
from datetime import datetime

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def user_query(conn):
    sql = "select * from user"
    cursor = conn.cursor()
    cursor.execute(sql)
    credentials = cursor.fetchall()

    # 写入字典
    credentials = {
        'usernames': {
            user[0]: {
                'email': user[1],
                'logged_in': False,  # 这里假设所有用户都未登录，可以根据实际情况修改
                'name': user[3],
                'password': user[4]
            } for user in credentials
        }
    }

    return credentials

def dc_df_query(conn):
    sql = "select * from bom"
    cursor = conn.cursor()
    cursor.execute(sql)
    record = cursor.fetchall()
    
    # 读取数据库中的列名并储存至列表中
    description = cursor.description
    column_list = [column[0] for column in description]

    # 输出带有列名的数据库中的表
    df = pd.DataFrame(record, columns=column_list)
    return df


def dc_query(conn, sap_code):
    sql = "select * from bom where 物料=?"
    cursor = conn.cursor()
    cursor.execute(sql, (sap_code,))
    record = cursor.fetchall()

    # 读取数据库中的列名并储存至列表中
    description = cursor.description
    column_list = [column[0] for column in description]

    # 输出带有列名的数据库中的表
    df = pd.DataFrame(record, columns=column_list)
    return df


def lb_df_query(conn):
    sql = "select * from master_data"
    cursor = conn.cursor()
    cursor.execute(sql)
    record = cursor.fetchall()
    
    # 读取数据库中的列名并储存至列表中
    description = cursor.description
    column_list = [column[0] for column in description]

    # 输出带有列名的数据库中的表
    df = pd.DataFrame(record, columns=column_list)
    return df



def lb_query(conn, sap_pc, channel, origin):
    sql = "select * from master_data where sap_pc='%s' and chanel='%s' and origin='%s'" % (sap_pc, channel, origin)
    cursor = conn.cursor()
    cursor.execute(sql)
    record = cursor.fetchall()

    # 读取数据库中的列名并储存至列表中  
    description = cursor.description
    column_list = [column[0] for column in description] 

    # 输出带有列名的数据库中的表
    df = pd.DataFrame(record, columns=column_list)
    return df


#在数据库lwms表master_data中创建新记录
def master_record_add(conn,sap_code,sap_pc,sap_dc,chanel,origin,lb_code,lb_dc,start_stock,start_location,current_user):
    if sap_code == "":
        sap_code = 0    
    try:
        sql = """
        INSERT INTO master_data (sap_code, sap_pc, sap_dc, chanel, origin, label_code, label_dc, start_stock,start_location, create_time, create_user)  
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)  
        """
        cursor = conn.cursor()
        cursor.execute(sql, (sap_code, sap_pc, sap_dc, chanel,origin, lb_code, lb_dc, start_stock,start_location, current_time, current_user))
        conn.commit()
        st.toast("记录已添加成功！")
    except Exception as e:
        st.toast(f"记录添加失败，错误代码: {e}")
        conn.rollback()


def master_record_update(conn, sap_code,sap_pc,sap_dc,chanel,origin,lb_code,lb_dc,start_stock,start_location,current_user):
    if sap_code == "":
        sap_code = 0
    try:
        sql = """
        UPDATE master_data
        SET sap_code=?, sap_pc=?, sap_dc=?, chanel=?, origin=?, label_code=?, label_dc=?, start_stock=? ,start_location=?, create_user=?
        WHERE sap_pc=? and chanel=? and origin=?
        """
        cursor = conn.cursor()
        cursor.execute(sql, (sap_code, sap_pc, sap_dc, chanel, origin,lb_code, lb_dc, start_stock, start_location, current_user, sap_pc, chanel, origin))
        conn.commit()
        st.toast("记录已修改成功！")        
    except Exception as e:
        st.toast(f"记录修改失败，错误代码: {e}")
        conn.rollback()


def master_record_delete(conn, sap_pc,chanel, origin):   
    try:
        sql = """
        DELETE FROM master_data
        WHERE sap_pc=? and chanel=? and origin=?
        """  
        cursor = conn.cursor()
        # 执行SQL语句  
        cursor.execute(sql, (sap_pc, chanel, origin))  
        # 提交事务  
        conn.commit()
        st.toast("记录已删除成功！")         
    except Exception as e:  
        #print(f"Error: {e}")
        st.toast(f"记录删除失败，错误代码: {e}")   
        # 如果发生错误，回滚事务  
        conn.rollback()

def bom_record_add(conn, sap_code,sap_dc,sap_pc,sap_pc_dc):    
    try:
        sql = """
        INSERT INTO bom (物料, 物料描述, BOM组件, 组件描述)
        VALUES (?, ?, ?, ?)  
        """
        cursor = conn.cursor()
        # 执行SQL语句  
        cursor.execute(sql,(sap_code,sap_dc,sap_pc,sap_pc_dc))  
        # 提交事务  
        conn.commit()
        st.toast("记录已添加成功！")
    except Exception as e:  
        print(f"Error: {e}")
        st.toast(f"记录添加失败，错误代码: {e}")
        # 如果发生错误，回滚事务  
        conn.rollback()  

def bom_record_update(conn, sap_code,sap_dc,sap_pc,sap_pc_dc):    
    try:
        sql = """ 
        UPDATE bom
        SET 物料=?, 物料描述=?, BOM组件=?, 组件描述=?
        WHERE 物料=?
        """ 
        cursor = conn.cursor()              
        # 执行SQL语句  
        cursor.execute(sql, (sap_code,sap_dc,sap_pc,sap_pc_dc,sap_code))  
        # 提交事务  
        conn.commit()
        st.toast("记录已修改成功！")         
    except Exception as e:  
        #print(f"Error: {e}")
        st.toast(f"记录修改失败，错误代码: {e}")
        # 如果发生错误，回滚事务  
        conn.rollback()  

def bom_record_delete(conn, sap_code):   
    try:
        sql = """
        DELETE FROM bom
        WHERE 物料=?
        """
        cursor = conn.cursor()  
        # 执行SQL语句  
        cursor.execute(sql, (sap_code,))  
        # 提交事务  
        conn.commit()
        st.toast("记录已删除成功！")         
    except Exception as e:  
        #print(f"Error: {e}")
        st.toast(f"记录删除失败，错误代码: {e}")   
        # 如果发生错误，回滚事务  
        conn.rollback()  

def bom_record_add_lotsize(conn, sap_code,sap_dc,sap_pc,sap_pc_dc,error_list):
    try:
        sql = """  
        INSERT INTO bom (物料, 物料描述, BOM组件, 组件描述)  
        VALUES (?, ?, ?, ?)    
        """
        cursor = conn.cursor()
        cursor.execute(sql, (sap_code, sap_dc, sap_pc, sap_pc_dc))  
        conn.commit()            

    except Exception as e:  
        error_list.append([sap_code, sap_dc, sap_pc, sap_pc_dc, str(e)])  
        conn.rollback()  
    
    return error_list


def inbound_record_add(conn, sap_pc, sap_pc_dc, brand, channel,origin, lb_code, lb_dc, inbound_num, inbound_location, inbound_type, inbound_remark, current_user):  
    try:
        sql = """  
        INSERT INTO inbound_data (sap_pc,sap_pc_dc,brand,channel,origin,lb_code,lb_dc,inbound_num,inbound_location,inbound_type,inbound_remark,inbound_time,inbound_user)  
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)    
        """
        cursor = conn.cursor()  
        cursor.execute(sql, (sap_pc, sap_pc_dc, brand, channel,origin, lb_code, lb_dc, inbound_num, inbound_location, inbound_type, inbound_remark, current_time, current_user))  
        conn.commit()
        st.toast("记录已添加成功！")           
    except Exception as e:  
        st.toast(f"记录添加失败，错误代码: {e}")  
        conn.rollback()
        # return f"记录添加失败，错误代码: {e}"  
    # 注意：没有 finally 块，因为 with 语句会自动关闭游标

def inbound_record_add_lotsize(conn,sap_pc,sap_pc_dc,brand,channel,origin,lb_code,lb_dc,inbound_num,inbound_location,inbound_type,inbound_remark,current_user,error_list):
    try:
        sql = """
        INSERT INTO inbound_data (sap_pc,sap_pc_dc,brand,channel,origin,lb_code,lb_dc,inbound_num,inbound_location,inbound_type,inbound_remark,inbound_time,inbound_user)
        VALUES (?, ?, ?, ?,?, ?, ?, ?, ?, ?, ?, ?, ?)  
        """
        cursor = conn.cursor()       
        # 执行SQL语句  
        cursor.execute(sql, (sap_pc,sap_pc_dc,brand,channel,origin, lb_code,lb_dc,inbound_num,inbound_location,inbound_type,inbound_remark,current_time,current_user))  
        # 提交事务  
        conn.commit()
        # st.toast("记录已添加成功！") 

    except Exception as e:  
        # st.toast(f"记录添加失败，错误代码: {e}")
        error_list.append([sap_pc,sap_pc_dc,brand,channel,origin,lb_code,lb_dc,inbound_num,inbound_location,inbound_type,inbound_remark,e])
        # 如果发生错误，回滚事务  
        conn.rollback()  
    # 注意：没有 finally 块，因为 with 语句会自动关闭游标
    
    return error_list

def inbound_record_query(conn, sap_code, channel, origin, start_date, end_date, lb_code, lb_dc, brand, inbound_type):
    try:
        sql = """  
        SELECT * FROM inbound_data WHERE sap_pc=? and channel=? and origin=? and lb_code=? and lb_dc=? and brand=? and inbound_type=? and inbound_time BETWEEN ? AND ?
        """
        cursor = conn.cursor()  
        cursor.execute(sql, (sap_code, channel, origin, lb_code, lb_dc, brand, inbound_type, start_date, end_date))
        data = cursor.fetchall()
        # 读取数据库中的列名并储存至列表中
        description = cursor.description
        column_list = [column[0] for column in description]
        # 输出带有列名的数据库中的表            
        df = pd.DataFrame(data, columns=column_list)
        st.toast("记录已查询成功！") 
        #return "记录已添加成功！"   
    except Exception as e:  
        st.toast(f"记录添加失败，错误代码: {e}")  
        conn.rollback()
    return df

def inbound_df_query(conn):
    try:
        sql = """  
        SELECT * FROM inbound_data
        """
        cursor = conn.cursor()  
        cursor.execute(sql)
        data = cursor.fetchall()
        # 读取数据库中的列名并储存至列表中
        description = cursor.description
        column_list = [column[0] for column in description]
        # 输出带有列名的数据库中的表            
        df = pd.DataFrame(data, columns=column_list)
        #st.toast("记录已查询成功！") 
        #return "记录已添加成功！"    
    except Exception as e:
        st.toast(f"记录添加失败，错误代码: {e}")  
        conn.rollback()
    return df


def inbound_df_query_with_filter(conn, sap_pc, channel, origin, start_date, end_date, brand, inbound_type):
    formatted_channel = ", ".join([f"'{value}'" for value in channel])
    formatted_channel = f"({formatted_channel})"

    formatted_brand = ", ".join([f"'{value}'" for value in brand])
    formatted_brand = f"({formatted_brand})"

    formatted_origin = ", ".join([f"'{value}'" for value in origin])
    formatted_origin = f"({formatted_origin})"

    formatted_inbound_type = ", ".join([f"'{value}'" for value in inbound_type])
    formatted_inbound_type = f"({formatted_inbound_type})"
    try:
        cursor = conn.cursor()
        if len(sap_pc) == 0:
            sql = f"""  
            SELECT * FROM inbound_data WHERE channel IN {formatted_channel} AND brand IN {formatted_brand} AND origin IN {formatted_origin} AND inbound_type IN {formatted_inbound_type} AND inbound_time >= ? AND inbound_time <= ?
            """
            cursor.execute(sql,(start_date,end_date))
        elif len(sap_pc) == 10:
            sql = f"""
            SELECT * FROM inbound_data WHERE sap_pc = ? AND channel IN {formatted_channel} AND brand IN {formatted_brand} AND origin IN {formatted_origin} AND inbound_type IN {formatted_inbound_type} AND inbound_time >= ? AND inbound_time <= ?
            """
            cursor.execute(sql,(sap_pc,start_date,end_date))
        data = cursor.fetchall()
        # 读取数据库中的列名并储存至列表中
        description = cursor.description
        column_list = [column[0] for column in description]
        # 输出带有列名的数据库中的表            
        df = pd.DataFrame(data, columns=column_list)
        # print(df)

    except Exception as e:
        st.toast(f"记录添加失败，错误代码: {e}")  
        conn.rollback()

    return df   




def outbound_record_add(conn, sap_pc, sap_pc_dc, brand, channel,origin, lb_code, lb_dc, outbound_num, outbound_location, outbound_type, outbound_remark, current_user):  
    try:
        sql = """  
        INSERT INTO outbound_data (sap_pc,sap_pc_dc,brand,channel,origin,lb_code,lb_dc,outbound_num,outbound_location,outbound_type,outbound_remark,outbound_time,outbound_user)  
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)    
        """
        cursor = conn.cursor()  
        cursor.execute(sql, (sap_pc, sap_pc_dc, brand, channel,origin, lb_code, lb_dc, outbound_num, outbound_location, outbound_type, outbound_remark, current_time, current_user))  
        conn.commit()
        st.toast("记录已添加成功！") 
    except Exception as e:  
        st.toast(f"记录添加失败，错误代码: {e}")  
        conn.rollback()

def outbound_record_add_lotsize(conn,sap_pc,sap_pc_dc,brand,channel,origin,lb_code,lb_dc,outbound_num,outbound_location,outbound_type,outbound_remark,current_user,error_list):
    try:
        sql = """
        INSERT INTO outbound_data (sap_pc,sap_pc_dc,brand,channel,origin,lb_code,lb_dc,outbound_num,outbound_location,outbound_type,outbound_remark,outbound_time,outbound_user)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)  
        """       
        cursor = conn.cursor()
        # 执行SQL语句  
        cursor.execute(sql, (sap_pc,sap_pc_dc,brand,channel,origin, lb_code,lb_dc,outbound_num,outbound_location,outbound_type,outbound_remark,current_time,current_user))  
        # 提交事务  
        conn.commit()
    except Exception as e:  
        # st.toast(f"记录添加失败，错误代码: {e}")
        error_list.append([sap_pc,sap_pc_dc,brand,channel,origin,lb_code,lb_dc,outbound_num,outbound_location,outbound_type,outbound_remark,e])
        # 如果发生错误，回滚事务  
        conn.rollback()

    return error_list

def outbound_df_query(conn):
    try:
        sql = """  
        SELECT * FROM outbound_data
        """
        cursor = conn.cursor()  
        cursor.execute(sql)
        data = cursor.fetchall()
        # 读取数据库中的列名并储存至列表中
        description = cursor.description
        column_list = [column[0] for column in description]
        # 输出带有列名的数据库中的表            
        df = pd.DataFrame(data, columns=column_list)
        #st.toast("记录已查询成功！") 
        #return "记录已添加成功！"    

    except Exception as e:
        st.toast(f"记录添加失败，错误代码: {e}")  
        conn.rollback()
    return df

def outbound_df_query_with_filter(conn, sap_pc, channel, origin, start_date, end_date, brand, outbound_type):
    formatted_channel = ", ".join([f"'{value}'" for value in channel])
    formatted_channel = f"({formatted_channel})"

    formatted_brand = ", ".join([f"'{value}'" for value in brand])
    formatted_brand = f"({formatted_brand})"

    formatted_origin = ", ".join([f"'{value}'" for value in origin])
    formatted_origin = f"({formatted_origin})"

    formatted_outbound_type = ", ".join([f"'{value}'" for value in outbound_type])
    formatted_outbound_type = f"({formatted_outbound_type})"    
    try:  
        cursor =conn.cursor()
        if len(sap_pc) == 0:
            sql = f"""  
            SELECT * FROM outbound_data WHERE channel IN {formatted_channel} AND origin IN {formatted_origin} AND brand IN {formatted_brand} AND outbound_type IN {formatted_outbound_type} AND outbound_time >= ? AND outbound_time <= ?
            """
            cursor.execute(sql,(start_date,end_date))
        elif len(sap_pc) == 10:
            sql = f"""
            SELECT * FROM outbound_data WHERE sap_pc = ? AND channel IN {formatted_channel} AND origin IN {formatted_origin} AND brand IN {formatted_brand} AND outbound_type IN {formatted_outbound_type} AND outbound_time >= ? AND outbound_time <= ?
            """
            cursor.execute(sql,(sap_pc,start_date,end_date))
        data = cursor.fetchall()
        # 读取数据库中的列名并储存至列表中
        description = cursor.description
        column_list = [column[0] for column in description]
        # 输出带有列名的数据库中的表            
        df = pd.DataFrame(data, columns=column_list)
    except Exception as e:
        st.toast(f"记录添加失败，错误代码: {e}")  
        conn.rollback()

    return df  

def stock_record_add(conn, sap_pc, channel, origin, lb_code, lb_dc, start_stock, start_location,move_type,current_user):
    try:
        cursor =conn.cursor()
        sql = """
        INSERT INTO stock (sap_pc, channel, origin, lb_code, lb_dc, num, location, move_type, record_time, record_user)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql, (sap_pc, channel, origin, lb_code, lb_dc, start_stock, start_location, move_type, current_time, current_user))
        conn.commit()
        #st.toast("记录已添加成功！")
    except Exception as e:
        st.toast(f"记录添加失败，错误代码: {e}")
        conn.rollback()

def stock_record_update(conn, sap_pc, channel, origin, lb_code, lb_dc, start_stock, start_location, current_user):

    try:
        cursor = conn.cursor()
        sql = """
        UPDATE stock
        SET sap_pc=?, channel=?, origin=?, lb_code=?, lb_dc=?, num=? ,location=?, record_user=?
        WHERE sap_pc=? and channel=? and origin=? and move_type="期初库存"
        """        
        # 执行SQL语句  
        cursor.execute(sql, (sap_pc, channel, origin, lb_code, lb_dc, start_stock, start_location, current_user, sap_pc, channel,origin))  
        # 提交事务  
        conn.commit()
        st.toast("记录已修改成功！") 
    except Exception as e:  
        #print(f"Error: {e}")
        st.toast(f"记录修改失败，错误代码: {e}")   
        # 如果发生错误，回滚事务  
        conn.rollback()

def master_record_delete(conn, sap_pc,channel,origin):   
    try:
        cursor = conn.cursor()
        sql = """
        DELETE FROM stock
        WHERE sap_pc=? and channel=? and origin=? and move_type="期初库存"
        """  
        # 执行SQL语句  
        cursor.execute(sql, (sap_pc, channel,origin))  
        # 提交事务  
        conn.commit()
        st.toast("记录已删除成功！") 
    except Exception as e:  
        #print(f"Error: {e}")
        st.toast(f"记录删除失败，错误代码: {e}")   
        # 如果发生错误，回滚事务  
        conn.rollback()

# 添加出库记录
def stock_record_remove(conn, sap_pc, channel,origin, lb_code, lb_dc, start_stock, start_location,move_type,current_user):
    try:
        cursor = conn.cursor()
        sql = """
        INSERT INTO stock (sap_pc, channel, origin, lb_code, lb_dc, num, location, move_type,record_time,record_user)
        VALUES (?, ?, ?, ?, ?, 0-?, ?, ?, ?, ?)
        """
        cursor.execute(sql, (sap_pc, channel, origin, lb_code, lb_dc, start_stock, start_location, move_type,current_time, current_user))
        conn.commit()
        #st.toast("记录已添加成功！")
    except Exception as e:
        st.toast(f"记录添加失败，错误代码: {e}")
        conn.rollback()

def stock_df_query(conn):
    try:  
        cursor = conn.cursor()
        sql = """  
        SELECT * FROM stock_total
        """  
        cursor.execute(sql)
        data = cursor.fetchall()
        # 读取数据库中的列名并储存至列表中
        description = cursor.description
        column_list = [column[0] for column in description]
        # 输出带有列名的数据库中的表            
        df = pd.DataFrame(data, columns=column_list)
        #st.toast("记录已查询成功！") 
        #return "记录已添加成功！"  
    except Exception as e:
        st.toast(f"记录添加失败，错误代码: {e}")  
        conn.rollback()
    return df

#需要重点核查，目前没有改造完
def stock_df_query_with_filter(conn, sap_pc, lb_code,channel, brand, origin):
    formatted_channel = ", ".join([f"'{value}'" for value in channel])
    formatted_channel = f"({formatted_channel})"

    formatted_brand = ", ".join([f"'{value}'" for value in brand])  
    formatted_brand = f"({formatted_brand})"

    formatted_origin = ", ".join([f"'{value}'" for value in origin])
    formatted_origin = f"({formatted_origin})"
    try:  
        cursor =conn.cursor()
        if len(sap_pc) == 0 and len(lb_code) == 0:
            sql = f"""  
            SELECT * FROM stock_total WHERE channel IN {formatted_channel} AND brand IN {formatted_brand} AND origin IN {formatted_origin}
            """
            cursor.execute(sql)
        elif len(sap_pc) == 10 and len(lb_code) == 0:
            sql = f"""
            SELECT * FROM stock_total WHERE channel IN {formatted_channel} AND brand IN {formatted_brand} AND origin IN {formatted_origin} and sap_pc = ?
            """
            cursor.execute(sql,(sap_pc))
        elif len(sap_pc) == 0 and len(lb_code) == 12:
            sql = f"""
            SELECT * FROM stock_total WHERE channel IN {formatted_channel} AND brand IN {formatted_brand} AND origin IN {formatted_origin} and lb_code = ?
            """
            cursor.execute(sql,(lb_code))
        elif len(sap_pc) == 10 and len(lb_code) == 12:
            sql = f"""
            SELECT * FROM stock_total WHERE channel IN {formatted_channel} AND brand IN {formatted_brand} AND origin IN {formatted_origin} and sap_pc = ? and lb_code = ?
            """
            cursor.execute(sql,(sap_pc,lb_code))
        data = cursor.fetchall()
        # 读取数据库中的列名并储存至列表中
        description = cursor.description
        column_list = [column[0] for column in description]
        # 输出带有列名的数据库中的表            
        df = pd.DataFrame(data, columns=column_list)

    except Exception as e:
        st.toast(f"记录添加失败，错误代码: {e}")  
        conn.rollback()

    return df    



def inbound_record_update(conn,sap_pc,sap_dc,brand,channel,origin,lb_code,lb_dc,start_stock,start_location,current_user):
    try:
        cursor = conn.cursor()
        sql = """
        UPDATE inbound_data
        SET sap_pc=?, sap_pc_dc=?, brand=?, channel=?, origin=?, lb_code=?, lb_dc=?, inbound_num=? ,inbound_location=?, inbound_user=?
        WHERE sap_pc=? and channel=? and origin=? and inbound_type="期初库存"
        """        
        # 执行SQL语句  
        cursor.execute(sql, (sap_pc,sap_dc,brand,channel,origin,lb_code,lb_dc,start_stock,start_location,current_user, sap_pc, channel,origin))  
        # 提交事务  
        conn.commit()
        st.toast("记录已修改成功！") 
    except Exception as e:  
        #print(f"Error: {e}")
        st.toast(f"记录修改失败，错误代码: {e}")   
        # 如果发生错误，回滚事务  
        conn.rollback()

def stock_add_lotsize(conn, sap_pc, channel, origin, lb_code, lb_dc, start_stock, start_location,move_type,current_user):
    try:
        cursor = conn.cursor()
        sql = """
        INSERT INTO stock (sap_pc, channel, origin, lb_code, lb_dc, num, location, move_type,record_time,record_user)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql, (sap_pc, channel, origin,lb_code, lb_dc, start_stock, start_location, move_type,current_time,current_user))
        conn.commit()
        #st.toast("记录已添加成功！")
    except Exception as e:   
        conn.rollback()  
    
