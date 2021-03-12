#!/usr/bin/env python3

import os
path_file = "/home/kwq/project/C/codelite_proj/struct_data_parse/struct_parse/log/3010"

gga = "$GPGGA,024028.00,4000.0013,N,11559.9974,E,1,10,1.22,113.714,M,-8.00,M,,*78"
gga_head = "$GPGGA,"
gga_time = "010038.00,"
gga_tail = ",E,1,10,1.22,113.714,M,-8.00,M,,*78"

gga_file = open("gga.txt", 'w')
with open(path_file, 'r') as fd:
    for row in fd:
        if len(row) < 11:
            continue
        s = ''
        try:
            s = row.split('47 50 53 3A ')[1]
        except:
            continue

        if s:
            hour = int(gga_time[:2]) + 1
            if hour > 23:
                hour = 0
            if hour < 10:
                gga_time = '0' + str(hour) + gga_time[2:]
            else:
                gga_time = str(hour) + gga_time[2:]

            exe = './struct_parse ' + s
            p = os.popen(exe)
            data = p.read()
            data_lst = data.split('\n')
            lon_str = data_lst[1].split('=')[-1]
            lat_str = data_lst[2].split('=')[-1]

            tmp_idx = lon_str.index('.')
            minute = round(float(lon_str[tmp_idx:]) * 60, 4)
            if minute < 10:
                lon_gga = lon_str[:tmp_idx].lstrip() + '0' + str(minute)
            else:
                lon_gga = lon_str[:tmp_idx].lstrip() + str(minute)

            tmp_idx = lat_str.index('.')
            minute = round(float(lat_str[tmp_idx:]) * 60, 4)
            if minute < 10:
                lat_gga = lat_str[:tmp_idx].lstrip() + '0' + str(minute)
            else:
                lat_gga = lat_str[:tmp_idx].lstrip() + str(minute)

            gga = gga_head + gga_time + lat_gga + ',N,' + lon_gga + gga_tail

            print(gga, file=gga_file)

# hex_str = ''
# for i in all_txt.split(' '):
#     hex_str += i
# hex_str = ''.join(all_txt.split())
# try:
#     valid_str = hex_str.split('4750533A')[1]
# except:
#     valid_str = hex_str
#
# print(valid_str)
#
# hex_mem = bytes.fromhex(valid_str)
# print(hex_mem)
#
#
# f_out = open("./out.bin", 'wb')
# f_out.write(hex_mem)
