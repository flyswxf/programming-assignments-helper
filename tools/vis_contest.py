from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
import sys

def vis_contest(url, driver, wait):
    # 访问指定的网址
    driver.get(url)
    # print(driver.title)

    # 打印出当前页面的标题,检查是否成功打开
    print(driver.title)

    # 查找页面中的所有段落，并打印出它们的文本
    paragraphs = driver.find_elements(By.TAG_NAME, "p")

    # 创建或打开result.txt文件，并写入文本
    with open("log/query.txt", "w", encoding="utf-8") as file:
        file.write(driver.title.replace('\n', ' '))
        for paragraph in paragraphs:
            text = paragraph.text
            # 如果文本包含不想要的内容，那么跳过这个段落
            if "团队: @ultmaster, @zerol, @kblack." in text or "联系方式: acmsupport@admin.ecnu.edu.cn" in text:
                continue
            file.write(text.replace('\n', ' '))

    print("Content written to query.txt")
    # driver.quit()
