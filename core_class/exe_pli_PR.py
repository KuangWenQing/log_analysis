import os
import sys
import matplotlib.pyplot as plt
from log_analysis import LogAnalysis


if __name__ == '__main__':
    num_argv = len(sys.argv)
    if num_argv < 2:
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
    file_lst.sort()
    purpose = {"pli": ["mean"], "dli": ["mean"], "PR": ["cmp"], "dopp": ["cmp"]}

    for file in file_lst:
        test = LogAnalysis(path + file, purpose, ubx_txt)
        '''进行的操作操作'''
        PR_all, pli_all = test.pli_PR()
        del test
        print("\n------\n")
        plt.plot(pli_all, PR_all, marker='*')
        plt.show()
