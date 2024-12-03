import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

from tools.txt_process import read_time_from_file

# 测试时使用下面的导入
# from txt_process import read_time_from_file


def make_pie_chart():
    # 创建 DataFrame
    data = read_time_from_file()

    df = pd.DataFrame(data)

    # 计算 vis, qry, sub 的平均值
    avg_vis = df["vis"].mean()
    avg_qry = df["qry"].mean()
    avg_sub = df["sub"].mean()

    # 创建包含平均值的新 DataFrame
    avg_data = {"step": ["vis", "qry", "sub"], "average": [avg_vis, avg_qry, avg_sub]}
    avg_df = pd.DataFrame(avg_data)

    # 设置 Seaborn 样式
    sns.set(style="whitegrid")

    # 创建饼图
    plt.figure(figsize=(10, 6))
    wedges, texts, autotexts = plt.pie(
        avg_df["average"],
        labels=avg_df["step"],
        autopct="%1.1f%%",
        startangle=140,
        colors=sns.color_palette("viridis"),
    )

    # 添加真实值
    for i, text in enumerate(texts):
        text.set_text(f"{text.get_text()} ({avg_df['average'][i]:.2f})")

    # 添加标题
    plt.title("Average Time Spent on Each Step(Seconds)")

    # 获取当前文件所在文件夹的上级目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)

    # 确保目录存在
    output_dir = os.path.join(parent_dir, "log", "image")
    os.makedirs(output_dir, exist_ok=True)

    # 保存图像到指定目录
    output_path = os.path.join(output_dir, "pie_chart.png")
    plt.savefig(output_path)

    # 关闭图像以释放内存
    plt.close()


def make_line_chart():
    # 创建 DataFrame
    data = read_time_from_file()
    """
    data格式如下:
    data = {
        'task': ['Task 1', 'Task 2', 'Task 3'],
        'time': [8, 16, 24],
        'vis': [5, 10, 15],
        'qry': [2, 4, 6],
        'sub': [1, 2, 3]
    }
    """
    df = pd.DataFrame(data)[["task", "time"]]

    # 设置 Seaborn 样式
    sns.set(style="whitegrid")

    # 创建折线图
    plt.figure(figsize=(10, 6))
    sns.lineplot(x="task", y="time", data=df, marker="o", palette="viridis")

    # 添加标题和标签
    plt.title("Task Completion Time")
    plt.xlabel("Task")
    plt.ylabel("Time (seconds)")

    # 获取当前文件所在文件夹的上级目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)

    # 确保目录存在
    output_dir = os.path.join(parent_dir, "log", "image")
    os.makedirs(output_dir, exist_ok=True)

    # 保存图像到指定目录
    output_path = os.path.join(output_dir, "line_chart.png")
    plt.savefig(output_path)

    # 关闭图像以释放内存
    plt.close()


# 测试用
if __name__ == "__main__":
    make_pie_chart(10, 20, 30)
    make_line_chart()
