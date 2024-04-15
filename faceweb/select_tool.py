import pymysql, configparser


config = configparser.ConfigParser()
config.read('config.ini')

host = config.get('mysql', 'host')
port = int(config.get('mysql', 'port'))
user = config.get('mysql', 'user')
passwd = config.get('mysql', 'passwd')
db = config.get('mysql', 'db')
charset = config.get('mysql', 'charset')



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


