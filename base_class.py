import re
from typing import Dict, List, Any

import numpy as np
import time
import matplotlib.pyplot as plt


class RowParse:
    def __init__(self, row):
        self.row = row
        self.NUM_COMMA = {"GPGGA": 14, "GPRMC": 12, "GPGSA": 17}


def pli_cnr_info_prn_parse(row):
    ret = re.findall(r"-?\d+\.?\d*", row)
    return ret


def PR_DOPP_parse(row):
    ret = re.findall(r"-?\d+\.?\d*", row[:row.index("ir")])
    return ret


def chl_time_parse(row):
    ret = row.split(',')
    return round(int(ret[1]) / 1000)


class LogAnalysis:
    def __init__(self, f, *args, **kwargs):
        if isinstance(f, str) or args or kwargs:
            self.fp = open(f, *args, **kwargs)
        else:
            assert isinstance(f, object)
            self.fp = f
        self.pos = 0
        self.FILE_LEN = self.fp.seek(0, 2)  # 这条语句会将文件指针移到文件末尾
        self.fp.seek(self.pos, 0)
        self.NUM_COMMA = {"GGA": 14, "RMC": 12, "GFM": 14,
                          "chl_time": 3, "dopp": 11, "PR": 10,
                          "svINFO": 9, "prnNOW": 9,
                          "cnr": 9, "pli": 9}
        self.one_sec_row = {"cnr": '', "pli": '', "svINFO": '', "prnNOW": '',
                            "RMC": '', "GGA": '', "GFM": '', "chl_time": '',
                            "dopp": '', 'PR': ''}
        self.row_num = 0
        self.restart = 0
        self.time_bak = -1
        print(f)

    def close(self):
        """
        Close the File.
        """
        self.fp.close()

    def is_intact(self, string, key_word):
        """
        :param key_word: 语句关键字
        :param string: 要检测的字符串
        """
        if string.count(',') == self.NUM_COMMA[key_word]:
            return True
        else:
            return False

    def read_one_sec_log(self, flag_one_sec="bit lck"):
        self.one_sec_row = {}
        line = self.fp.readline()
        self.row_num += 1
        while line:
            line = self.fp.readline()
            self.row_num += 1
            if line.startswith("pli a:") or line.startswith("pli lst:"):
                self.one_sec_row["pli"] = line
            elif line.startswith("cnr:"):
                self.one_sec_row["cnr"] = line
            elif line.startswith("CHL TIME,"):
                self.one_sec_row["chl_time"] = line
            elif line.startswith('$GPGGA'):
                self.one_sec_row["GGA"] = line
            elif line.startswith('$GPRMC'):
                self.one_sec_row["RMC"] = line
            elif line.startswith('$GPGFM'):
                self.one_sec_row["GFM"] = line
            elif line.startswith('CHL PR,'):
                self.one_sec_row["GGA"] = line
            elif line.startswith('CHL DOPP,'):
                self.one_sec_row["dopp"] = line
            elif line.startswith("SV INFO"):
                self.one_sec_row["svINFO"] = line
            elif line.startswith("PRN NOW"):
                self.one_sec_row["prnNOW"] = line
            elif flag_one_sec in line:
                self.pos = self.fp.tell()
                return self.one_sec_row
            elif "cce load over" in line:
                return {'attention': "重启"}
        self.pos = self.fp.tell()
        return self.one_sec_row

    def get_target_row(self, target_lst):
        ret = {}
        one_sec_dict = self.read_one_sec_log()
        if 'attention' in one_sec_dict.keys():
            self.restart = 1
            return {}
        if bool(one_sec_dict):
            for aim in target_lst:
                if aim in one_sec_dict.keys():
                    tmp_row = one_sec_dict[aim]
                    if self.is_intact(tmp_row, aim):
                        ret[aim] = tmp_row
                    else:
                        print('The %d row <<%s>> not intact' % (self.row_num, tmp_row))
                        return {}
                else:
                    print("nearly %d row, this second  '%s'  not intact" % (self.row_num, aim))
                    return {}
        return ret

    def get_time_week_per_sec(self, string):
        """获取本周内的秒计数, 如果跨周, 就加上60480"""
        time_sec = chl_time_parse(string)
        if time_sec < 100 or self.time_bak - time_sec > 30240:
            if self.time_bak != -1:
                if self.restart != 0:   # 重启
                    return -1
                time_sec += 604800      # 没有重启 说明到下一周了
            else:
                return -1               # 板子刚上电
        self.restart = 0
        self.time_bak = time_sec
        return time_sec

    @property
    def pli_cnr_mean(self):
        time_lst = np.array([])
        pli_mean_lst = np.array([])
        cnr_mean_lst = np.array([])
        target = ["pli", "cnr", "chl_time"]
        self.fp.seek(0, 0)
        self.pos = 0
        # start_time = time.time()  # 开始时间
        while self.pos < self.FILE_LEN:
            ret_dict = self.get_target_row(target)
            if bool(ret_dict):  # 判断字典是否为空
                time_sec = self.get_time_week_per_sec(ret_dict[target[2]])
                if time_sec == -1:
                    continue
                pli_row = ret_dict[target[0]]
                pli_list = pli_cnr_info_prn_parse(pli_row)  # 解析 pli row
                tmp_arr_pli = []
                valid_idx_list = []
                for idx, item in enumerate(pli_list):
                    if item != '100':
                        tmp_arr_pli.append(int(item))
                        valid_idx_list.append(idx)
                if len(valid_idx_list) < 2:
                    continue
                pli_mean_lst = np.append(pli_mean_lst, np.mean(tmp_arr_pli))

                cnr_row = ret_dict[target[1]]
                cnr_list = pli_cnr_info_prn_parse(cnr_row)  # 解析 cnr row
                tmp_arr_cnr = []
                for i in valid_idx_list:
                    tmp_arr_cnr.append(int(cnr_list[i]))
                cnr_mean_lst = np.append(cnr_mean_lst, np.mean(tmp_arr_cnr))

                time_lst = np.append(time_lst, time_sec)

        # end_time = time.time()  # 结束时间
        # print("耗时: %d" % (end_time - start_time))
        return time_lst, pli_mean_lst, cnr_mean_lst

    @property
    def each_sv_per_sec_cnr(self):
        _all_sv_cnr_: Dict[str, List[Any]] = {}
        _all_sv_time_ = {}
        target = ["svINFO", "prnNOW", "cnr", "chl_time"]
        self.fp.seek(0, 0)
        self.pos = 0
        start_time = time.time()  # 开始时间
        while self.pos < self.FILE_LEN:
            ret_dict = self.get_target_row(target)
            if bool(ret_dict):  # 判断字典是否为空
                time_sec = self.get_time_week_per_sec(ret_dict[target[3]])
                if time_sec == -1:
                    continue
                
                svINFO_row = ret_dict[target[0]]
                info_list = pli_cnr_info_prn_parse(svINFO_row)  # 解析 svINFO row
                valid_sv_idx = []
                for i in range(10):                 # 获取有效的通道
                    if info_list[i] == '0':
                        valid_sv_idx.append(i)

                prn_row = ret_dict[target[1]]
                sv_id = pli_cnr_info_prn_parse(prn_row)
                new_sv_id = [str(int(i) + 1) for i in sv_id]

                cnr_row = ret_dict[target[2]]
                cnr_list = pli_cnr_info_prn_parse(cnr_row)  # 解析 cnr row

                for i in valid_sv_idx:
                    if new_sv_id[i] in _all_sv_time_.keys():
                        _all_sv_time_[new_sv_id[i]].append(time_sec)
                        _all_sv_cnr_[new_sv_id[i]].append(int(cnr_list[i]))
                    else:
                        _all_sv_time_[new_sv_id[i]] = []
                        _all_sv_time_[new_sv_id[i]].append(time_sec)
                        _all_sv_cnr_[new_sv_id[i]] = []
                        _all_sv_cnr_[new_sv_id[i]].append(int(cnr_list[i]))

        end_time = time.time()  # 结束时间
        print("耗时: %d" % (end_time - start_time))

        return _all_sv_time_, _all_sv_cnr_


