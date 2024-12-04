from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.relative_locator import locate_with

from tools.txt_process import get_one_piece_from_query, get_task_index_from_url
from tools.web_check import try_to_find_site, open_a_new_tab

import pyperclip
import time
import sys
import re


def query(driver, wait, longwait, task_index):
    target_url = "https://tongyi.aliyun.com/qianwen/"
    try_to_find_site(driver, wait, target_url)

    # 每问5次就打开一个新对话,放止ai卡顿
    if int(task_index) % 5 == 0:
        open_a_new_tab(driver, target_url)

    # 设置重试次数
    retry_times = 3

    for i in range(retry_times):
        try:
            """
            # 等到页面加载完成,利用推荐模块的出现作为判断标准
            if driver.current_url == target_url:
                wait.until(EC.visibility_of_element_located((By.CLASS_NAME,'recommendWrapper--DtspmXbn')))
            """

            # 等到搜索框出现
            text_box = wait.until(
                EC.visibility_of_element_located((By.TAG_NAME, "textarea"))
            )
            print("qianwen is ready")
            break

        except Exception:
            print("fail to visit qianwen")
            print(f"retry {i+1}:")
            driver.refresh()

    with open("log/current_query.txt", "r", encoding="utf-8") as f:
        query = f.read()

    # 输入搜索内容并提交
    pyperclip.copy(query)
    text_box.send_keys(Keys.CONTROL + "v")

    wait.until(EC.text_to_be_present_in_element_value((By.TAG_NAME, "textarea"), query))
    text_box.send_keys(Keys.RETURN)
    print("query is sent")

    for i in range(retry_times):
        try:
            # 获取代码
            print("wait for code")
            longwait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "tools--IJfoLgka"))
            )
            longwait.until(EC.visibility_of_all_elements_located((By.TAG_NAME, "code")))

            # 获取所有的 pre 元素中的最后一个,即多次提问后的最新回答
            pre_elements = driver.find_elements(By.TAG_NAME, "pre")
            last_pre_element = pre_elements[-1]

            # code_locator=locate_with(By.TAG_NAME,'code').near({By.TAG_NAME:'pre'})
            code_locator = locate_with(By.TAG_NAME, "code").near(last_pre_element)
            code_element = driver.find_element(code_locator)
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
                    EC.visibility_of_all_elements_located(
                        (
                            By.XPATH,
                            "/html/body/div[1]/div/div[3]/div/div[2]/div/div[3]/div/div[3]/div[2]/span/svg",
                        )
                    )
                )
                copy_button = driver.find_element(
                    By.XPATH,
                    "/html/body/div[1]/div/div[3]/div/div[2]/div/div[2]/div[1]/div/div/div[2]/div[2]/div[1]/div/div/div/pre/div/span/div/svg",
                )

                # 鼠标移动到copy_button位置
                driver.execute_script("arguments[0].scrollIntoView();", copy_button)
                time.sleep(2)
                copy_button.click()
                # driver.execute_script("arguments[0].click();", copy_button)

                # 从剪贴板获取内容
                content = pyperclip.paste()
                print("get content from clipboard")

    # 打开一个文件用于写入搜索结果
    with open("log/results.txt", "w", encoding="utf-8") as f:
        # 移除开头的数字
        result = re.sub(r"^\d+", "", content, flags=re.MULTILINE)
        f.write(result)
        print("Search results written to results.txt")

    # driver.quit()
