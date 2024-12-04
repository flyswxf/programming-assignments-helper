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
    # 让浏览器打开perplexity首页
    driver.get("https://www.perplexity.ai/")

    # 设置重试次数
    retry_times = 3

    for i in range(retry_times):
        try:
            # 等待搜索框变为可交互状态
            wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "/html/body/div/main/div/div/div[2]/div/div/div/div[1]/div[2]/div/div/div[2]/span/div/div/textarea",
                    )
                )
            )
            elem = driver.find_element(
                By.XPATH,
                "/html/body/div/main/div/div/div[2]/div/div/div/div[1]/div[2]/div/div/div[2]/span/div/div/textarea",
            )
        except Exception:
            print("cant visit perplexity.ai")
            print(f"retry {i+1}:")
            driver.refresh()

    # 读取query.txt中的文本信息
    with open("log/query.txt", "r", encoding="utf-8") as f:
        query = f.read().strip()

    # 输入搜索内容并提交
    pref = "用c++实现代码: "
    suff = " 请在每一个case与答案之间换行" if "case" in query else ""
    elem.send_keys(pref + query + suff + Keys.RETURN)
    print("query is sent")

    # 等待搜索结果出现
    # wait = WebDriverWait(driver, 10)
    # results = wait.until(EC.presence_of_all_elements_located((By.XPATH, '/html/body/div/main/div/div/div[2]/div/div/div[2]/div[1]/div/div/div[1]/div/div/div[3]/div/div[1]/div[2]/div/div[2]/div/div/div/div//*')))

    for i in range(retry_times):
        try:
            # time.sleep(20)
            # raise Exception("Force jump to exception")
            wait.until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "/html/body/div[1]/main/div/div/div[2]/div/div/div[2]/div[1]/div/div/div[1]/div/div/div[3]/div/div[1]/div[3]/div",
                    )
                )
            )

            code_element = driver.find_element(By.TAG_NAME, "code")
            content = code_element.text
            print("get content from code")
            break
        except Exception:
            # 需修改,无法点击copy_botton
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
                            "/html/body/div[1]/main/div/div/div[2]/div/div/div[2]/div[1]/div/div/div[1]/div/div/div[3]/div/div[1]/div[2]/div/div[2]/div/div/div/div/div/pre/div/div[2]/button",
                        )
                    )
                )
                copy_button = driver.find_element(
                    By.XPATH,
                    "/html/body/div[1]/main/div/div/div[2]/div/div/div[2]/div[1]/div/div/div[1]/div/div/div[3]/div/div[1]/div[2]/div/div[2]/div/div/div/div/div/pre/div/div[2]/button",
                )

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
