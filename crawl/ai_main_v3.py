import requests
from bs4 import BeautifulSoup
import time, random, datetime
from ai_todb_v2 import tb1_insert, tb1_del, updata_ck, tb2_db, get_ckurl, get_info_table


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


info_table = get_info_table()
urls = []
item_dict = {}

for data in info_table:
    urls.append(data[2])
    item_dict[data[0]] = data[1]


start = True

while start == True:
    try:
        naid = 0
        for url in urls:
            tb2 = []
            ck_url = get_ckurl(naid)
            
            ts = 0
            next_page = True
            while next_page != False:
                url = get_info(url, ts, naid, ck_url)
                print(url)
                ts += 15
                if url == None:
                    break
            
            if len(tb2) != 0:
                tb2_db(tb2)

            up_ck = updata_ck(naid)  # 判斷是否有今天新增的
            if up_ck == True:
                tb1_del(naid)
                tb1_insert(naid, item_dict)

            time.sleep(random.randint(3, 10))
            
            naid += 1
        start = False
    except Exception as e:
        pass

