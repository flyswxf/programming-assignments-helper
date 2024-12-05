from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.relative_locator import locate_with

from tools.txt_process import (
    get_one_piece_from_query,
    get_task_index_from_url,
    clear_file,
)
from tools.web_check import check_login_status, try_to_find_site, open_a_new_tab
from tools.time_tracker import Time_tracker

import pyperclip
import time
import re
import logging
import json

with open("./constants.json", "r", encoding="utf-8") as f:
    constants = json.load(f)

TASK_BASE_URL = constants["TASK_BASE_URL"]
AI_URL = constants["AI_URL"]
RETRY_TIME = constants["RETRY_TIME"]
QUERY_FILE_PATH = constants["QUERY_FILE_PATH"]
RESULT_FILE_PATH = constants["RESULT_FILE_PATH"]


class File_Manager:
    def __init__(self):
        self.file_path = {"query": QUERY_FILE_PATH, "result": RESULT_FILE_PATH}

    def clear_file(self, file_name):
        with open(self.file_path[file_name], "w", encoding="utf-8") as f:
            f.write("")

    def find_query_position(self, task_index):
        """
        在文件中遍历行，找到包含题目{task_index}的行，
        如果找不到，则去找包含题目{最大的比task_index小的index}行。
        返回这个行号。

        !!!暂时弃用!!!

        Args:
        task_index (int): 题目编号

        Returns:
        position (int): 行在文件流中的位置
        """
        # 如果文件为空, 则返回0
        position = 0
        current_position = 2

        with open(self.file_path["queries"], "r", encoding="utf-8") as file:
            for line in file:
                if "题目" in line:
                    current_index = int(line.strip().split("题目")[1])
                    # 题目编号一定递增, 找到比task_index大的编号后返回前一个"题目"位置
                    if current_index > task_index:
                        return position
                    position = file.tell()
                    # 每次增加4是因为每个题目之间有4行
                    current_position += 4
        return position

    def make_a_query(self, task_index, paragraphs, opt="a"):
        """根据题目编号和段落内容, 将查询内容写入query.txt

        Args:
            task_index (int): 题目编号
            paragraphs (list): WebElement 列表. 实为段落内容
            opt (str, optional): 文件打开方式. 默认为'a', 即追加. 可选值为'w', 即覆盖.
        """

        with open(self.file_path["query"], opt, encoding="utf-8") as file:
            file.write("START OF THE QUERY\n")
            file.write(f"题目{task_index}\n")
            file.write("用C++实现代码: ")

            for paragraph in paragraphs:
                text = paragraph.text
                # 如果文本包含不想要的内容，那么跳过这个段落
                if (
                    "团队: @ultmaster, @zerol, @kblack." in text
                    or "联系方式: acmsupport@admin.ecnu.edu.cn" in text
                ):
                    continue
                file.write(text.replace("\n", " "))
            file.write(" 我需要在在线评测系统中提交代码，请确保你提供的程序能够直接接收输入而不需要提示信息,输入和输出格式可以参考样例\n")
            file.write("END OF THE QUERY\n")

        print("Content written to query.txt")

    def load_existing_tasks(self):
        """
        加载一个集合, 包含已经存在的题目编号, 用于提高搜索题目是否存在的效率
        Returns:
            set: 包含已经存在的题目编号
        """
        existing_tasks = set()
        try:
            with open(self.file_path["query"], "r", encoding="utf-8") as file:
                for line in file:
                    if line.startswith("题目"):
                        task_number = int(line.strip().replace("题目", ""))
                        existing_tasks.add(task_number)
        except FileNotFoundError:
            pass
        return existing_tasks


