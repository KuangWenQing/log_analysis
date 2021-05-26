#!/usr/bin/env python3
import os
import sys
import time
import matplotlib.pyplot as plt
sys.path.extend([".."] + [os.path.join(root, name) for root, dirs, _ in os.walk("../") for name in dirs])
from log_analysis import LogAnalysis
from base_function import calc_True_Txyz


def delete_file(pathname):
    if os.path.exists(pathname):  # 如果文件存在
        # 删除文件，可使用以下两种方法。
        os.remove(pathname)
        # os.unlink(path)   # 删除一个正在使用的文件会报错
    else:
        print('no such file: %s' % pathname)  # 则返回文件不存在


def chart_init(_path_):
    delete_file(_path_ + 'chart/_compare_dopp.xlsx')
    delete_file(_path_ + 'chart/_compare_PR.xlsx')
    delete_file(_path_ + 'chart/_compare_cnr.xlsx')
    fd_Summary_Table = open(_path_ + 'chart/summary_table.md', 'w')
    print("\n## " + _path_.split('/')[-2], file=fd_Summary_Table)
    print("log||final|||||pos||||||vel|||||pli|| |cnr||||PR|||dopp||", file=fd_Summary_Table)
    print(":---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|"
          ":---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|", file=fd_Summary_Table)
    print(".|Sep|Cep|sep50|sep95|sep99|sep std|cep50|cep95|cep99|cep std|v50|v95|v99|v std|fix rate|warning rate|"
          "mean|std|abnormal rate|mean|std|diff mean|diff std|"
          "mean[mean[diff_PR - diff_mean_PR]]|std[mean[diff_PR - diff_mean_PR]]|abnormal rate (100)|"
          "mean[mean[diff_dopp - diff_mean_dopp]]|std[mean[diff_dopp - diff_mean_dopp]]|abnormal rate (5)",
          file=fd_Summary_Table)
    return fd_Summary_Table


if __name__ == '__main__':
    num_argv = len(sys.argv)
    if num_argv < 2:
        path = "/home/kwq/work/east_window/0524_night/"
        ubx_txt = path + "COM3_210524_120351_F9P.txt"
        ubx_gga = path + "nmea/COM3_210524_120351_F9P.gga"
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
    # purpose = ["pos", "posKF"]
    purpose = ["cnr", "pli", "pos", "posKF", "PR", "dopp"]
    # purpose = {"cnr": ["mean", "std"], "pli": ["mean"], "PR": ["cmp"]}

    fd_summary_table = chart_init(path)
    Txyz, Tlla, mean_err_dis, std_err_dis = calc_True_Txyz(ubx_gga)
    print("ubx position =", Txyz, Tlla)

    for file in file_lst:
        # print(file, end='|', file=fd_summary_table)
        start_time = time.time()  # 开始时间
        test = LogAnalysis(path+file, purpose, ubx_txt)
        end_time = time.time()  # 结束时间
        print("耗时: %d" % (end_time - start_time))
        print(file + "  ")
        '''进行的操作操作'''
        test.cmp_with_true_draw_picture(Txyz, ["GGA", "GGAKF"])
        test.final_pos_analysis(Txyz, fd_summary_table)
        test.static_pos_cmp(Txyz, fd_summary_table)
        test.pli_abnormal_pli_mean_cnr_mean(fd_summary_table)
        if len(ubx_txt):
            test.cnr_cmp(fd_summary_table)
            test.pr_cmp(fd_summary_table)
            test.dopp_cmp(fd_summary_table)
        del test
        print('\n\n')
    print("\n------\n", file=fd_summary_table)



    # if os.stat(ubx_txt).st_size < 1000:
    #     print(ubx_txt + " too short, size = %d" % os.stat(ubx_txt).st_size + "Bytes")
    #     ubx_txt = ''

    # file_lst = [f for f in os.listdir(path) if f.endswith('.log') or f.endswith('DAT')]
    # file_lst = ["9_qfn_kfTst_pmdl_east.log"]
    # file_lst = [f for f in os.listdir(path) if f.endswith('z.log') or f.endswith('DAT')]
    # file_lst.sort()
    # purpose = ["pos", "posKF"]
    #
    # for file in file_lst:
    #     test = LogAnalysis(path + file, purpose, '')
    #     '''进行的操作操作'''
    #     # test.cmp_with_true_draw_picture([-1557931.6893273648, 5327181.764408474, 3132365.4582960745], ["GGA", "GGAKF"])
    #     test.cmp_with_true_draw_picture([-2144855.42, 4397605.31, 4078049.85], ["GGA", "GGAKF"])
    #     # PR_pli, PR_dli = test.pli_PR()
    #     # test.static_pos_cmp([-2144855.42, 4397605.31, 4078049.85])
    #     del test
    #     print("\n------\n")

        # plt.subplot(211)
        # xy = sorted(PR_pli.items(), key=lambda d: d[0])
        # x = [i[0] for i in xy]
        # y = [i[1] for i in xy]
        # plt.plot(x, y, marker='o')
        #
        # plt.subplot(212)
        # xy = sorted(PR_dli.items(), key=lambda d: d[0])
        # x = [i[0] for i in xy]
        # y = [i[1] for i in xy]
        # plt.plot(x, y, marker='*')
        # plt.show()
