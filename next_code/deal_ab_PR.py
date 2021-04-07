import re
import numpy as np
import matplotlib.pyplot as plt
from base_function import find_abnormal_data

path_name = "/home/kwq/work/east_window/0401/chart/1_qfn4CAA_memOutSeemsOk_east_abnormal_PR.txt"
fd = open(path_name, 'r')


def read_unit(_fd_):
    info = []
    line = _fd_.readline()
    while line != '\n':
        info.append(line)
        line = _fd_.readline()
    return info


time_dict = {}
PR_diff_diff_dict = {}

dict_tmp = {}
time = -1
for row in fd:
    if "time" in row:
        ret = re.findall(r"\d+\.?\d?", row)
        time = int(ret[0])
        ab_sv = ret[3]
    if "diff =" in row:
    # if "PR" in row:
        dict_str = row[row.index('{'):]
        dict_tmp = eval(dict_str)

    if "diff_diff_mean" in row:
        diff_list = list(dict_tmp.values())
        diff_list_cp = diff_list.copy()
        len_cp = len(diff_list_cp)
        mean_cp = np.mean(diff_list_cp)
        while len_cp > 2:
            abnormal_idx = find_abnormal_data(diff_list_cp)
            ab_diff = diff_list_cp.pop(abnormal_idx[0])
            len_cp = len(diff_list_cp)
            mean_cp = np.mean(diff_list_cp)  # 与ubx的差 去除最异常的值后 的均值
            ab_diff_diff = round(np.fabs(ab_diff - mean_cp))    # 最异常的值 - mean_cp
            if ab_diff_diff < 100:
                break

        for key in dict_tmp.keys():
            if key in time_dict.keys():
                time_dict[key].append(time)
                PR_diff_diff_dict[key].append(dict_tmp[key] - mean_cp)
            else:
                time_dict[key] = [time, ]
                PR_diff_diff_dict[key] = [dict_tmp[key] - mean_cp, ]

fd.close()

for key in PR_diff_diff_dict.keys():
    plt.title("diff_PR - diff_PR_mean")
    plt.plot(time_dict[key], PR_diff_diff_dict[key], marker='*', label='diff_diff_PR, sv' + str(key))
    plt.legend()  # 不加该语句无法显示 label
    # plt.draw()
    # plt.pause(4)  # 间隔的秒数： 4s
    # plt.close(fig1)
    plt.show()
