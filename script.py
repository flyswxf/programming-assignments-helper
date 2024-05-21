from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from tools.vis_contest import visit
# from tools.vis_perplex import query
from tools.input_contest import submit
from tools.vis_gpt import query

import argparse
import time
import subprocess
import pyperclip
import sys

# 创建解析器
parser = argparse.ArgumentParser()
parser.add_argument('--mode', default='run', help='Mode to run the script. run or test')
parser.add_argument('--step',default='visit',help='Step to run.visit, query or submit.')
parser.add_argument('--cmd',default='auto',help='whether to run cmd in python. auto or manual')

# 解析参数
args = parser.parse_args()
mode = args.mode
step = args.step
cmd_status = args.cmd


if cmd_status == 'auto':
    # 定义你的命令
    cmd = '"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe" --remote-debugging-port=9222 --user-data-dir="C:\\selenum\\AutomationProfile"'

    # 使用subprocess模块运行命令
    subprocess.Popen(cmd, shell=True)

# 启动Edge浏览器时，添加远程调试端口参数
edge_options = Options()
# options.add_argument("--headless")
edge_options.add_experimental_option("debuggerAddress", "localhost:9222")

# 尝试连接到浏览器，如果失败则等待一段时间后重试
while True:
    try:
        # 创建一个新的Edge浏览器实例，连接到已经打开的浏览器会话
        driver = webdriver.Edge(service=Service('D://HuaweiMoveData//Users//fengl//Desktop//code//basic script//driver//msedgedriver.exe'), options=edge_options)
        wait = WebDriverWait(driver, 20)
        break
    except WebDriverException:
        print("Waiting for Edge to start...")
        time.sleep(1)

if mode == 'run':
    print('Running in run mode')

    start = time.time()

    for num in range(1003,1004):
        num=str(num)
        url="https://acm.ecnu.edu.cn/contest/774/problem/"+num+"/"
        print(url)

        # 执行vis-contest.py
        print('visit contest')
        visit(url, driver, wait)
        time.sleep(2)

        # 设置重试次数
        retry_times = 3

        for i in range(retry_times):
            # 执行vis-perplex.py
            print('visit perplexity')
            query(driver, wait)
            time.sleep(2)

            # 执行input-contest.py
            print('submit answer')
            result = submit(url, driver, wait)
            time.sleep(2)

            if result == 'Accepted':
                break
            print('re-search for answer')
        
        end = time.time()
        print(f"run time = {end-start}")

elif mode == 'test':
    print('Running in test mode')

    url="https://acm.ecnu.edu.cn/contest/774/problem/1003/"
    print('url = ' + url)

    if step == 'visit':
        # 执行vis-contest.py
        print('visit contest')
        visit(url, driver, wait)
        time.sleep(2)
        with open('log/query.txt','r',encoding='utf-8') as f:
            query = f.read().strip()
            print(query)

    elif step == 'query':
        # 执行vis-perplex.py
        print('visit ai')
        query(driver, wait)
        time.sleep(2)

    elif step == 'submit':
        # 执行input-contest.py
        print('submit answer')
        result = submit(url, driver, wait)
        time.sleep(2)

    else:
        print('no step named ' + step)

else:
    print('no mode named ' + mode)

    