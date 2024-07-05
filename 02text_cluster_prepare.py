import os

import jieba
import jieba.analyse
import pandas as pd
from keybert import KeyBERT
from zhkeybert import KeyBERT, extract_kws_zh
from bs4 import BeautifulSoup
import csv
from mots_vides import stop_words
import warnings
import spacy
from sentence_transformers import SentenceTransformer
import re
import jieba.posseg as pseg
import time  # 引入time模块用于测试程序性能
# import chardet
#
# # 检测编码方式
# with open("company_website.csv", 'rb') as file:
#     result = chardet.detect(file.read())
#
# encoding = result['encoding']

start_time = time.time()

os.environ['HTTP_PROXY'] = "http://127.0.0.1:7890"
os.environ['HTTPS_PROXY'] = "https://127.0.0.1:7890"

# bert模型选择
# model = KeyBERT('distilbert-base-nli-mean-tokens')

#model = KeyBERT('paraphrase-multilingual-MiniLM-L12-v2')
#模型安装：从hugging face下到本地
model = KeyBERT('D:/1学习/科研/AIDD/paraphrase-multilingual-MiniLM-L12-v2 (2)')
zhmodel = KeyBERT('D:/1学习/科研/AIDD/paraphrase-multilingual-MiniLM-L12-v2 (2)')
print("Hello, World!")
warnings.filterwarnings("ignore", message="Your stop_words may be inconsistent with your preprocessing.")

# 加载 spaCy 模型:用于词性标注,模型安装：python -m spacy download en_core_web_sm
nlp = spacy.load("en_core_web_sm")

languages = [
    'arabic', 'bulgarian', 'catalan', 'czech', 'danish', 'dutch',
    'english', 'finnish', 'french', 'german', 'hungarian', 'indonesian',
    'italian', 'norwegian', 'polish', 'portuguese', 'romanian', 'russian',
    'spanish', 'swedish', 'turkish', 'ukrainian'
]
#all_stop_words = []
all_stop_words = set()
for lang in languages:
    try:
        # 尝试获取当前语言的停用词
        stop_words_for_lang = stop_words(lang)
        all_stop_words.update(stop_words_for_lang)
    except Exception as e:
        continue


# 从文件中读取中文停用词
def load_chinese_stop_words(file_path):
    stop_words = set()
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            stop_words.add(line.strip())
    return stop_words


chinese_stop_words_path = "chinese_stop_words.txt"
chinese_stop_words = load_chinese_stop_words(chinese_stop_words_path)
all_stop_words.update(chinese_stop_words)
all_stop_words = list(all_stop_words)
print("Chinese Stop Words Loaded:", len(chinese_stop_words))
print(all_stop_words)

# 指定读取HTMl文件夹路径
#folder_path = "output"
#folder_path = "facial_CB_html"
folder_path = "E:\科研\AIDD\AIDD_html24292"
file_list = []

# 指定读取HTML文件夹路径
write_file_path = "output.csv"

# 删除现有文件（如果存在），并重新创建文件
if os.path.exists(write_file_path):
    os.remove(write_file_path)

# 初始化CSV文件并写入表头
fieldnames = ["Repo_name", "About Content", "Readme Title", "Readme Content",
              "Keywords_1", "Value_1",
              "Keywords_2", "Value_2",
              "Keywords_3", "Value_3",
              "Keywords_4", "Value_4",
              "Keywords_5", "Value_5",
              "stars", "forks"]
