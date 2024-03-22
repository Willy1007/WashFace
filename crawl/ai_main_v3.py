import requests
from bs4 import BeautifulSoup
import pandas as pd
import time, random, os, datetime
from ai_todb_v2 import tb1_insert, tb1_del, updata_ck, tb2_db


if not os.path.exists(os.path.join("data")):
    os.mkdir(os.path.join("data"))

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_info(url, ts, naid, ck_url):
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    
    info_links = soup.find_all("a", class_="review-content-top")
    ni_age_sts = soup.find_all("div", class_="author-review-status")
    scores = soup.find_all("div", class_="review-score")
  
    for info_link, ni_age_st, score in zip(info_links, ni_age_sts, scores):
        if score.text == "(淺層體驗)":
            print("Error PassInfo!!")
            continue
        if info_link.get("href") not in ck_url:
            links = "https://www.cosme.net.tw" + info_link.get("href")
            res_info = requests.get(links, headers=HEADERS)
            soup_info = BeautifulSoup(res_info.text, "html.parser")
            content = soup_info.find("div", class_="review-content")
            for extract_tag in content.find_all("div", class_="review-attributes"):
                sg = extract_tag.extract()
                sb = sg.text.split("・")[1].replace(" ", "").replace("效果：", "").replace("--", "")

            ages = ni_age_st.text.split("・")[1]

            tb2.append(
                (naid,                            # Name_id
                ni_age_st.text.split("・")[0],    # Skin_type
                int(score.text),                  # Score
                int(''.join(filter(str.isdigit, ages))), # Age
                content.text.replace(" ", "").replace("　", "").replace("    ", ""),    # Content
                sb,                               # Con2
                info_link.get("href"),            # Url
                datetime.date.today())
            )
        else:
            print(f"passssss")
            continue
    
        ts += 1
        print(f"page:{ts}")

    next_link = soup.find("a", class_="next_page")
    return ("https://cosme.net.tw" + next_link.get("href")) if next_link != None else None


urls = (
    'https://www.cosme.net.tw/products/87330/reviews',
    'https://www.cosme.net.tw/products/4989/reviews',
    'https://www.cosme.net.tw/products/85513/reviews',
    'https://www.cosme.net.tw/products/79415/reviews',
    'https://www.cosme.net.tw/products/40527/reviews',
    'https://www.cosme.net.tw/products/19398/reviews',
    'https://www.cosme.net.tw/products/79637/reviews',
    'https://www.cosme.net.tw/products/90191/reviews',
    'https://www.cosme.net.tw/products/105363/reviews',
    'https://www.cosme.net.tw/products/57958/reviews',
    'https://www.cosme.net.tw/products/67787/reviews',
    'https://www.cosme.net.tw/products/58118/reviews',
    'https://www.cosme.net.tw/products/89784/reviews',
    'https://www.cosme.net.tw/products/67788/reviews',
    'https://www.cosme.net.tw/products/36729/reviews',
    'https://www.cosme.net.tw/products/82073/reviews',
    'https://www.cosme.net.tw/products/82072/reviews',
    'https://www.cosme.net.tw/products/82074/reviews'
)


item_dict = {
    0: "超綿感泡泡保濕洗面乳",
    1: "青柚籽深層潔顏乳",
    2: "卵肌溫和去角質洗面乳",
    3: "極潤健康深層清潔調理洗面乳",
    4: "極潤保濕洗面乳",
    5: "豆乳美肌洗面乳",
    6: "草本調理淨化洗顏乳",
    7: "溫和保濕潔顏乳",
    8: "超微米胺基酸溫和潔顏慕絲",
    9: "淨白洗面乳",
    10: "溫和水嫩洗面乳",
    11: "透白勻亮洗面乳",
    12: "碧菲絲特毛孔淨透洗面乳",
    13: "清透極淨洗面乳",
    14: "海泥毛孔潔淨洗顏乳",
    15: "碧菲絲特抗暗沉碳酸泡洗顏",
    16: "碧菲絲特清爽碳酸泡洗顏",
    17: "碧菲絲特保濕碳酸泡洗顏"
}

columns = ["Name_id", "Skin_type", "Score", "Age", "Content", "Con2", "Url", "Date_ck"]

naid = 0
for url in urls:
    tb2 = []
    ck_url = []
    if os.path.exists(os.path.join('data', f'table02_No{naid}.csv')):
        checks = pd.read_csv(os.path.join('data', f'table02_No{naid}.csv'))
        for check in checks["Url"]:
            ck_url.append(check)

    ts = 0
    next_page = True
    while next_page != False:
        url = get_info(url, ts, naid, ck_url)
        print(url)
        ts += 15
        if url == None:
            break
    
    tb2_db(tb2)

    table02 = pd.DataFrame(columns=columns, data=tb2)
    if os.path.exists(os.path.join('data', f'table02_No{naid}.csv')):
        table02.to_csv(
            os.path.join('data', f'table02_No{naid}.csv'), mode="a", index=False, header=False, encoding="utf-8"
        )

        up_ck = updata_ck(naid)  # 判斷是否有今天新增的
        if up_ck == True:
            tb1_del(naid)
            print("Delete Table01")
            tb1_insert(naid, item_dict)
            print("Update OK")
    else:
        table02.to_csv(
            os.path.join('data', f'table02_No{naid}.csv'), mode="w", index=False, encoding="utf-8"
        )

        tb1_insert(naid, item_dict)
        print("Insert OK")
    
    table02.drop(table02.index, inplace=True)
    time.sleep(random.randint(3, 10))

    naid += 1
    

