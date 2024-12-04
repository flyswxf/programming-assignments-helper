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


def query(driver, wait):
    target_url = "https://chatgpt.com/"
    found = False

    # 遍历所有打开的页面
    for window_handle in driver.window_handles:
        # 切换到该页面
        driver.switch_to.window(window_handle)
        # 检查URL是否与你想要的相等
        if driver.current_url == target_url:
            found = True
            print("found chatgpt")
            break

    # 如果没有找到，创建新的页面
    if not found:
        print("open chatgpt, you have 20 seconds to pass the robot test")
        driver.execute_script("window.open('" + target_url + "');")
        # 切换到新的页面
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(20)

    # 设置重试次数
    retry_times = 3

    for i in range(retry_times):
        try:
            # 等待搜索框变为可交互状态
            elem = wait.until(EC.element_to_be_clickable((By.TAG_NAME, "textarea")))
        except Exception:
            print("cant visit chatgpt")
            print(f"retry {i+1}:")
            driver.refresh()

    # 读取query.txt中的文本信息
    with open("log/query.txt", "r", encoding="utf-8") as f:
        query = f.read()

    # 输入搜索内容并提交
    pyperclip.copy(query)
    elem.send_keys(Keys.CONTROL + "v")

    time.sleep(2)
    elem.send_keys(Keys.RETURN)

    print("query is sent")

    # 等待搜索结果出现
    # wait = WebDriverWait(driver, 10)
    # results = wait.until(EC.presence_of_all_elements_located((By.XPATH, '/html/body/div/main/div/div/div[2]/div/div/div[2]/div[1]/div/div/div[1]/div/div/div[3]/div/div[1]/div[2]/div/div[2]/div/div/div/div//*')))

    for i in range(retry_times):
        try:
            print("wait for code")
            # time.sleep(20)
            # raise Exception("Force jump to exception")
            wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "ol")))
            # wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME, 'code')))

            code_element = driver.find_element(By.TAG_NAME, "code")
            content = code_element.text
            print("get content from code")
            break
        except TimeoutException:
            # 需修改,无法点击copy_botton
            # 原因是屏幕没有移动到copy按钮的位置
            print("page refresh")
            driver.refresh()

            time.sleep(2)

            if i < retry_times - 1:  # 如果不是最后一次重试，那么继续重试
                print(f"第{i+1}次尝试失败,总共{retry_times}次")

            else:  # 如果是最后一次重试，那么执行备用方案
                # 等待复制按钮出现并点击
                # 需要保持浏览器页面整齐!!!否则click()失效
                print("try to get content form clipboard")

                wait.until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "/html/body/div[1]/div[1]/div/main/div[1]/div[1]/div/div/div/div/div[5]/div/div/div[2]/div/div[1]/div/div/div/pre/div/div[1]/div/span/button",
                        )
                    )
                )
                copy_button = driver.find_element(
                    By.XPATH,
                    "/html/body/div[1]/div[1]/div/main/div[1]/div[1]/div/div/div/div/div[5]/div/div/div[2]/div/div[1]/div/div/div/pre/div/div[1]/div/span/button",
                )

                driver.execute_script("arguments[0].scrollIntoView();", copy_button)
                copy_button.click()
                # driver.execute_script("arguments[0].click();", copy_button)

                # 从剪贴板获取内容
                content = pyperclip.paste()
                print("get content from clipboard")

    # 打开一个文件用于写入搜索结果
    with open("log/results.txt", "w", encoding="utf-8") as f:
        f.write(content)

    # 关闭浏览器
    print("Search results written to results.txt")
    # driver.quit()