class Window_handler:
    def __init__(self, driver, wait, longwait):
        self.driver = driver
        self.wait = wait
        self.longwait = longwait

    def navigate_to_url(self, url):
        """
        执行完成后跳转到该页面
        """
        found = False
        # 检查是否已经有过页面
        for window_handle in self.driver.window_handles:
            self.driver.switch_to.window(window_handle)
            if url in self.driver.current_url:
                found = True
                print(f"found {url}")
                break

        # 如果没有找到，创建新的页面
        if not found:
            print("failed to find that site, open a new one")
            self.driver.execute_script("window.open('" + url + "');")
            # 切换到新的页面
            self.driver.switch_to.window(self.driver.window_handles[-1])

    def close(self):
        """
        关闭当前页面, 并切换到最后一个页面
        """
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def clean(self):
        """
        清理页面, 避免打开过多页面导致浏览器崩溃
        """
        while len(self.driver.window_handles) > 1:
            self.close()


class Visitor:
    def __init__(self, window_handler):
        self.window_handler = window_handler
        self.wait = window_handler.wait
        self.driver = window_handler.driver

    def get_task_url(self, task_index):
        """
        根据题目编号, 获取题目所在的URL
        """
        url = f"{TASK_BASE_URL}{task_index}/"
        return url

    def visit_task(self, task_index, opt, file_manager):
        """
        访问一个题目页面, 并获取题目内容
        如果无法访问, 则返回False, 否则返回True
        """
        url = self.get_task_url(task_index)
        self.window_handler.navigate_to_url(url)

        for i in range(RETRY_TIME):
            try:
                info_or_limited = self.wait.until(
                    EC.any_of(
                        EC.visibility_of_element_located(
                            (By.CLASS_NAME, "problem-body")
                        ),
                        EC.visibility_of_element_located(
                            (By.CLASS_NAME, "ui.grey.header")
                        ),
                    )
                )
                print(self.driver.title)

                if info_or_limited.get_attribute("class") == "ui grey header":
                    print(
                        "This problem is not accessible. Turning to the next problem..."
                    )
                    self.window_handler.close()
                    return False

                break
            except TimeoutException:
                print(f"visit task site failed, retry {i+1}")
                self.driver.refresh()

        paragraphs = self.driver.find_elements(By.CLASS_NAME, "problem-body")
        file_manager.make_a_query(task_index, paragraphs, opt)
        return True


class Querier:
    def __init__(self, window_handler):
        self.window_handler = window_handler
        self.wait = window_handler.wait
        self.driver = window_handler.driver

    def get_query(self, task_index):
        """
        从query.txt中获取本次查询内容
        Returns:
            str: 本次查询内容
        """
        with open(QUERY_FILE_PATH, "r", encoding="utf-8") as file:
            for line in file:
                if f"题目{task_index}" in line:
                    query = next(file).strip()
                    return query

        print(f"Query for task {task_index} not found.")
        raise ValueError("Query not found")

    def query_task(self, task_index):
        self.window_handler.navigate_to_url(AI_URL)
        # 等待页面加载
        for i in range(RETRY_TIME):
            try:
                text_box = self.wait.until(
                    EC.visibility_of_element_located((By.TAG_NAME, "textarea"))
                )
                print("Qianwen is ready")
                break
            except Exception:
                print(f"fail to visit Qianwen, retry {i+1}")
                self.driver.refresh()

        # 获取本次查询内容
        query = self.get_query(task_index)

        # 发送查询内容
        pyperclip.copy(query)
        text_box.send_keys(Keys.CONTROL + "v")
        self.wait.until(
            EC.text_to_be_present_in_element_value((By.TAG_NAME, "textarea"), query)
        )
        text_box.send_keys(Keys.RETURN)
        print("query is sent")

        # 等待查询结果
        for i in range(RETRY_TIME):
            try:
                print("wait for code")
                self.longwait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "tools--IJfoLgka"))
                )
                self.longwait.until(
                    EC.visibility_of_all_elements_located((By.TAG_NAME, "code"))
                )

                pre_elements = self.driver.find_elements(By.TAG_NAME, "pre")
                last_pre_element = pre_elements[-1]

                code_locator = locate_with(By.TAG_NAME, "code").near(last_pre_element)
                code_element = self.driver.find_element(code_locator)
                content = code_element.text

                print("get content from code")
                break
            except TimeoutException:
                print(f"code not found, retry {i+1}")
                self.driver.refresh()

        # 写入查询结果
        with open(RESULTS_FILE_PATH, "w", encoding="utf-8") as f:
            result = re.sub(r"^\d+", "", content, flags=re.MULTILINE)
            f.write(result)
            print("Search results written to results.txt")


