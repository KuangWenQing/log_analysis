import os
import sys
import matplotlib.pyplot as plt
from log_analysis import LogAnalysis


if __name__ == '__main__':
    num_argv = len(sys.argv)
    if num_argv < 2:
        # path = "/home/kwq/work/east_window/0415/"
        # path = "/home/kwq/tmp/th/"
        path = "/home/kwq/work/east_window/0419_night/"
        ubx_txt = path + "COM3_210419_112956_F9P.txt"
        ubx_gga = path + "nmea/COM3_210419_112956_F9P.gga"
    else:
        path = sys.argv[1]
        ubx_txt = path + sys.argv[2]
        ubx_gga = path + "nmea/" + sys.argv[2].split('.')[0] + ".gga"
    print(path)
    print(ubx_txt)
    print(ubx_gga)

    # if os.stat(ubx_txt).st_size < 1000:
    #     print(ubx_txt + " too short, size = %d" % os.stat(ubx_txt).st_size + "Bytes")
    #     ubx_txt = ''

    # file_lst = [f for f in os.listdir(path) if f.endswith('.log') or f.endswith('DAT')]
    file_lst = ["1_qfn4caa_kfTst_pmdl_east.log"]
    # file_lst = [f for f in os.listdir(path) if f.endswith('.log')]
    file_lst.sort()
    # purpose = ["pli", "dli", "PR", "dopp", "pos", "posKF"]
    purpose = ["PR"]

    for file in file_lst:
        test = LogAnalysis(path + file, purpose, ubx_txt)
        '''进行的操作操作'''
        # test.cmp_with_true_draw_picture([-1557909.6662893195, 5327327.445091481, 3132300.496464893], ["GGA", "GGAKF"])
        #
        PR_pli, PR_dli = test.pli_PR()
        # test.not_fix_analysis()
        del test
        print("\n------\n")

        plt.subplot(211)
        xy = sorted(PR_pli.items(), key=lambda d: d[0])
        x = [i[0] for i in xy]
        y = [i[1] for i in xy]
        plt.plot(x, y, marker='o')

        plt.subplot(212)
        xy = sorted(PR_dli.items(), key=lambda d: d[0])
        x = [i[0] for i in xy]
        y = [i[1] for i in xy]
        plt.plot(x, y, marker='*')
        plt.show()