if __name__ == '__main__':
    # path_file = "/home/kwq/work/east_window/0204/1_qfn6_newFrm_fixStatRenew_east.log"
    path_file = "/home/kwq/work/east_window/0203/qfn6_normal_newFrm_addSysChk_0.log"
    test = LogAnalysis(path_file, 'r')
    time_list, pli_mean_list, cnr_mean_list = test.pli_cnr_mean

    fig1 = plt.figure(1)
    plt.title("per second pli mean and cnr mean")
    plt.xlabel("sec of week")
    plt.plot(time_list, pli_mean_list, marker='x', label='pli')
    plt.plot(time_list, cnr_mean_list, marker='o', linestyle=':', label='cnr')
    plt.draw()
    plt.pause(5)
    plt.close(fig1)

    all_sv_time, all_sv_cnr = test.each_sv_per_sec_cnr
    fig2 = plt.figure(2)
    for key in all_sv_time.keys():
        plt.title("per second per sv cnr")
        plt.xlabel("sec of week")
        if int(key) > 32:
            plt.plot(all_sv_time[key], all_sv_cnr[key], linestyle=':', label='sv' + key)
        else:
            plt.plot(all_sv_time[key], all_sv_cnr[key], label='sv' + key)
    plt.legend()
    plt.draw()
    plt.pause(5)
    plt.close(fig2)