class WebAutomation:
    """
    启动方式:
    webAtuo = WebAutomation(window_handler)
    注: visit是独立的, 如果query需要使用的信息尚不存在, 则会自动调用visit
    webAtuo.visit(task_start_index = , task_end_index =)
    webAtuo.query(task_start_index = , task_end_index =)
    """

    def __init__(self, window_handler):
        self.window_handler = window_handler
        self.driver = window_handler.driver
        self.longwait = window_handler.longwait
        self.wait = window_handler.wait

        self.Visitor = Visitor(window_handler)
        self.Querier = Querier(window_handler)

        self.timetracker = Time_tracker()
        self.file_manager = File_Manager()

        self.existing_tasks = self.file_manager.load_existing_tasks()

    def visit(self, task_start_index, task_end_index=None, opt="a"):
        """从task_start_index到task_end_index访问题目, 如果题目已经存在, 则跳过

        Args:
            task_start_index (int): 题目起始编号
            task_end_index (int): 题目结束编号, 可选参数, 不输入时只访问一个题目
            opt (str, optional): query.txt的打开方式. 默认为'a', 即追加. 可选值为'w', 即覆盖.
        Returns:
            将题目信息按编号无顺序写入query.txt, 但保证不重复
        """
        self.timetracker.start()

        # 如果task_end_index未指定, 则只访问一个题目
        if task_end_index is None:
            task_end_index = task_start_index + 1

        if opt == "a":
            print(f"visit contest from {task_start_index} to {task_end_index - 1}")

            for task_index in range(task_start_index, task_end_index):
                # 题目信息已经被记录在query.txt中
                if task_index in self.existing_tasks:
                    print(f"problem {task_index} already exist in query.txt, skip")
                    continue
                print(f"visit problem {task_index}")

                self.Visitor.visit_task(task_index, opt, self.file_manager)

                if task_index % 5 == 0:
                    self.window_handler.clean()

        self.timetracker.get_time("visit")

    def query(self, task_start_index, task_end_index):
        self.timetracker.start()

        print(f"query from {task_start_index} to {task_end_index - 1}")
        for task_index in range(task_start_index, task_end_index):
            if task_index not in self.existing_tasks:
                print(f"problem {task_index} not exist, skip")
                self.visit(task_index)
            self.Querier.query(task_index)

            if task_index % 5 == 0:
                self.window_handler.clean()

        self.timetracker.get_time("query")

    def submit(self, url):
        try_to_find_site(self.driver, self.wait, url)
        check_login_status(driver=self.driver, wait=self.wait)
        try_to_find_site(self.driver, self.wait, url)

        with open("log/results.txt", "r", encoding="utf-8") as f:
            content = f.read()

        text_box = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "ace_text-input"))
        )

        pyperclip.copy(content)
        text_box.send_keys(Keys.CONTROL + "a")
        text_box.send_keys(Keys.DELETE)
        self.wait.until(
            EC.text_to_be_present_in_element_value(
                (By.CLASS_NAME, "ace_text-input"), ""
            )
        )
        text_box.send_keys(Keys.CONTROL + "v")

        submit_button = self.driver.find_element(By.ID, "problem-submit")
        submit_button.click()
        print("successfully submitted")

        try:
            for _ in range(self.retry_times):
                try:
                    element = self.wait.until(
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
                    self.wait.until(lambda driver: element.text != "In queue")
                except StaleElementReferenceException:
                    time.sleep(1)

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

        except StaleElementReferenceException:
            print(url + " : " + "Wrong answer")
            with open("log/submitted.txt", "w", encoding="utf-8") as f:
                f.write(url + " : " + "Wrong answer\n")
            return "Wrong answer"
