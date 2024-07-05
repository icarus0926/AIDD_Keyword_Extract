'''
email+link
36000*6=216000-214109
'''

import requests
import time
import pandas as pd
from bs4 import BeautifulSoup
import csv
import random
import argparse
from urllib.parse import quote

df = pd.read_excel('AIDD_Allrepo_24075.xlsx')
#proxy = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
session = requests.Session()
url = "https://github.com/{}"
headers_list = [
    {
        'Host': 'github.com',
        'method': 'GET',
        'scheme': 'https',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'If-None-Match': 'W/"92677dd8484e517e101346acc89b3983"',
        'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
        'Cookie': '_octo=GH1.1.1295396590.1684908646; _device_id=6c2224059a659fd82fc348f04c799a08; saved_user_sessions=126681664%3AeD7EJ4o6zFbwLxdsf0MJC4-mgDT1n7AwFXlnzHSs3aBAvJtg; user_session=eD7EJ4o6zFbwLxdsf0MJC4-mgDT1n7AwFXlnzHSs3aBAvJtg; __Host-user_session_same_site=eD7EJ4o6zFbwLxdsf0MJC4-mgDT1n7AwFXlnzHSs3aBAvJtg; logged_in=yes; dotcom_user=ninenia; has_recent_activity=1; color_mode=%7B%22color_mode%22%3A%22auto%22%2C%22light_theme%22%3A%7B%22name%22%3A%22light%22%2C%22color_mode%22%3A%22light%22%7D%2C%22dark_theme%22%3A%7B%22name%22%3A%22dark%22%2C%22color_mode%22%3A%22dark%22%7D%7D; preferred_color_mode=light; tz=Etc%2FGMT-8; _gh_sess=Xd3497jQ3vDu87QLCcteXjVf8xB6pgeFmOCekwUPugZ8lScHWdP0TFtqU56e0A7pZ2USy15rIUbUaV5W8RLEGwBXEtmqXc5Z%2FvLaGwYhU%2BPRDS2Ty6Z47FKQzyYky5MDvacMt9cPiW3mwekzCRKdgl3DvEZUy0s7qnA65Otu235ao0b6qBEEhTTbMO5XQToBJL6l%2FVJMFZvOcCaQN7sEJDQ1Q2DdcB%2FU1l8KmJyJRaM8JgVUq71WOrf6jyFzpnqEaI19byIZEzUT0YftExRj4mtlOiL3JDIs09HgogKcyIhh1YkZK9SzamwBQkmO7KLPl1%2F3MTazXXcn788hpukM1p6mBBFGVhXG4lKwFgRBS7rbP2nl0tz0AgW4vy4ZDtQ7UQrm5qXI17273y%2BO1QJxC74%2F1G94NJJ5YcOiI1g4Vq4DuHGrZT743zaA7BadRH0jStJxEYG4ZSw18DobX%2BoDts8OSPdgp%2FAXaoeoFgWCzZvg%2FO6kZFo3gki3SU%2FRtLan7FnGtIYyOOt0ofaPqekNKnG7G41mrDP8mm0lxk0DpnYJRvYLMfybITmLV4JjP%2BsKlvkb2jlg%2FOWg8x0NmA9etJCblpEY0%2FwMShcfqpofVYk%3D--W6jphv7xUG80qcWB--mhkFAOymLmV7m8jpoFhfsg%3D%3D'
    }
]

owner_repos = df['hl_name']


def run(search_url, owner_repo):
    headers = random.choice(headers_list)
    res = session.get(search_url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    owner_repo = owner_repo.replace("/", "@")
    file_path = f"AIDDhtml/{owner_repo}.html"
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(str(soup.prettify()))
    return res


def claw(search_url, owner_repo_quote, owner_repo):
    while True:
        url = search_url.format(owner_repo_quote)
        print(url)
        try:
            response = run(url, owner_repo)
            if response.status_code == 200:
                print("success")
                time.sleep(3)
                break  # 如果请求成功，退出循环
            if response.status_code == 404:
                time.sleep(3)
                print("404 not found")
                break
        except Exception as e:
            print(e)
            time.sleep(10)
        time.sleep(5)


if __name__ == '__main__':
    i = 1
    parser = argparse.ArgumentParser(description='github user website')
    parser.add_argument('--start_row_num', help='the starting row', default=1)
    parser.add_argument('--stop_row_num', help='the stopping row', default=1)
    args = parser.parse_args()
    # 遍历公司名单并爬取数据
    start_row = int(args.start_row_num)
    stop_row = int(args.stop_row_num)
    for owner_repo in owner_repos:
        if i < start_row:
            i += 1
            continue
        if i > stop_row:
            break
        if pd.isnull(owner_repo):
            i += 1
            print("Nan,pass.")
            continue
        owner_repo_quote = quote(owner_repo)  # 取第一个字符串作为搜索关键词
        print("\033[91mNo.{}\033[0m".format(owner_repo))
        url = 'https://github.com/{}'
        claw(url, owner_repo_quote, owner_repo)
        i += 1
