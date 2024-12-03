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
import re


def check_login_status(
    driver: webdriver.Edge,
    wait: WebDriverWait,
    url="https://acm.ecnu.edu.cn/problem/list/",
):
    # 检查是否已经执行过了
    if getattr(check_login_status, "has_run", False):
        return

    # 切换到新标签页
    driver.execute_script("window.open(arguments[0], '_blank');", url)
    driver.switch_to.window(driver.window_handles[-1])

    # 等待任意一个元素出现
    # 一个是登录按钮(上),一个是账户信息(下)
    try:
        element = wait.until(
            EC.any_of(
                EC.visibility_of_element_located((By.CLASS_NAME, "ui.primary.button")),
                EC.visibility_of_element_located(
                    (By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[1]")
                )
                # 有待修改
            )
        )
        key = element.text

    except TimeoutException:
        print("Neither element was found within the given time.")
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return

    driver.close()
    driver.switch_to.window(driver.window_handles[-1])
    # 必须切换回原标签页,不然driver仍然对应已关闭标签页,会报错

    if key == "登入":
        print("please login and then try again")
        print("press 'c' to continue, press 'q' to quit")
        while True:
            user_input = input("Enter your choice: ").strip().lower()
            if user_input == "c":
                print("Continuing...")
                break
            elif user_input == "q":
                print("Quitting...")
                exit()
            else:
                print("Invalid input. Please press 'c' to continue or 'q' to quit.")
    else:
        print("you have already logined in")

    check_login_status.has_run = True


check_login_status.has_run = False


def check_site(driver: webdriver.Edge, wait: WebDriverWait, url):
    match = re.search(r"https://acm\.ecnu\.edu\.cn/problem/(\d+)/", url)
    if match:
        num = match.group(1)
        print(f"Extracted num: {num}")

    if EC.title_contains(num):
        return True
    else:
        return False

    # title形式如 Problem #5735 - ECNU Online Judge
    # 没做完,似乎不是很需要


def try_to_find_site(driver: webdriver.Edge, wait: WebDriverWait, url):
    # 执行完成后跳转到最新页面
    found = False
    # 检查是否已经有过页面
    for window_handle in driver.window_handles:
        # 切换到该页面
        driver.switch_to.window(window_handle)
        # 检查URL是否与你想要的相等
        if url in driver.current_url:
            found = True
            print("found that site")
            break

    # 如果没有找到，创建新的页面
    if not found:
        print("failed to find that site, open a new one")
        driver.execute_script("window.open('" + url + "');")
        # 切换到新的页面
        driver.switch_to.window(driver.window_handles[-1])


def open_a_new_tab(driver: webdriver.Edge, url):
    # 如果已经是目标页面,则不打开新标签页
    if not driver.current_url == url:
        driver.close()
        # close()方法会导致driver.window_handles更新,所以需要重新切换到原标签页
        driver.switch_to.window(driver.window_handles[-1])
        driver.execute_script("window.open('" + url + "');")
        driver.switch_to.window(driver.window_handles[-1])
