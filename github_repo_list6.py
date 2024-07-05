

# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import csv
import requests
from datetime import date, timedelta
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 设置重试策略
retry_strategy = Retry(
    total=5,  # 总共重试次数
    backoff_factor=1,  # 重试间隔时间的增长因子
    status_forcelist=[429, 500, 502, 503, 504],  # 需要重试的HTTP状态码
    allowed_methods=["HEAD", "GET", "OPTIONS"]  # 需要重试的方法
)

adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("https://", adapter)
session.mount("http://", adapter)

url = 'https://github.com/search?q=biomarker+OR+exosomes+OR+microbiota+OR+drug-discovery+OR+Pharmaceutical-Formulation+OR+Pharmaceutical-Manufacturing+created%3A{}..{}&type=repositories&ref=advsearch&p={}'


start_date = date(2008, 1, 1)
end_date = date(2023, 12, 31)
current_date = start_date

def handle_rate_limit(response):
    if response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers and response.headers['X-RateLimit-Remaining'] == '0':
        reset_time = int(response.headers['X-RateLimit-Reset'])
        sleep_time = max(reset_time - time.time(), 0)
        print(f"Rate limit exceeded. Sleeping for {sleep_time} seconds.")
        time.sleep(sleep_time + 10)  # 等待速率限制重置，并额外等待10秒

def cun(search_url, p):
    res = session.get(search_url)
    handle_rate_limit(res)
    soup = BeautifulSoup(res.text, 'html.parser')
    repo_names = [repo.text.strip() for repo in soup.find_all('a', class_='v-align-middle')]
    
    if not repo_names:
        return repo_names

    write_header = not os.path.isfile("GITHUB_claw_repo_list.csv")

    with open("GITHUB_claw_repo_list.csv", "a", newline='', encoding='utf-8', errors='replace') as csvfile:
        writer = csv.writer(csvfile)
        if write_header:
            writer.writerow(['repo_name', 'current_date'])
        for repo_name in repo_names:
            writer.writerow([repo_name, str(current_date)])
    
    if p == 100:
        with open("exceed.csv", "a", newline='', encoding='utf-8', errors='replace') as csvfile:
            fieldnames = ['search_url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'search_url': search_url})
        print('大于或者等于100页')
    return 1

def claw(start_date, end_date):
    p = 1
    while 1:
        search_url = url.format(start_date, end_date, p)
        print(search_url)
        try:
            result = cun(search_url, p)
            if not result:
                break
            p += 1
        except Exception as e:
            print(e)
            time.sleep(120)
        time.sleep(10)

while current_date <= end_date:
    ten_days_end_date = current_date + timedelta(days=9)
    if ten_days_end_date > end_date:
        ten_days_end_date = end_date
    try:
        claw(current_date, ten_days_end_date)
        current_date += timedelta(days=10)
    except Exception as e:
        print(e)
        time.sleep(120)

