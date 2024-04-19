import pymysql, configparser


config = configparser.ConfigParser()
config.read('config.ini')

host = config.get('mysql', 'host')
port = int(config.get('mysql', 'port'))
user = config.get('mysql', 'user')
passwd = config.get('mysql', 'passwd')
db = config.get('mysql', 'db')
charset = config.get('mysql', 'charset')


conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
cursor = conn.cursor()
sql0 = f"""
Select ID, info_name from info_table;
"""
cursor.execute(sql0)
datas = cursor.fetchall()
info_dict = {}
for data in datas:
    info_dict[data[1]] = data[0]



def select_1(product_id):
    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
    cursor = conn.cursor()

    sql1 = f"""
    select Name, Avg_score, Effect, Advantage, Defect from Table01
    where Name_id = {product_id};
    """
    cursor.execute(sql1)
    data1 = cursor.fetchone()

    sql2 = f"""
    select marks from info_table
    where ID = {product_id};
    """
    cursor.execute(sql2)
    data2 = cursor.fetchone()

    data = data2 + data1
    cursor.close()
    conn.close()

    return data


def select_2(pid, age_type):
    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
    cursor = conn.cursor()

    sql = f"""
    select {age_type}_score, {age_type}_effect from Table01
    where Name_id = {pid};
    """
    cursor.execute(sql)
    data = cursor.fetchone()

    cursor.close()
    conn.close()

    return data


def pushdata(pid):
    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
    cursor = conn.cursor()

    sql1 = f"""
    select Push01, Push02, Push03 from Table01
    where Name_id = {pid};
    """
    cursor.execute(sql1)
    pushs = cursor.fetchone()

    push_ids = (info_dict[pushs[0]], info_dict[pushs[1]], info_dict[pushs[2]])

    sql2 = f"""
    select Name_id, Name, Avg_score, Effect, Advantage, Defect from Table01
    where Name_id = {push_ids[0]} or Name_id = {push_ids[1]} or Name_id = {push_ids[2]};
    """
    cursor.execute(sql2)
    id_data = cursor.fetchall()

    info = []
    for i in push_ids:
        for x in range(3):
            if id_data[x][0] == i:
                info.append((id_data[x]))  # 調整排序問題

    cursor.close()
    conn.close()
    
    return info
