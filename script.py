from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException

from core.vis_contest import visit

# from tools.vis_perplex import query
from core.input_contest import submit
from core.vis_qianwen import query  # 选择使用通义千问
from tools.txt_process import (
    research,
    get_one_piece_from_query,
    clear_file,
    show_accuracy,
)
from tools.time_tracker import Time_tracker
from core.WebAutomation import WebAutomation, Window_handler

import argparse
import subprocess

# 创建解析器
parser = argparse.ArgumentParser()
parser.add_argument(
    "--mode", default="classtest", help="Mode to run the script. run, test or classtest"
)
parser.add_argument(
    "--step", default="visit", help="Step to run. visit, query or submit."
)
parser.add_argument(
    "--cmd", default="auto", help="whether to run cmd in python. auto or manual"
)
parser.add_argument("--task_test_index", default="1", help="which task to test")
parser.add_argument(
    "--task_start_index", default=20, help="which task to start when running"
)
parser.add_argument(
    "--task_end_index", default=30, help="which task to end(not including) when running"
)

# 解析参数
args = parser.parse_args()
mode = args.mode
step = args.step
cmd_status = args.cmd
task_test_index = args.task_test_index
task_start_index = args.task_start_index
task_end_index = args.task_end_index


if cmd_status == "auto":
    # 定义你的命令
    cmd = '"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe" --remote-debugging-port=9222 --user-data-dir="C:\\selenum\\AutomationProfile"'

    # 使用subprocess模块运行命令
    subprocess.Popen(cmd, shell=True)

# 启动Edge浏览器时，添加远程调试端口参数
edge_options = Options()
# options.add_argument("--headless")
edge_options.add_experimental_option("debuggerAddress", "localhost:9222")

# 网络参数
driver = webdriver.Edge(
    service=Service(
        "./driver/msedgedriver.exe"
        # "D://HuaweiMoveData//Users//fengl//Desktop//code//web_spider//driver//msedgedriver.exe"
    ),
    options=edge_options,
)
wait = WebDriverWait(driver, 30)
longwait = WebDriverWait(driver, 60)

# 设置重试次数
retry_times = 3

# 设置计时功能
Timetra = Time_tracker()

# 修改意见:通义千问可能会碰到long long的问题,可以在查询时加上long long
# 修改意见:如果已经有query,则不再visit

if mode == "run":
    print("Running in run mode")
    clear_file("log/submitted.txt")
    # clear_file('log/query.txt')
    # 由于要多次搜索获得多个query,最好每次手动清理query.txt

    for task_index in range(task_start_index, task_end_index):
        task_index = str(task_index)
        url = "https://acm.ecnu.edu.cn/problem/" + task_index + "/"
        print(url)

        # 获取问题
        print("visit contest")
        Timetra.start()
        if not visit(url, driver, wait):
            Timetra.reset()
            continue
        Timetra.stop()
        Timetra.get_time("visit")

        # 查询问题
        print("query ai")
        Timetra.start()
        get_one_piece_from_query(task_index)

        for _ in range(retry_times):
            query(driver, wait, longwait, task_index)
            Timetra.stop()
            Timetra.get_time("query")

            # 提交答案
            print("submit answer")
            Timetra.start()
            result = submit(url, driver, wait)
            Timetra.stop()
            Timetra.get_time("submit")

            if result == "Accepted":
                driver.close()
                break
            # 若答案错误,则重新查询
            print("re-search for answer")
            Timetra.start()
            research(task_index, result)

        # 顺序不能变,因为set_task_index会设置任务数,show_time会计算平均时间
        Timetra.set_task_index(task_index)
        Timetra.show_time()

    # 展示运行效率
    Timetra.show_pie_chart()
    Timetra.show_line_chart()
    show_accuracy(task_start_index, task_end_index)

elif mode == "test":
    print("Running in test mode")
    clear_file("log/submitted.txt")

    url = "https://acm.ecnu.edu.cn/problem/" + task_test_index + "/"
    # 测试题目
    print("url = " + url)

    if step == "visit":
        clear_file("log/query.txt")
        print("visit contest")
        visit(url, driver, wait, "w")
        # 仅作测试用,显示query内容
        with open("log/query.txt", "r", encoding="utf-8") as f:
            query = f.read().strip()
            print(query)
        driver.quit()

    elif step == "multiVisit":
        clear_file("log/query.txt")
        print("multivisit contest")
        for _ in range(15):
            url = "https://acm.ecnu.edu.cn/problem/" + task_test_index + "/"
            visit(url, driver, wait, "a")

            # 多次访问后关闭一些窗口直到只剩一个
            if _ % 5 == 0:
                while len(driver.window_handles) > 1:
                    driver.switch_to.window(driver.window_handles[0])
                    driver.close()
                driver.switch_to.window(driver.window_handles[0])

            task_test_index = str(int(task_test_index) + 1)
        # 需要手动打开文本查看query内容
        driver.quit()

    elif step == "query":
        print("visit ai")
        get_one_piece_from_query(task_test_index)
        query(driver, wait, longwait, task_test_index)
        # 仅作测试用,显示result内容
        with open("log/results.txt", "r", encoding="utf-8") as f:
            print(f.read())
        driver.quit()

    elif step == "submit":
        retry_times = 3
        for i in range(retry_times):
            print("submit answer")
            result = submit(url, driver, wait)
            if result == "Accepted":
                driver.close()
                break
            print("re-search for answer")
            research(task_test_index, result)
            query(driver, wait, longwait, task_test_index)

    else:
        print("no step named " + step)

elif mode == "classtest":
    window_handler = Window_handler(driver, wait, longwait)
    WebAuto = WebAutomation(window_handler)
    if step == "visit":
        WebAuto.visit(task_start_index=17, task_end_index=30)


else:
    print("no mode named " + mode)