with open(write_file_path, "w", newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

# 指定写入文件夹
write_file_path = "output.csv"
output_repo_name = pd.read_csv(write_file_path)["Repo_name"].tolist()


def parse_int(text):
    if text.endswith("k"):
        return int(float(text[:-1]) * 1000)
    elif text.endswith("m"):
        return int(float(text[:-1]) * 1000000)
    else:
        return int(text)


def about_readme(file_path):
    with open(file_path, "r", encoding="utf-8", errors='ignore') as file:
        # 读取文件内容
        html_content = file.read()
        soup = BeautifulSoup(html_content, "html.parser")
        about_section = soup.select("div.BorderGrid-row "
                                    "div.BorderGrid-cell "
                                    "div.hide-sm.hide-md "
                                    "p.f4.my-3")
        readme_html = "article.markdown-body.entry-content.container-lg"
        readme_title = soup.select("{} h1.heading-element".format(readme_html))
        readme_section = soup.select("{} p".format(readme_html))

        content = soup.find_all("a", class_="Link Link--muted")
        star_fork = {"stars": 0, "forks": 0}
        for item in content:
            sub_soup = BeautifulSoup(str(item), "html.parser")
            strong_tags = sub_soup.find_all("strong")
            for strong_tag in strong_tags:
                adjacent_text = strong_tag.next_sibling.strip()
                if adjacent_text in star_fork:
                    star_fork[adjacent_text] = parse_int(strong_tag.text.strip())
        # print(star_fork_watching)

        about_content = "\n".join(p.text.strip() for p in about_section)
        readme_title = "\n".join(p.text.strip() for p in readme_title)
        readme_content = "\n".join(p.text.strip().replace("\n", "") for p in readme_section)
        return about_content, readme_title, readme_content, star_fork


def pos_tagging(text):
    # 使用 jieba 进行中文分词和词性标注
    words = pseg.lcut(text)
    # 过滤中文分词结果，只保留名词和形容词，同时排除停用词
    filtered_words = [word for word, flag in words if flag in ('n', 'nr', 'ns', 'nt', 'nz', 'a', 'ad', 'an', 'ag', 'al') and word not in all_stop_words]

    # 使用 spaCy 进行英文分词和词性标注
    doc = nlp(text)
    # 过滤英文分词结果，只保留名词和形容词
    filtered_words.extend([word.text for word in doc if word.pos_ in ('NOUN', 'ADJ')])

    return " ".join(filtered_words)


def contains_chinese(text):
    # 使用正则表达式判断文本中是否包含中文字符
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def keybert(repo_name, about_content, readme_title, readme_content, star_fork):
    a = ""
    a = str(about_content) + str(readme_title) + str(readme_content)
    if a == "":
        with open("without_about_readme.txt", "a") as f:
            f.write(repo_name + "\n")
        return
    tagged_text = pos_tagging(a)

    if contains_chinese(a):
        # 提取中文关键词
        #keywords = jieba.analyse.textrank(a, topK=5, withWeight=True, allowPOS=('ns', 'n', 'vn', 'v'))
        #keywords = extract_kws_zh(tagged_text, model,ngram_range=(1, 2))
        keywords = model.extract_keywords(tagged_text, keyphrase_ngram_range=(1, 2), stop_words=all_stop_words)
    else:
        keywords = model.extract_keywords(tagged_text, keyphrase_ngram_range=(1, 2), stop_words=all_stop_words)

    # 检查提取出的关键词总长度是否超过20
    if sum(len(keyword) for keyword, _ in keywords) > 30:
        # 将提取出的关键词组合成一个文本
        combined_keywords = " ".join(keyword for keyword, _ in keywords)
        # 再次从组合后的关键词文本中提取关键词
        if contains_chinese(combined_keywords):
            #keywords = extract_kws_zh(combined_keywords, model, ngram_range=(1, 2))
            keywords = model.extract_keywords(combined_keywords, keyphrase_ngram_range=(1, 2),
                                              stop_words=all_stop_words)
        else:
            keywords = model.extract_keywords(combined_keywords, keyphrase_ngram_range=(1, 2),
                                              stop_words=all_stop_words)

    #keywords = model.extract_keywords(tagged_text, keyphrase_ngram_range=(1, 2), stop_words=all_stop_words)
    #keywords = model.extract_keywords(a, keyphrase_ngram_range=(1, 2), stop_words=all_stop_words)
    print("repo:")
    print(repo_name)
    print("keybert:keywords:")
    print(keywords)
    keyword_dict = {f"Keywords_{i + 1}": "" for i in range(5)}
    keyword_dict.update({f"Value_{i + 1}": "" for i in range(5)})
    for i, (keyword, value) in enumerate(keywords[:5]):
        keyword_dict[f"Keywords_{i + 1}"] = keyword
        keyword_dict[f"Value_{i + 1}"] =  value
    data = {
        "Repo_name": repo_name,
        "About Content": about_content,
        "Readme Title": readme_title,
        "Readme Content": readme_content,
        **keyword_dict,
        **star_fork
    }
    #print(data)

    fieldnames = ["Repo_name", "About Content", "Readme Title", "Readme Content",
                  "Keywords_1", "Value_1",
                  "Keywords_2", "Value_2",
                  "Keywords_3", "Value_3",
                  "Keywords_4", "Value_4",
                  "Keywords_5", "Value_5",
                  "stars", "forks"]
    with open(write_file_path, "a", newline='', encoding='utf-8',
              errors='replace') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()
        writer.writerow(data)
        csvfile.flush()


def read_file():
    # 遍历文件夹内所有文件
    for file_name in os.listdir(folder_path):
        # 检查文件是否以 .html 结尾
        if file_name.endswith(".html"):
            print(file_name)
            repo_name = file_name[:-5].replace("_", "/", 1)
            # 处理中断问题
            if repo_name in output_repo_name:
                continue
            file_path = os.path.join(folder_path, file_name)
            about_content, readme_title, readme_content, star_fork = about_readme(file_path)

            # print(about_content)
            # print(readme_title)
            # print(readme_content)
            keybert(repo_name, about_content, readme_title, readme_content, star_fork)
            print('keybert')


def main():
    read_file()
    print('END')


if __name__ == "__main__":
    main()
    # 记录结束时间
    end_time = time.time()

    # 计算并打印运行时间
    print(f"程序运行时间: {end_time - start_time} 秒")

# main()
text = "Whisper is a general-purpose speech recognition model."
model = KeyBERT('D:/1学习/科研/AIDD/paraphrase-multilingual-MiniLM-L12-v2 (2)')
keywords = model.extract_keywords(text)
print(keywords)
