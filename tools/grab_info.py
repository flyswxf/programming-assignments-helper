from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pyperclip
import time
import sys
import subprocess
import requests

cmd = '"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe" --remote-debugging-port=9222 --user-data-dir="C:\\selenum\\AutomationProfile"'

# 使用subprocess模块运行命令
# subprocess.Popen(cmd, shell=True)

edge_options = Options()
edge_options.add_experimental_option("debuggerAddress", "localhost:9222")

driver = webdriver.Edge(service=Service('D://HuaweiMoveData//Users//fengl//Desktop//code//basic script//driver//msedgedriver.exe'), options=edge_options)
wait = WebDriverWait(driver, 20)

url = "https://www.51jiaoxi.com/doc-15664684.html"

driver.get(url)

# 等待页面加载完毕，这里使用的是等待body元素出现
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))


def get_text():
    # 获取特定XPath下的元素
    element = driver.find_element(By.XPATH,"/html/body/div[3]/div[1]/div[1]/div[3]")

    # 在该元素中找到所有的p元素
    paragraphs = element.find_elements(By.TAG_NAME, "p")

    with open("log/info.txt", "w", encoding="utf-8") as file:
        for paragraph in paragraphs:
            text = paragraph.text
            file.write(text + '\n')

    print('writing to info.txt')



def get_image():
    element = driver.find_element(By.XPATH,"/html/body/div[3]/div[2]/div[1]/div[2]/main/div[1]")
    # 在该元素中找到所有的img元素
    images = element.find_elements(By.TAG_NAME, "img")

    for index, image in enumerate(images):
        # 获取图片的src属性
        src = image.get_attribute("src")
        # 下载图片
        response = requests.get(src)
        with open(f"log/image/image{index}.png", 'wb') as f:
            f.write(response.content)

    print('writing images')

get_image()
