import pandas as pd
from collections import Counter

# 读取 CSV 文件
file_path = "output.csv"
df = pd.read_csv(file_path)

# 提取 Keywords_1 列
keywords = df["Keywords_1"].dropna().tolist()  # 使用 dropna() 以避免 NaN 值

# 统计词频
counter = Counter(keywords)

# 对词频统计结果进行排序
sorted_keywords = sorted(counter.items(), key=lambda item: item[1], reverse=True)

# 打印排序结果
for keyword, frequency in sorted_keywords:
    print(f"{keyword}: {frequency}")
