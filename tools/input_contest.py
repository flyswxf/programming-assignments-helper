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

def submit(url, driver, wait):
    # 访问指定的网址
    driver.get(url)
    print(driver.title)

    # 打开并读取results.txt文件的内容
    with open('log/results.txt', 'r', encoding='utf-8') as f:
        content = f.read()

    # 找到文本框元素
    wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[2]/div[1]/div[2]/div[1]/form/div[2]/div[1]/div/textarea')))
    text_box = driver.find_element(By.XPATH,'/html/body/div[2]/div[1]/div[2]/div[1]/form/div[2]/div[1]/div/textarea')

    # 将content复制到剪贴板
    pyperclip.copy(content)

    # 清除文本框的内容
    text_box.send_keys(Keys.CONTROL + 'a')
    text_box.send_keys(Keys.DELETE)
    time.sleep(2)

    # 模拟粘贴操作
    text_box.send_keys(Keys.CONTROL + 'v')

    # 等待一段时间以确保内容已经输入
    time.sleep(2)

    # 找到提交按钮元素
    submit_button = driver.find_element(By.XPATH,'/html/body/div[2]/div[1]/div[2]/div[1]/form/div[2]/div[2]/button')

    # 使用JavaScript将浏览器滚动到提交按钮元素
    driver.execute_script("arguments[0].scrollIntoView();", submit_button)
    # 使用JavaScript将浏览器向下滚动200像素
    driver.execute_script("window.scrollBy(0, -200);")

    # 点击提交按钮
    submit_button.click()
    print('successfully submitted')

    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[1]/div[2]/div[1]/div[6]/table/tbody/tr[1]/td[5]/h5')))
        while True:
            element = driver.find_element(By.XPATH,'/html/body/div[2]/div[1]/div[2]/div[1]/div[6]/table/tbody/tr[1]/td[5]/h5')
            if element.text != 'In queue':
                break
            time.sleep(1)

        # 检查元素的文本内容
        with open('log/submitted.txt', 'w', encoding='utf-8') as f:
            # print(element.text)
            if element.text == 'Accepted':
                print('Accepted')
                f.write(url + ' : ' + 'Accepted')
                return 'Accepted'
            else:
                print('Wrong Answer')
                f.write(url + ' : ' + 'Wrong Answer')
                return 'Wrong Answer'
        # driver.quit()

    except TimeoutException:
        print(url + ' : ' + 'Unknown Error')
        return 'Unknown Error'
        # driver.quit()
