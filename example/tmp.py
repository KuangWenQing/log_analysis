
path_file = "/home/kwq/work/east_window/0312/1_mdl5daa_seemfixMemOut_east.log"

f_our = open(path_file, 'r', errors="ignore")

final_pos_str = ''
row_cnt = 1
row_num = 0
line = f_our.readline()
while line:
    if "DEBUG R AVE, tot cnt: 2074070" in line:
        final_pos_str = line
        row_num = row_cnt
    line = f_our.readline()
    row_cnt += 1


print(row_num)
print(final_pos_str)
