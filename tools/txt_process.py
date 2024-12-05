import re

# 查询相关------------------------------------------------


def search_query(task_index):
    # 计算大致的起始位置
    start_pos = 4 * (query_number - 1) + 2

    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

        # 从大致位置开始搜索
        for i in range(max(0, start_pos - 10), min(len(lines), start_pos + 10)):
            if lines[i].strip() == f"题目{query_number}":
                return True
    return False


def get_one_piece_from_query(task_index):
    with open("log/query.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()

    query_start_index = None
    query_end_index = None

    # 找到包含 '题目' 和 task_index 的行
    for i, line in enumerate(lines):
        if f"题目{task_index}" in line:
            query_start_index = i
            break

    # 找到 'END OF THE QUERY' 的行
    if query_start_index is not None:
        for i, line in enumerate(lines, start=query_start_index):
            if "END OF THE QUERY" in line:
                query_end_index = i
                break

    # 提取查询内容
    if query_start_index is not None and query_end_index is not None:
        query_lines = lines[query_start_index + 1 : query_end_index - 1]

        with open("log/current_query.txt", "w", encoding="utf-8") as file:
            for line in query_lines:
                file.write(line)

        print("Query for this task written to current_query.txt")
    else:
        print(f"Query for task {task_index} not found.")
        raise ValueError("Query not found")


def research(task_index, error_type):
    """
    # 获取错误类型
    with open('log/submitted.txt', 'r', encoding='utf-8') as f:
        last_result = f.readlines()[-1]
        error_type = last_result.split(':')[-1].strip()
    """
    # 判断是否已经重新查询过
    have_researched = False
    with open("log/current_query.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
        if any("你之前提供的代码不对" in line for line in lines):
            have_researched = True

    if have_researched:
        # 删除包含 '你之前提供的代码不对' 的行
        lines = [line for line in lines if "你之前提供的代码不对" not in line]

        # 添加新的错误信息
        new_error_message = "你之前提供的代码又出错了,出现了" + error_type + "错误,请好好考虑,重新提供代码\n"
        lines.append(new_error_message)

        with open("log/current_query.txt", "w", encoding="utf-8") as f:
            f.writelines(lines)
    else:
        # 准备下次查询
        with open("log/current_query.txt", "a", encoding="utf-8") as f:
            f.write("你之前提供的代码不对,出现了" + error_type + "错误,请重新提供代码\n")


def get_task_index_from_url(url):
    # 从URL中提取题目编号
    match = re.search(r"https://acm\.ecnu\.edu\.cn/problem/(\d+)/", url)
    if match:
        num = match.group(1)
        return num
    else:
        return None


# 时间相关------------------------------------------------


def write_time_to_file(task_index, vis, qry, sub):
    with open("log/time.txt", "a", encoding="utf-8") as f:
        f.write(f"Problem {task_index}\n")
        f.write(f"vis: {vis}\n")
        f.write(f"qry: {qry}\n")
        f.write(f"sub: {sub}\n")
        f.write("\n")

    print("Time written to time.txt")


def read_time_from_file():
    with open("log/time.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 从文件中读取时间
    tasks = []
    times = []
    V, Q, S = [], [], []
    for i in range(0, len(lines), 5):
        task_index = lines[i].split(" ")[-1].strip()
        vis = float(lines[i + 1].split(":")[-1].strip())
        qry = float(lines[i + 2].split(":")[-1].strip())
        sub = float(lines[i + 3].split(":")[-1].strip())
        total_time = vis + qry + sub
        tasks.append(f"Problem {task_index}")
        times.append(total_time)
        V.append(vis)
        Q.append(qry)
        S.append(sub)

    data = {"task": tasks, "time": times, "vis": V, "qry": Q, "sub": S}

    return data


def clear_file(file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("")


# 访问相关------------------------------------------------


def make_query(url, paragraphs, opt):
    """
    根据给定的 URL 和段落列表生成查询，并将其写入文件。

    参数:
    url (str): 网站的 URL。
    paragraphs (list): 包含段落文本的列表。
    opt (str): 文件打开模式，'a' 表示追加，'w' 表示覆盖。

    file中格式如下:
        START OF THE QUERY
        题目1000
        用C++实现代码: 标题 内容 我需要在在线评测系统中提交代码，请确保你提供的程序能够直接接收输入而不需要提示信息,输入和输出格式可以参考样例
        END OF THE QUERY

    返回:
    None
    """
    task_index = get_task_index_from_url(url)

    # 测试多次搜索功能使用"a"
    with open("log/query.txt", opt, encoding="utf-8") as file:
        file.write("START OF THE QUERY\n")
        file.write("题目" + task_index + "\n")
        file.write("用C++实现代码:")
        # file.write(driver.title.replace("\n", " "))

        for paragraph in paragraphs:
            text = paragraph.text
            # 如果文本包含不想要的内容，那么跳过这个段落
            if (
                "团队: @ultmaster, @zerol, @kblack." in text
                or "联系方式: acmsupport@admin.ecnu.edu.cn" in text
            ):
                continue
            file.write(text.replace("\n", " "))
        file.write("我需要在在线评测系统中提交代码，请确保你提供的程序能够直接接收输入而不需要提示信息,输入和输出格式可以参考样例\n")
        file.write("END OF THE QUERY\n")

    print("Content written to query.txt")


def show_accuracy(task_start_index, task_end_index):
    with open("log/submitted.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()

    correct = 0
    wrong = 0
    for line in lines:
        if "Accepted" in line:
            correct += 1
        else:
            wrong += 1

    print(
        f"Accuracy for task from {task_start_index} to {task_end_index} : {correct}/{correct+wrong}"
    )
