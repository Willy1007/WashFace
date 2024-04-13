import pymysql, json, configparser


config = configparser.ConfigParser()
config.read('config.ini')

host = config.get('mysql', 'host')
port = int(config.get('mysql', 'port'))
user = config.get('mysql', 'user')
passwd = config.get('mysql', 'passwd')
db = config.get('mysql', 'db')
charset = config.get('mysql', 'charset')
end_point = config.get('line-bot', 'end_point')


conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
print('Successfully connected!')
cursor = conn.cursor()
sql = f"""
Select ID, marks, info_url, imgs from info_table;
"""
cursor.execute(sql)
datas = cursor.fetchall()
cursor.close()
conn.close()

mark = {}
urls = {}
imgs = {}

for data in datas:
    mark[data[0]] = data[1]
    urls[data[0]] = data[2]
    imgs[data[0]] = data[3]



def select_1(product_id):
    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
    print('Successfully connected!')
    cursor = conn.cursor()

    sql = f"""
    select Name_id, Name, Avg_score, Effect, Advantage, Defect, Push01, Push02, Push03 from Table01
    where Name_id = {product_id};
    """
    cursor.execute(sql)
    data = cursor.fetchone()

    cursor.close()
    conn.close()

    return data


def select_2(product_id, age_type):
    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
    print('Successfully connected!')
    cursor = conn.cursor()

    sql = f"""
    select {age_type}_score, {age_type}_effect from Table01
    where Name_id = {product_id};
    """
    cursor.execute(sql)
    data = cursor.fetchone()

    cursor.close()
    conn.close()

    return data


def stars_1(js, math):
    star = {
    "type": "icon",
    "size": "lg",
    "url": "https://imgur.com/ZCwfMp0.png"
    }

    starhelf = {
        "type": "icon",
        "size": "lg",
        "url": "https://imgur.com/eIiB8Qn.png"
    }

    starlast = {
        "type": "text",
        "text": f"{math}",
        "size": "sm",
        "margin": "md",
        "color": "#111111",
        "offsetTop": "none",
        "offsetBottom": "none",
        "offsetStart": "none",
        "offsetEnd": "none"
    }

    for i in range(int(math)):
        js["body"]["contents"][2]["contents"].append(star)

    num = int(math * 10 % 10)
    if num >= 7 and num <= 9:
        js["body"]["contents"][2]["contents"].append(star)
        js["body"]["contents"][2]["contents"].append(starlast)
    elif num >= 4 and num <= 6:
        js["body"]["contents"][2]["contents"].append(starhelf)
        js["body"]["contents"][2]["contents"].append(starlast)
    else:
        js["body"]["contents"][2]["contents"].append(starlast)

    return js


def stars_2(js, math, info_number):
    star = {
    "type": "icon",
    "size": "lg",
    "url": "https://imgur.com/ZCwfMp0.png"
    }

    starhelf = {
        "type": "icon",
        "size": "lg",
        "url": "https://imgur.com/eIiB8Qn.png"
    }

    starlast = {
        "type": "text",
        "text": f"{math}",
        "size": "sm",
        "margin": "md",
        "color": "#111111",
        "offsetTop": "none",
        "offsetBottom": "none",
        "offsetStart": "none",
        "offsetEnd": "none"
    }

    for i in range(int(math)):
        js['contents'][info_number]["body"]["contents"][2]["contents"].append(star)

    num = int(math * 10 % 10)
    if num >= 7 and num <= 9:
        js['contents'][info_number]["body"]["contents"][2]["contents"].append(star)
        js['contents'][info_number]["body"]["contents"][2]["contents"].append(starlast)
    elif num >= 4 and num <= 6:
        js['contents'][info_number]["body"]["contents"][2]["contents"].append(starhelf)
        js['contents'][info_number]["body"]["contents"][2]["contents"].append(starlast)
    else:
        js['contents'][info_number]["body"]["contents"][2]["contents"].append(starlast)

    return js


def load_js1(data):
    with open('v1.json', mode='r', encoding='utf-8') as fi:
        js = json.load(fi)

    math = data[2]
    js = stars_1(js, math)

    js["body"]["contents"][0]["text"] = mark[data[0]]  # 品牌
    js['body']['contents'][1]['text'] = data[1]  # 商品名稱
    js['body']['contents'][3]['contents'][0]['contents'][1]['text'] = data[3]  # 效果
    js['body']['contents'][3]['contents'][1]['contents'][1]['text'] = data[4] # 優點
    js["body"]["contents"][3]["contents"][1]["contents"][2]["contents"][1]["text"] = data[5] # 缺點
    js['footer']['contents'][1]['action']['text'] = f"推薦:{data[1]}"  # 推薦商品
    js['hero']['url'] = imgs[data[0]]  # 圖片
    js['footer']['contents'][0]['action']['uri'] = urls[data[0]]  # 網址
    
    return js


def load_js2(data):
    with open('v2.json', mode='r', encoding='utf-8') as fi:
        js = json.load(fi)

    for info_number in range(3):
        math = data[info_number][2]
        js = stars_2(js, math, info_number)

        js['contents'][info_number]["body"]["contents"][0]["text"] = mark[data[info_number][0]]  # 品牌
        js['contents'][info_number]['body']['contents'][1]['text'] = data[info_number][1]  # 商品名稱
        js['contents'][info_number]['body']['contents'][3]['contents'][0]['contents'][1]['text'] = data[info_number][3]  # 效果
        js['contents'][info_number]['body']['contents'][3]['contents'][1]['contents'][1]['text'] = data[info_number][4] # 優點
        js['contents'][info_number]["body"]["contents"][3]["contents"][1]["contents"][2]["contents"][1]["text"] = data[info_number][5] # 缺點
        js['contents'][info_number]['footer']['contents'][1]['action']['text'] = f"推薦:{data[info_number][1]}"  # 推薦商品
        js['contents'][info_number]['hero']['url'] = imgs[data[info_number][0]]  # 圖片
        js['contents'][info_number]['footer']['contents'][0]['action']['uri'] = urls[data[info_number][0]]  # 網址
    
    return js


def push_db(id_tp):
    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
    print('Successfully connected!')
    cursor = conn.cursor()

    sql = f"""
    select Name_id, Name, Avg_score, Effect, Advantage, Defect from Table01
    where Name_id = {id_tp[0]} or Name_id = {id_tp[1]} or Name_id = {id_tp[2]};
    """
    cursor.execute(sql)
    data = cursor.fetchall()

    info = []
    for i in id_tp:
        for x in range(3):
            if data[x][0] == i:
                info.append((data[x]))  # 調整排序問題

    cursor.close()
    conn.close()

    return info


def get_info_dict():
    conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
    print('Successfully connected!')
    cursor = conn.cursor()

    sql = f"""
    Select ID, info_name from info_table;
    """
    cursor.execute(sql)
    datas = cursor.fetchall()
    cursor.close()
    conn.close()

    info_dict ={}
    for data in datas:
        info_dict[data[1]] = data[0]

    return info_dict
