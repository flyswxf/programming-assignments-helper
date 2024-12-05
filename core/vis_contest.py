from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support import expected_conditions as EC

from tools.web_check import try_to_find_site
from tools.txt_process import make_query

import sys


def visit(url, driver, wait, opt):
    # 检查是否已经打开过该网页
    try_to_find_site(driver, wait, url)

    info_or_limited = wait.until(
        EC.any_of(
            EC.visibility_of_element_located((By.CLASS_NAME, "problem-body")),
            EC.visibility_of_element_located((By.CLASS_NAME, "ui.grey.header")),
        )
    )
    print(driver.title)

    if info_or_limited.get_attribute("class") == "ui grey header":
        print("This problem is not accessible. Turning to the next problem...")
        driver.close()
        driver.switch_to.window(driver.window_handles[-1])
        return False

    # 查找页面中的所有段落，并打印出它们的文本
    paragraphs = driver.find_elements(By.CLASS_NAME, "problem-body")
    # examples = driver.find_elements(By.CLASS_NAME, "example")

    # 创建或打开result.txt文件，并写入文本
    make_query(url, paragraphs, opt)
    # driver.quit()
    return True
