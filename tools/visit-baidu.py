from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 创建一个新的Edge浏览器实例
driver = webdriver.Edge(service=Service('D://HuaweiMoveData//Users//fengl//Desktop//code//basic script//driver//msedgedriver.exe'))
# 让浏览器打开Google首页
driver.get("http://www.baidu.com")

# 等待搜索框变为可交互状态
wait = WebDriverWait(driver, 10)
elem = wait.until(EC.element_to_be_clickable((By.NAME, "wd")))

# 找到搜索框
elem = driver.find_element(By.NAME, "wd")

# 输入搜索内容并提交
elem.send_keys("Hello World" + Keys.RETURN)

# 等待搜索结果出现
wait = WebDriverWait(driver, 10)
results = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.result.c-container')))

# 打开一个文件用于写入搜索结果
with open('results.txt', 'w', encoding='utf-8') as f:
    # 遍历搜索结果
    for result in results:
        # 获取并写入标题和URL
        title = result.find_element(By.CSS_SELECTOR, 'h3.t').text
        url = result.find_element(By.CSS_SELECTOR, 'h3.t a').get_attribute('href')
        f.write(f'Title: {title}\nURL: {url}\n\n')

# 关闭浏览器
print('Search results written to results.txt')
driver.quit()
