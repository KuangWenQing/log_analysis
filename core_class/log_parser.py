import re
import os
import sys
import numpy as np
from base_function import lla_to_xyz

__all__ = ['LogParser']


class LogParser:
    purpose_need_row = {"cnr": ["cnr", "svINFO", "prnNOW"], "pli": ["pli", "svINFO", "prnNOW"], "dli": ["dli"],
                        "pos": ["GGA", "RMC", "GGAIGG", "GGAKF"], "posKF": ["RMCKF", "GGAKF"],
                        "PR": ["PR", "svINFO", "prnNOW"], "dopp": ["dopp", "svINFO", "prnNOW"]}
    row_flag_dict = {"cnr": ['cnr:', ''], "pli": ['pli ', ''], "svINFO": ['SV INFO', ''], "prnNOW": ['PRN NOW', ''],
                     "dli": ['dli a:', ''], "RMC": ['$GPRMC,', ''], "GGA": ['$GPGGA,', ',*'], "GFM": ['$GPGFM', ''],
                     "chl_time": ['CHL TIME,', ''], "GGAIGG": ['$GGAIGG', ''], "GGAKF": ['$GPGGA,', ',KF*'],
                     "RMCKF": ['$GPRMC,', 'KF'], "val_num": ["val num", "sv"],
                     "dopp": ['CHL DOPP,', 'ir'], 'PR': ['CHL PR,', 'ir'], "fix_sv": ['PV, val num', '']}
    NUM_COMMA = {"GGA": 14, "RMC": 12, "GFM": 14, "GGAIGG": 14, "GGAKF": 14, "RMCKF": 12,
                 "chl_time": 3, "dopp": 11, "PR": 10,
                 "svINFO": 9, "prnNOW": 9, "fix_sv": 2, "val_num": 10,
                 "cnr": 9, "pli": 9, "dli": 9}

    def __init__(self, target_file, __purpose__, ubx_file):
        self.valid_chl_flag = [0, ]  # 9, 3, 1, 2]
        self.cmp_enable = 0
        self.cmp_support = 0
        if len(ubx_file):  # 有U-blox的文件
            self.cmp_support = 1
            self.f_ubx = open(ubx_file, 'r', errors="ignore")

        if isinstance(__purpose__, dict) and len(target_file):
            self.filename = os.path.split(target_file)[1]
            self.path = target_file.split(self.filename)[0]
            self.f_our = open(target_file, 'r', errors="ignore")
            self.purpose = __purpose__.copy()
            _target_row = ["chl_time", "val_num"]
            for key in __purpose__.keys():
                if key in LogParser.purpose_need_row.keys():
                    _target_row += LogParser.purpose_need_row[key]
                else:
                    del self.purpose[key]
                    print("can't support the <%s> purpose" % key)

                if key in ["cnr", "pos", "pr", "dopp", "sv_keep"]:
                    self.cmp_enable = 1
            self.target_row = list(set(_target_row))
        else:
            sys.exit("you must input our path file, "
                     "1 dict, the key is target_row and value are you want operate\n"
                     "the ubx path file is not essential")
        self.ubx_bak_time = 0
        self.final_pos_str = ''
        self.row_cnt = 0
        self.restart = 0
        self.time_bak = -1
        self.pos = 0
        self.FILE_LEN = self.f_our.seek(0, 2)  # 把文件指针移到文件末尾并移动0
        self.f_our.seek(0, 0)  # 把文件指针移到文件起始并移动0
        print(self.path, self.filename)
        print("目的:", self.purpose, "\n需要解析的行:", self.target_row)

        self.all_info_list: list = []  # [{"cnr": [], "pli": [], "pr": [], ..}, {2sec info}, ... ]
        self.all_info_dict: dict = {}  # {"cnr": [[1sec], [2sec], ... ], "pli":[[1sec], [2sec], ... ],  ..}
        self.all_valid_chl: list = []
        self.ubx_info_dict: dict = {}  # {time: [each sv_info], time: [each sv_info], }
        self.parser_file()

    def is_intact(self, string, key_word):
        """
        :param key_word: 语句关键字
        :param string: 要检测的字符串
        """
        if string.count(',') == self.NUM_COMMA[key_word]:
            return True
        else:
            return False

    def read_one_second_field(self, flag_one_sec="bit lck"):
        one_sec_row = {}
        line = self.f_our.readline()
        if line:
            self.row_cnt += 1
        while line:
            one_sec_row[self.row_cnt] = line
            line = self.f_our.readline()
            self.row_cnt += 1
            ''' 重启标志 '''
            if "cce load over" in line:
                self.restart = 2
                break

            ''' 1 秒标志 '''
            if flag_one_sec in line:
                break

        self.pos = self.f_our.tell()
        one_sec_row[self.row_cnt] = line
        return one_sec_row

    def extract_target_row(self):
        one_sec_row = {}
        one_second_field = self.read_one_second_field()
        for key in one_second_field.keys():
            line = one_second_field[key]
            if "tot cnt:" in line:
                self.final_pos_str = line
            elif "set time:" in line:
                if self.restart == 2:
                    self.restart = 1

            for target in self.target_row:
                if line.startswith(self.row_flag_dict[target][0]) and self.row_flag_dict[target][1] in line \
                        and target not in one_sec_row.keys():
                    if target == "val_num":
                        if not one_second_field[key-1].startswith("PDT DB DIFF,"):
                            continue
                    if self.is_intact(line, target):
                        one_sec_row[target] = line
                    else:
                        print("The %d row << %s >> is incomplete" % (key, line))
        return one_sec_row

    def one_second_field(self, flag_one_sec="bit lck"):
        one_sec_row = {}
        line = self.f_our.readline()
        self.row_cnt += 1
        while line:
            line = self.f_our.readline()
            self.row_cnt += 1

            if "tot cnt:" in line:
                self.final_pos_str = line
            elif "set time:" in line:
                if self.restart == 2:
                    self.restart = 1

            for target in self.target_row:
                if line.startswith(self.row_flag_dict[target][0]) and self.row_flag_dict[target][1] in line \
                        and target not in one_sec_row.keys():
                    if self.is_intact(line, target):
                        one_sec_row[target] = line
                    else:
                        print("The %d row << %s >> is incomplete" % (self.row_cnt, line))
            ''' 重启标志 '''
            if "cce load over" in line:
                self.restart = 2
                self.pos = self.f_our.tell()
                return {}
            ''' 1 秒标志 '''
            if flag_one_sec in line:
                self.pos = self.f_our.tell()
                return one_sec_row

        self.pos = self.f_our.tell()
        return one_sec_row

    def get_ubx_time(self):
        line = self.f_ubx.readline()
        while line:
            if "gpsTOW" in line:
                ret = re.findall(r"\d+", line)
                ubx_time = round(int(ret[1]) / 1000)
                if self.ubx_bak_time - ubx_time > 30240:
                    ubx_time += 604800  # 到下一周了
                self.ubx_bak_time = ubx_time
                return ubx_time
            line = self.f_ubx.readline()
        return -1

    def parser_ubx_txt(self):
        next_field = 0
        all_sv_info_dict = {}  # {gps: {'svId': {'cnr': 38, 'pli': 5, }, }, BD: {'svId': {'cnr': 45, 'pli': 3, }, } }
        line = self.f_ubx.readline()
        while line:
            line = self.f_ubx.readline()
            if not line:
                print("ubx file end")
                return {}
            if "--------" in line:
                break
            elif "rcvTow" in line:
                next_field = 1
                continue

            ret = line.split()
            if not bool(ret) or ret[0].isalpha():  # ret = [] or ret[0] is not num
                continue

            if next_field:
                if float(ret[0]) < 1e6:
                    continue
                if ret[3] not in ['0', '5']:
                    continue
                if ret[4] not in all_sv_info_dict[ret[3]]:
                    continue

                all_sv_info_dict[ret[3]][ret[4]]["PR"] = float(ret[0])

                continue

            if ret[0].isdigit():  # 字符都是数字，为真返回 Ture，否则返回 False
                if ret[0] not in ['0', '5']:
                    continue
                if ret[0] in all_sv_info_dict.keys():
                    all_sv_info_dict[ret[0]][ret[1]] = {"cnr": int(ret[2]), "dopp": float(ret[5])}
                else:
                    all_sv_info_dict[ret[0]] = {ret[1]: {}}
                    all_sv_info_dict[ret[0]][ret[1]] = {"cnr": int(ret[2]), "dopp": float(ret[5])}
        return all_sv_info_dict

    def parser_file(self):
        _all_info_list = []
        t_our = -1
        t_ubx = -1
        val_our = 0
        val_ubx = 0
        max_td = 0.2  # unit s
        parser_field_dict = {}
        while self.pos < self.FILE_LEN:
            if self.cmp_enable and self.cmp_support:
                if not val_our:
                    field_dict = self.one_second_field()
                    if not bool(field_dict):  # this second field is empty
                        continue
                    parser_field_dict = self.parser_field(field_dict)
                    if self.restart:
                        continue
                    try:
                        t_our = parser_field_dict["chl_time"]
                    except:
                        continue
                    if t_our == -1:
                        continue

                if not val_ubx:
                    t_ubx = self.get_ubx_time()
                    if t_ubx == -1:
                        print("ubx file end, can't match the time ", t_our)
                        break

                td = t_our - t_ubx
                if td > max_td:
                    val_our = 1
                elif td < -max_td:
                    val_ubx = 1
                else:
                    val_our = 1
                    val_ubx = 1

                if val_our and val_ubx:  # time match!
                    val_our = 0
                    val_ubx = 0
                    tmp_dict = self.parser_ubx_txt()
                    if not bool(tmp_dict):
                        continue
                    self.ubx_info_dict[t_our] = tmp_dict
                    _all_info_list.append(parser_field_dict)
            else:
                field_dict = self.one_second_field()
                #field_dict = self.extract_target_row()
                if bool(field_dict):
                    file_dict = self.parser_field(field_dict)
                    try:
                        if file_dict["chl_time"] == -1:
                            continue
                    except:
                        continue
                    _all_info_list.append(file_dict)

        if len(_all_info_list) == 0:
            sys.exit("find nothing valid information. Please make sure the input file is right")
        self.all_info_list = _all_info_list  # [{"cnr": [], "pli": [], "pr": [], }, {2sec info}, ... ]
        self._transpose_()
        self.all_valid_chl = self.valid_chl_list(self.valid_chl_flag)

    def parser_field(self, field_dict):
        _result = {}
        for key in field_dict.keys():
            _result.update(self.parser_row(key, field_dict[key]))
        return _result

    def parser_row(self, row_flag, row):
        _result_ = {}
        if row_flag == "chl_time":
            ret = self.second_of_week(row)
            _result_ = {row_flag: ret}  # float

        elif row_flag == "GGA" or row_flag == "GGAKF" or row_flag == "GFM" or row_flag == "GGAIGG":
            GGA = row.split(',')
            if GGA[6] == '1':
                alt = float(GGA[9])  # 海拔
                alt_GS = float(GGA[11])  # 高程异常
                high = alt + alt_GS  # 椭球高
                lat = LogParser.GGA_ll_to_float(GGA[2])
                lon = LogParser.GGA_ll_to_float(GGA[4])

                xyz = lla_to_xyz(lat, lon, high)
                _result_ = {row_flag: {"lat": lat, "lon": lon, "high": high, "xyz": xyz, 'valid': 1}}
            else:
                _result_ = {row_flag: {'valid': 0}}  # {}

        elif row_flag == "RMC" or row_flag == "RMCKF":
            # speed = float(re.findall(r"\d+\.?\d*", row)[3]) * 0.514
            RMC = row.split(',')
            if RMC[7]:
                speed = float(RMC[7]) * 0.514  # float
            else:
                speed = None
            if RMC[2] == 'A':
                _result_ = {row_flag: {"speed": speed, 'valid': 1}}
            else:
                _result_ = {row_flag: {"speed": speed, 'valid': 0}}  # {}

        elif row_flag == "cnr" or row_flag == "pli" or row_flag == "dli" or \
                row_flag == "svINFO" or row_flag == "prnNOW":
            ret = re.findall(r"\d+", row)  # [char, ]
            ret_arr = np.array([int(i) for i in ret])
            _result_ = {row_flag: ret_arr}

        elif row_flag == "dopp" or row_flag == "PR":
            ret = re.findall(r"-?\d+\.?\d*", row[:row.index("ir")])
            _result_ = {row_flag: [float(i) for i in ret]}  # [float, ]

        elif row_flag == "fix_sv":
            ret = row[row.index(self.row_flag_dict[row_flag]): row.index(',')]
            _result_ = {row_flag: int(ret)}     # int

        elif row_flag == "val_num":
            ret = re.findall(r"\d+", row)[0]
            _result_ = {row_flag: int(ret)}     # int

        return _result_

    def second_of_week(self, string):
        """获取本周内的秒计数, 如果跨周, 就加上60480"""
        _time_sec = LogParser.chl_time_parse(string)
        if _time_sec < 100 or self.time_bak - _time_sec > 302400:
            if self.time_bak != -1:
                if self.restart:  # 重启
                    if self.restart == 1:  # 重启 后 又 set time
                        if np.fabs(_time_sec - self.time_bak) < 100:
                            self.restart = 0
                    return -1
                _time_sec += 604800  # 没有重启 说明到下一周了
            else:
                return -1  # 板子刚上电

        if self.restart == 1:  # 重启 后 又 set time
            if np.fabs(_time_sec - self.time_bak) < 100:
                self.restart = 0
            return -1
        self.time_bak = _time_sec
        return _time_sec

    def _transpose_(self):
        for key in self.target_row:
            self.all_info_dict[key] = []
        for info in self.all_info_list:
            for key in info.keys():
                self.all_info_dict[key].append(info[key])
            if "prnNOW" not in info.keys():
                self.all_info_dict["prnNOW"].append([])
            if "svINFO" not in info.keys():
                self.all_info_dict["svINFO"].append([])

    def valid_chl_list(self, valid_chl_flag):
        valid_chl_lst = []
        for sv_info in self.all_info_dict["svINFO"]:
            valid_chl_lst.append(self.valid_chl_per_sec(sv_info, valid_chl_flag))
        return valid_chl_lst

    @staticmethod
    def valid_chl_per_sec(sv_info, valid_chl_flag):
        valid_chl = []
        for idx, item in enumerate(sv_info):
            if item in valid_chl_flag:
                valid_chl.append(idx)
        return valid_chl

    @staticmethod
    def chl_time_parse(row):
        _ret = row.split(',')
        return round(int(_ret[1]) / 1000)

    @staticmethod
    def GGA_ll_to_float(ll_str):
        """
        :param ll_str:  GGA经纬度字符串
        :return: 转换GGA经纬度字符串 为 浮点数 (unit 度
        """
        ll_int_part = float(ll_str[: ll_str.find('.') - 2])
        ll_min_part = float(ll_str[ll_str.find('.') - 2:]) / 60.0
        return ll_int_part + ll_min_part
