# Github_Keyword_Extract
本项目用于提取以AIDD（AI制药）为主题的github仓库的关键词  
以下是文件说明：  
02text_cluster_prepare.py:使用bert模型提取仓库关键词  
AIDDhtml、facial_CB_html：之前使用get_html抓取的网页
4_get_html.py：用于抓取指定主题的github仓库网页  
chinese_stop_words.txt：中文停用词  
WordCount.py：将输出结果中的第一列关键词按词频排序（用于直观的查看抓取的关键词分布）
  
# 使用方法：
1.运行4_get_html.py抓取指定主题github仓库的首页，包括仓库的readme，repo_name等信息  
2.直接运行02text_cluster_prepare.py即可输出抓取仓库的关键词，每个仓库使用bert模型抓取出五个关键词
  

# Github_Keyword_Extract
This project is used to extract keywords from GitHub repositories themed around AIDD（AI Drug Discovery）.  
Here are the file descriptions:  

02text_cluster_prepare.py: Uses the BERT model to extract repository keywords.  
AIDDhtml, facial_CB_html: Previously scraped web pages using get_html.  
4_get_html.py: Used to scrape GitHub repository web pages for specified themes.  
chinese_stop_words.txt: Chinese stop words.  
WordCount.py: Sorts the first column of keywords in the output by frequency (used to visually check the distribution of extracted keywords).  
  
# Usage Instructions:：  
1.Run 4_get_html.py to scrape the homepage of GitHub repositories with the specified theme, including information such as the repository's readme, repo_name, etc.  
2.Simply run 02text_cluster_prepare.py to output the keywords for the scraped repositories, with each repository using the BERT model to extract five keywords.
