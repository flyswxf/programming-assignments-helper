from tools.graph import make_pie_chart, make_line_chart
from tools.txt_process import write_time_to_file, clear_file

import time


class Time_tracker:
    def __init__(self):
        # 每一次计时使用的变量
        self.start_time = None
        self.end_time = None
        self.this_time = None

        # 统计时间
        self.total_time = 0
        self.task_count = 0
        self.time_per_task = None

        # 分部时间
        self.vis_time = None
        self.qry_time = None
        self.sub_time = None

        """
        # 用作图标下标
        self.task_index_start = None
        self.task_index_end = None
        """
        self.current_task_index = None

        clear_file("log/time.txt")

    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.end_time = time.time()

    def reset(self):
        self.start_time = None
        self.end_time = None

    def set_task_index(self, task_index):
        self.current_task_index = task_index
        self.task_count = self.task_count + 1

        if self.vis_time and self.qry_time and self.sub_time:
            write_time_to_file(
                self.current_task_index, self.vis_time, self.qry_time, self.sub_time
            )
        else:
            print("Time required is not complete")

    """
    def set_task_num(self,start,end):
        self.task_index_start = start
        self.task_index_end = end
    """

    def get_time(self, which_time=str):
        # 计算时间
        self.this_time = (
            self.end_time - self.start_time
            if self.end_time
            else time.time() - self.start_time
        )
        self.total_time = self.total_time + self.this_time

        if which_time == "visit":
            # 重置时间
            self.vis_time = None
            self.qry_time = None
            self.sub_time = None

            self.vis_time = self.this_time

        elif which_time == "query":
            self.qry_time = (
                self.this_time + self.qry_time if self.qry_time else self.this_time
            )
        elif which_time == "submit":
            self.sub_time = (
                self.this_time + self.sub_time if self.sub_time else self.this_time
            )

        self.this_time = None

    def show_time(self):
        print(f"total time = {self.total_time}")
        print(f"task count = {self.task_count}")
        print(f"time per task = {self.total_time/self.task_count}")

    # 需要三个时间都有值
    def show_pie_chart(self):
        make_pie_chart()

    def show_line_chart(self):
        make_line_chart()

    def __str__(self):
        return str(self.get_time())
