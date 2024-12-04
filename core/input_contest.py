from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException

from tools.web_check import check_login_status, try_to_find_site

import pyperclip
import time


def submit(url, driver, wait):
    # 这里要加wait,不然会出现问题
    try_to_find_site(driver, wait, url)
    check_login_status(driver=driver, wait=wait)
    try_to_find_site(driver, wait, url)

    # 打开并读取results.txt文件的内容
    with open("log/results.txt", "r", encoding="utf-8") as f:
        content = f.read()

    # 找到文本框元素
    text_box = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "ace_text-input"))
    )

    # 将content复制到剪贴板
    pyperclip.copy(content)

    # 清除文本框的内容
    text_box.send_keys(Keys.CONTROL + "a")
    text_box.send_keys(Keys.DELETE)
    wait.until(
        EC.text_to_be_present_in_element_value((By.CLASS_NAME, "ace_text-input"), "")
    )

    # 模拟粘贴操作
    text_box.send_keys(Keys.CONTROL + "v")
    # wait.until(EC.text_to_be_present_in_element_attribute((By.CLASS_NAME,'ace_layer.ace_text-layer'),'textContent',content))

    # 找到提交按钮元素
    submit_button = driver.find_element(By.ID, "problem-submit")

    # 点击提交按钮
    submit_button.click()
    print("successfully submitted")
    try:
        retry_times = 3
        for _ in range(retry_times):
            try:
                # 等待提交结果出现
                element = wait.until(
                    EC.any_of(
                        EC.visibility_of_element_located(
                            (
                                By.XPATH,
                                "/html/body/div[2]/div[1]/div[5]/table/tbody/tr/td[5]/h5",
                            )
                        ),
                        EC.visibility_of_element_located(
                            (
                                By.XPATH,
                                "/html/body/div[2]/div[1]/div[4]/table/tbody/tr[1]/td[5]/h5",
                            )
                        ),
                    )
                )
                # /html/body/div[2]/div[1]/div[5]/table/tbody/tr/td[5]/h5     当浏览器是竖式显示的
                # /html/body/div[2]/div[1]/div[4]/table/tbody/tr[1]/td[5]/h5  当浏览器是横式显示的
                wait.until(lambda driver: element.text != "In queue")
            except StaleElementReferenceException:
                time.sleep(1)

        """
        # 等待提交结果出现
        wait.until(lambda driver: element.text != 'In queue')
        time.sleep(1)
        
        element = wait.until(
            EC.any_of(
                EC.visibility_of_element_located((By.XPATH,'/html/body/div[2]/div[1]/div[5]/table/tbody/tr/td[5]/h5')),
                EC.visibility_of_element_located((By.XPATH,'/html/body/div[2]/div[1]/div[4]/table/tbody/tr[1]/td[5]/h5'))
            )
        )
        """

        # 记录提交结果
        with open("log/submitted.txt", "a", encoding="utf-8") as f:
            print(f"TextContent is {element.text}")
            if element.text == "Accepted":
                print("Accepted")
                f.write(url + " : " + "Accepted\n")
                return "Accepted"
            elif "Wrong answer" in element.text:
                print("Wrong Answer")
                f.write(url + " : " + "Wrong answer\n")
                return "Wrong Answer"
            elif "Runtime error" in element.text:
                print("Runtime Error")
                f.write(url + " : " + "Runtime error\n")
                return "Runtime Error"
            elif "Compilation error" in element.text:
                print("Compilation Error")
                f.write(url + " : " + "Compilation error\n")
                return "Compilation Error"
            elif "Time limit exceeded" in element.text:
                print("Time limit exceeded")
                f.write(url + " : " + "Compilation error\n")
                return "Time limit exceeded"
            else:
                print(url + " : " + "Unknown error")
                f.write(url + " : " + "Unknown error\n")
                return "Unknown error"

    except TimeoutException:
        print(url + " : " + "Unknown error")
        with open("log/submitted.txt", "w", encoding="utf-8") as f:
            f.write(url + " : " + "Unknown error\n")

        return "Unknown error"
        # 返回结果用于判断是否继续运行/停止检查

    except StaleElementReferenceException:
        print(url + " : " + "Wrong answer")
        with open("log/submitted.txt", "w", encoding="utf-8") as f:
            f.write(url + " : " + "Wrong answer\n")

        return "Wrong answer"
