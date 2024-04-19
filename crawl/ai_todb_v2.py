import pymysql, jieba, datetime, configparser


config = configparser.ConfigParser()
config.read('config.ini')

host = config.get('mysql', 'host')
port = int(config.get('mysql', 'port'))
user = config.get('mysql', 'user')
passwd = config.get('mysql', 'passwd')
db = config.get('mysql', 'db')
charset = config.get('mysql', 'charset')


def jb_sort(sb):
    jieba.load_userdict("mydict.txt")
    word_cut_grt = jieba.cut(sb)
    word_cut_list = [
        w for w in word_cut_grt if len(w) > 1
    ]

    wd_dict = {}
    for wd in word_cut_list:
        if wd in wd_dict:
            wd_dict[wd] += 1
        else:
            wd_dict[wd] = 1

    wd_con_list = []
    for k, v in wd_dict.items():
        wd_con_list.append((k, v))
    wd_con_list.sort(key=lambda x: x[1], reverse=True)
    top3 = ""
    ts = 0
    for top in wd_con_list:
        if ts < 2:
            top3 += top[0] + "、"
            ts += 1
        else:
            top3 += top[0]
            break
    return top3


def tb1_insert(naid, item_dict):
    A_sco = {}
    B_sco = {}
    C_sco = {}
    D_sco = {}
    A_eff = {}
    B_eff = {}
    C_eff = {}
    D_eff = {}
    score_list = [A_sco, B_sco, C_sco, D_sco]
    effect_list = [A_eff, B_eff, C_eff, D_eff]
    age_range = ["Age <= 20", "Age between 21 and 30", "Age between 31 and 45", "Age >= 46"]
    type_list = ["乾性肌膚", "油性肌膚", "敏感性肌膚", "混合性肌膚"]

    try:
        conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
        print('Successfully connected!')
        cursor = conn.cursor()
        # 總均分
        Avg_score_sql = f"""
        select ROUND(AVG(Score), 1) from Table02
        where Name_id = {naid}
        """
        cursor.execute(Avg_score_sql)
        Avg_score = cursor.fetchone()

        # 總效果
        Effect_sql = f"""
        select Name_id, Con2 from Table02
        where Name_id = {naid};
        """
        cursor.execute(Effect_sql)
        effect_all = cursor.fetchall()
        eff = ""
        for ts in effect_all:
            if ts[1] != "":
                eff += ts[1] + "、"
        tb1_effect = jb_sort(eff)


        for sco, eff, ran in zip(score_list, effect_list, age_range):
            for tp in type_list:
                sc = f"""
                select Skin_type, ROUND(AVG(Score), 1) from Table02
                where Name_id = {naid} and {ran}
                group by Skin_type
                having Skin_type = "{tp}"
                """
                cursor.execute(sc)
                score = cursor.fetchone()
                if score != None:
                    sco[tp] = float(score[1])
                else:
                    sco[tp] = None


                ef = f"""
                select Skin_type, Con2 from Table02
                where Name_id = {naid} and {ran} and Skin_type = "{tp}";
                """
                cursor.execute(ef)
                effect = cursor.fetchall()
                if len(effect) == 0:
                    eff[tp] = None
                else:
                    sb = ""
                    for ts in effect:
                        if ts[1] != "":
                            sb += ts[1] + "、"
                    
                    if sb == "":
                        eff[tp] = None
                    else:
                        eff[tp] = jb_sort(sb)
     

        tba = (naid, item_dict[naid], float(Avg_score[0]), tb1_effect,
            A_sco["乾性肌膚"], A_sco["油性肌膚"], A_sco["敏感性肌膚"], A_sco["混合性肌膚"],
            B_sco["乾性肌膚"], B_sco["油性肌膚"], B_sco["敏感性肌膚"], B_sco["混合性肌膚"],
            C_sco["乾性肌膚"], C_sco["油性肌膚"], C_sco["敏感性肌膚"], C_sco["混合性肌膚"],
            D_sco["乾性肌膚"], D_sco["油性肌膚"], D_sco["敏感性肌膚"], D_sco["混合性肌膚"],
            A_eff["乾性肌膚"], A_eff["油性肌膚"], A_eff["敏感性肌膚"], A_eff["混合性肌膚"],
            B_eff["乾性肌膚"], B_eff["油性肌膚"], B_eff["敏感性肌膚"], B_eff["混合性肌膚"],
            C_eff["乾性肌膚"], C_eff["油性肌膚"], C_eff["敏感性肌膚"], C_eff["混合性肌膚"],
            D_eff["乾性肌膚"], D_eff["油性肌膚"], D_eff["敏感性肌膚"], D_eff["混合性肌膚"]
        )
        sqla = """
        INSERT INTO Table01 (Name_id, Name, Avg_score, Effect,
                            A1_score, A2_score, A3_score, A4_score,
                            B1_score, B2_score, B3_score, B4_score,
                            C1_score, C2_score, C3_score, C4_score,
                            D1_score, D2_score, D3_score, D4_score,
                            A1_effect, A2_effect, A3_effect, A4_effect,
                            B1_effect, B2_effect, B3_effect, B4_effect,
                            C1_effect, C2_effect, C3_effect, C4_effect,
                            D1_effect, D2_effect, D3_effect, D4_effect)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        cursor.execute(sqla, tba)
        conn.commit()
        cursor.close()
        conn.close()
        print("Table01新增成功")
    except Exception:
        print("Table01新增失敗")


def tb1_del(naid):
    try:
        conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
        print('Successfully connected!')
        cursor = conn.cursor()
        sql_del = f"""
        delete from Table01
        where Name_id = {naid};
        """
        cursor.execute(sql_del)
        conn.commit()
        cursor.close()
        conn.close()
        print("Table01刪除成功")
    except Exception:
        print("Table01刪除失敗")


def tb2_db(tb2):
    try:
        conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
        print('Successfully connected!')
        cursor = conn.cursor()

        sql_insert = """
        INSERT INTO Table02 (Name_id, Skin_type, Score, Age, Content, Con2, Url, Date_ck)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """

        cursor.executemany(sql_insert, tb2)
        conn.commit()
        cursor.close()
        conn.close()
        print("Table02新增成功")
    except Exception:
        print("Table02新增失敗")


def updata_ck(naid):
    try:
        conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
        print('Successfully connected!')
        cursor = conn.cursor()

        sql = f"""
        select DATE_FORMAT(Date_ck, "%Y-%m-%d") from Table02
        where Name_id = {naid};
        """
        cursor.execute(sql)
        sn = cursor.fetchall()
        up_ck = False
        for i in sn:
            if i[0] == str(datetime.date.today()):
                up_ck = True
                break

        cursor.close()
        conn.close()
        if up_ck == True:
            print("有更新資料")
        else:
            print("無更新資料")
        return up_ck
    except Exception:
        print("比對失敗")


def get_ckurl(naid):
    try:
        conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
        print('Successfully connected!')
        cursor = conn.cursor()

        sql = f"""
        select Url from Table02
        where Name_id = {naid};
        """
        cursor.execute(sql)
        datas = cursor.fetchall()
        ck_url = []
        for data in datas:
            ck_url.append(data[0])
        
        cursor.close()
        conn.close()
        return ck_url
    except Exception:
        print("ck_url ERROR")


def get_info_table():
    try:
        conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
        print('Successfully connected!')
        cursor = conn.cursor()

        sql = f"""
        select ID, info_name, info_url from info_table;
        """
        cursor.execute(sql)
        datas = cursor.fetchall()

        cursor.close()
        conn.close()
        print("info_table 成功")
        return datas
    except Exception:
        print("info_table ERROR")

