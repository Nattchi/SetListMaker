from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import re
import random
import pandas as pd
from bs4 import BeautifulSoup

# 環境設定
driver_path = r"C:\Users\admin\Downloads\SetList\driver\chromedriver.exe"  # chromedriver へのパス
save_dir_path = "./results/"                                   # ライブ情報を格納した csvファイルの保存先

results = dict()
artist = input("セットリスト情報を検索したいアーティスト名を入力してください。\n")
domain = 'https://www.livefans.jp/'
# UAをいくつか格納しておく
user_agent = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
]
chrome_options = Options()
# ここにuser_agentからランダムで読み込み
chrome_options.add_argument('--user-agent=' + user_agent[random.randrange(0, len(user_agent), 1)])
# chrome_options.add_argument('--headless') # driver のウィンドウを表示しない
driver = webdriver.Chrome(
    executable_path=driver_path,
    options=chrome_options)

try:
    driver.get('https://www.livefans.jp/search?option=1&keyword=' + artist + '&genre=all&setlist=on&sort=e1')
    pageSource = driver.page_source
    bs = BeautifulSoup(pageSource, 'html.parser')

    event_url = list()
    event_title = list()

    # ライブ情報へのリンクを取得
    for info in bs.findAll("h3", class_="artistName"):
        for link in info.findAll("a", {"href": re.compile(r"^\/events\/\d+$")}):
            event_url.append(link.get('href'))
            print(link.get_text())
            event_title.append(link.get_text())

    dict.fromkeys(event_url)
    # ライブ情報を取得
    for idx, link in enumerate(event_url):
        result = {
            "artist": artist,
            "title": event_title[idx],
            "place": "",
            "url": link,
            "setlist": dict()
        }
        # print(domain + link)
        time.sleep(8)
        driver.set_page_load_timeout(30)
        driver.get(domain + link)
        driver.execute_script("document.EditSetlist.submit(); return false;")

        pageSource = driver.page_source
        bs = BeautifulSoup(pageSource, 'html.parser')
        count = 0
        event_place = bs.find("div", class_="bggry").find("h4").find("span").get_text()
        result["place"] = event_place
        print(result["title"], result["place"])
        for song in bs.findAll("input", {"id": re.compile(r"^sl_song_name_.+$")}):
            count += 1
            if song['value'] != "":
                print(count, song['value'])
                result["setlist"][count] = song['value']

        live_info = result["title"] + result["place"]
        results[live_info] = result

except:
    print("TIME OUT!!")
    print("正確なアーティスト名を入力されることを勧めます。")

driver.close()
driver.quit()
df = pd.DataFrame(results)
pd.set_option("display.width", 100)
df.to_csv(save_dir_path + artist + "_setlist.csv", encoding='utf-8-sig')
