#!/usr/bin/env python3
import os
import sys
import time
sys.path.extend([".."] + [os.path.join(root, name) for root, dirs, _ in os.walk("../") for name in dirs])
from core import LogParser
# from log_analysis.core import LogParser
from core import chart_init
from base_function import calc_True_Txyz


if __name__ == '__main__':
    num_argv = len(sys.argv)
    if num_argv < 2:
        # path = "/home/kwq/work/east_window/0316/"
        # ubx_txt = path + "COM3_210316_114345_F9P.txt"
        # ubx_gga = path + "nmea/COM3_210316_114345_F9P.gga"
        path = "/home/kwq/work/out_test/0401/cd236_test/"
        ubx_txt = path + "COM7_210401_082809_gan_F9P.txt"
        ubx_gga = path + "nmea/COM7_210401_082809_gan_F9P.gga"
    else:
        path = sys.argv[1]
        ubx_txt = path + sys.argv[2]
        ubx_gga = path + "nmea/" + sys.argv[2].split('.')[0] + ".gga"
    print(path)
    print(ubx_txt)
    print(ubx_gga)

    if os.stat(ubx_txt).st_size < 1000:
        print(ubx_txt + " too short, size = %d" % os.stat(ubx_txt).st_size + "Bytes")
        ubx_txt = ''

    file_lst = [f for f in os.listdir(path) if f.endswith('.log') or f.endswith('DAT')]
    # file_lst = ["1_mdl5daa_fixRst_east.log"]
    file_lst.sort()
    purpose = {"cnr": ["mean", "std"], "pli": ["mean"], "pos": ["cep50", "cep95", "cep99", "mean", "std"],
                "PR": ["cmp"], "dopp": ["cmp"]}
    # purpose = {"cnr": ["mean", "std"], "pli": ["mean"], "pos": ["cep50", "cep95", "cep99", "mean", "std"],}

    fd_summary_table = chart_init(path)
    Txyz, Tlla, mean_err_dis, std_err_dis = calc_True_Txyz(ubx_gga)
    print("ubx position =", Txyz, Tlla)

    for file in file_lst:
        print(file, end='|', file=fd_summary_table)
        test = LogParser(path+file, purpose, ubx_txt, fd_summary_table)

        start_time = time.time()  # 开始时间
        test.parser_file()
        end_time = time.time()  # 结束时间
        print("耗时: %d" % (end_time - start_time))

        '''进行的操作操作'''
        test.final_pos_analysis(Txyz)
        test.static_pos_cmp(Txyz)
        test.pli_abnormal_pli_mean_cnr_mean()
        if len(ubx_txt):
            test.cnr_cmp()
            test.pr_cmp()
            test.dopp_cmp()
        del test
        print('\n\n')
    print("\n------\n", file=fd_summary_table)