import re
import numpy as np
import matplotlib.pyplot as plt

path_name = "/home/kwq/8_mdl5daa_hVarVel_kfTst_east.log"

with open(path_name, 'r') as fd:
    ref_std = []
    for row in fd:
        if row.startswith("val num"):
            num = int(re.findall(r"-?\d+", row)[0])
        if row.startswith("PDT REF"):
            ref_str = row.split(',')[2:]
            ref = [int(s) for s in ref_str]
            ref = ref[:num]
            ref_std.append(np.std(ref))
    x_arr = [x for x in range(len(ref_std))]
    plt.plot(x_arr, ref_std, marker='*')
    plt.show()

