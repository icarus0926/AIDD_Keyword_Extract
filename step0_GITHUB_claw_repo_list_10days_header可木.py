

# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import csv
import json
import requests
from datetime import date, timedelta

proxy = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
session = requests.Session()

# url='https://github.com/search?q=big-data+created%3A{}..{}&type=repositories&ref=advsearch&p={}'
# url='https://github.com/search?q=machine-learning+created%3A{}..{}&type=repositories&ref=advsearch&p={}'

# url='https://github.com/search?q=drug+OR+medicine+OR+pharmaceutical*+created%3A{}..{}&type=repositories&ref=advsearch&p={}'

# url='https://github.com/search?q=q=drug-discovery+OR+medicine-discovery+OR+pharmaceutical-discovery+OR+drug-design+OR+medicine-design+OR+pharmaceutical-design+created%3A{}..{}&type=repositories&&ref=advsearch&p={}'

# url='https://github.com/search?q=genomics+OR+transcriptomics+OR+proteomics+OR+epigenomics+OR+metabolomics+created%3A{}..{}&type=repositories&&ref=advsearch&p={}'

url = 'https://github.com/search?q=biomarker+OR+exosomes+OR+microbiota+OR+drug-discovery+OR+Pharmaceutical-Formulation+OR+Pharmaceutical-Manufacturing+created%3A{}..{}&type=repositories&ref=advsearch&p={}'

start_date = date(2008, 1, 1)
end_date = date(2023, 12, 31)
current_date = start_date


def cun(search_url, p):
    res = session.get(search_url, proxies=proxy)
    print(res.text)
    res = json.loads(res.text)
    results = res['payload']['results']
    if results == []:
        return results

    keys = list(results[0].keys()) + ['current_date']  # Convert dict_keys to list
    for result in results:
        result['hl_name'] = result['hl_name'].replace('<em>', '').replace('</em>', '')
        result['current_date'] = str(current_date)  # Manually add current_date field
    write_header = not os.path.isfile("GITHUB_claw_repo_list.csv", )

    with open("GITHUB_claw_repo_list.csv", "a", newline='', encoding='utf-8', errors='replace') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        if write_header:
            writer.writeheader()
        for data in results:
            print(data)
            writer.writerow(data)
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
            if result == []:
                break;
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

