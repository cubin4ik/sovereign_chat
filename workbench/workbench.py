"""Test your ideas here"""

import time


def perf_check():
    start_time = time.perf_counter()

    with open("workbench.txt", "r") as rf:
        stat = rf.readlines()[-1]
        print(stat)

    # with open("workbench.txt", "r") as rf:
    #     while True:
    #         stat = rf.readline()
    #         print(stat)
    #         if not stat:
    #             break

    stop_time = time.perf_counter()

    print(f"DIFF: {stop_time - start_time}")

    # 0.040541499999999994 - using [-1]
    # 0.485154 - using all file loop


def get_last_id():
    with open("../data/users.txt", "r") as rf:
        text = rf.readlines()[-1].split(",")[0]
        if not text:
            return "NO"
        else:
            return text

