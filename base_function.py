#!/usr/bin/env python3
import os
import sys
import math

import numpy as np

# 椭球高 = 海拔高 + 高程异常
R = 6378137     # 地球长半轴【m】
f_inv = 298.257224
f = 1.0 / f_inv     # earth flattening 扁率 (WGS84)
e2 = 1 - (1-f)*(1-f)


def lla_to_xyz(lat, lon, alt):
    """
    :param lat: 纬度
    :param lon: 经度
    :param alt: 椭球高
    :return: X, Y, Z
    """
    cos_lat = math.cos(lat * math.pi / 180)
    sin_lat = math.sin(lat * math.pi / 180)

    cos_lon = math.cos(lon * math.pi / 180)
    sin_lon = math.sin(lon * math.pi / 180)

    c = 1 / math.sqrt((cos_lat ** 2) + ((1-f) ** 2) * (sin_lat ** 2))
    s = (1 - f) ** 2 * c
    x = (R * c + alt) * cos_lat * cos_lon
    y = (R * c + alt) * cos_lat * sin_lon
    z = (R * s + alt) * sin_lat
    return round(x, 5), round(y, 5), round(z, 5)


def xyz_to_lla(x, y, z):
    DBL_EPSILON = 2.2204460492503131e-016
    GPS_EARTH_B = 6356752.3142451795
    GPS_ECC_2 = 0.00669437999014132
    USR_EPSILON = 1.0e-6
    dLat = 0.0
    sCnt = 0
    dr = math.sqrt(x**2 + y**2)
    if dr < DBL_EPSILON:
        dLon = 0.0
        if z < DBL_EPSILON:
            falt = -z - GPS_EARTH_B
            dLat = -(math.pi/2)
        else:
            falt = z - GPS_EARTH_B
            dLat = math.pi/2
    else:
        dLatTmp = dLat
        dSinLat = math.sin(dLatTmp)
        dTmp = GPS_ECC_2 * dSinLat
        dN = R / math.sqrt(1 - dTmp * dSinLat)
        dLat = R / math.atan((z + dN * dTmp) / dr)
        dErr = dLat - dLatTmp
        sCnt += 1
        while dErr > USR_EPSILON or dErr < -USR_EPSILON and sCnt < 10:
            dLatTmp = dLat
            dSinLat = math.sin(dLatTmp)
            dTmp = GPS_ECC_2 * dSinLat
            dN = R / math.sqrt(1-dTmp*dSinLat)
            dLat = math.atan((z + dN*dTmp)/dr)
            dErr = dLat - dLatTmp
            sCnt += 1
        dLon = math.atan2(y, x)
        dLat = dLat
        falt = dr / math.cos(dLat) - dN
    return dLat * 180/math.pi, dLon * 180/math.pi, falt


def ecef_to_enu(x, y, z, lat, lon, alt):
    """
    :输入： 正确的直角坐标xyz, 纬经高(椭球高
    :return: 东北天
    """
    cos_lat = math.cos(lat * math.pi / 180)
    sin_lat = math.sin(lat * math.pi / 180)
    cos_lon = math.cos(lon * math.pi / 180)
    sin_lon = math.sin(lon * math.pi / 180)
    c = 1 / math.sqrt((cos_lat ** 2) + ((1-f) ** 2) * (sin_lat ** 2))
    x0 = (R * c + alt) * cos_lat * cos_lon
    y0 = (R * c + alt) * cos_lat * sin_lon
    z0 = (R * c * (1 - e2) + alt) * sin_lat
    x_east = (-(x - x0) * sin_lon) + ((y - y0) * cos_lon)
    y_north = (-cos_lon * sin_lat * (x - x0)) - (sin_lat * sin_lon * (y -y0)) + (cos_lat * (z - z0))
    z_up = (cos_lat * cos_lon * (x - x0)) + (cos_lat * sin_lon * (y - y0)) + (sin_lat * (z - z0))
    return x_east, y_north, z_up


def convert_ll_to_float(ll_str):
    """
    :param ll_str:  GGA经纬度字符串
    :return: 转换GGA经纬度字符串 为 浮点数
    """
    ll_int_part = float(ll_str[: ll_str.find('.')-2])
    ll_min_part = float(ll_str[ll_str.find('.')-2: ll_str.find('.')]) / 60.0
    ll_sec_part = float(ll_str[ll_str.find('.'):])/60.0
    return ll_int_part + ll_min_part + ll_sec_part


def degree_to_dms(old_str='116.00001'):
    """度 转 度分秒"""
    degree = int(old_str[:old_str.index('.')])
    tmp = float(old_str[old_str.index('.'):])
    tmp_min = str(tmp * 60)
    min = int(tmp_min[:tmp_min.index('.')])
    sec = round(float(tmp_min[tmp_min.index('.'):]) * 60, 4)
    mix = str(degree) + ',' + str(min) + "'" + str(sec) + "''"
    return mix, degree, min, sec


def degree_to_df(old_str='116.00001'):
    """度 转 度分"""
    degree = int(old_str[:old_str.index('.')])
    tmp = float(old_str[old_str.index('.'):])
    fra = str(tmp * 60)
    if len(fra[:fra.index('.')]) == 1:
        fra = '0' + fra
    mix = str(degree) + fra[:fra.index('.')+5]
    return mix


def get_time_from_gga(row="$GPGGA,024028.00,4000.0013,N,11559.9974,E,1,10,1.22,113.714,M,-8.00,M,,*78"):
    """
    :param row:   GPGGA行
    :return:      sec_of_day,  original_str
    """
    GGA = row.split(',')
    time_str = GGA[1]
    time_sec = int(time_str[0:2]) * 3600 + int(time_str[2:4]) * 60 + float(time_str[4:])
    return time_sec, time_str


def get_llh_from_gga(row="$GPGGA,024028.00,4000.0013,N,11559.9974,E,1,10,1.22,113.714,M,-8.00,M,,*78"):
    """
    :param row:  GPGGA行
    :return:  纬度  经度  椭球高(Ellipsoid height)
    """
    GGA = row.split(',')
    lat_str = GGA[2]
    lon_str = GGA[4]
    alt = float(GGA[9])  # 海拔
    alt_GS = float(GGA[11])  # 高程异常
    lat = convert_ll_to_float(lat_str)
    lon = convert_ll_to_float(lon_str)
    return lat, lon, alt + alt_GS


def analysis_gga(Txyz=[-2144855.42272, 4397605.31284, 4078049.85099], row="$GPGGA,024028.00,4000.0013,N,11559.9974,E,1,10,1.22,113.714,M,-8.00,M,,*78"):
    """
    :param Txyz:真正的坐标[Tx, Ty, Tz]
    :param row:GPGGA行
    :return:时间秒, [经,纬,高], [x, y, z], [E, N, U], dis_xyz(与真值点的空间距离), dis_en(与真值点的水平距离)
    """
    time_sec, time_str = get_time_from_gga(row)

    lat, lon, ellipsoid_height = get_llh_from_gga(row)

    xyz = lla_to_xyz(lat, lon, ellipsoid_height)
    ENU = ecef_to_enu(Txyz[0], Txyz[1], Txyz[2], lat, lon, ellipsoid_height)
    diff_xyz = np.array(Txyz) - np.array(xyz)         # (Tx - x, Ty - y, Tz - z)
    dis_xyz = np.linalg.norm(diff_xyz)
    dis_en = np.linalg.norm(ENU[:2])
    return time_sec, (lat, lon, ellipsoid_height), xyz, ENU, dis_xyz, dis_en


def find_abnormal_data(arr=[]):
    """
    :param arr: 一组数
    :return: 按最像异常排列的索引
    """
    len_arr = len(arr)
    if len_arr < 3:
        print("Please enter an array with length greater than 3 ")
        return None

    tmp_sum = [0 for i in range(len_arr)]   # 存放差值和, 索引列表=[0, 1, 2, 3...(len_arr-1)]
    for i in range(len(arr)):
        for item in arr:
            tmp_sum[i] += np.fabs(arr[i] - item)

    idx = np.array(tmp_sum).argsort()[::-1]   # tmp_sum 从小到大排列后的索引列表, 再逆序

    return idx


def write_excel_xlsx(sheet, value, row_cnt=0):
    """ sheet 工作簿
        value 是写的内容
        row_cnt 表示写到表格第几行"""

    index = len(value)
    for i in range(0, index):
        row_cnt += 1
        for j in range(0, len(value[i])):
            sheet.cell(row=row_cnt, column=j+1, value=str(value[i][j]))
    return row_cnt


'''alt = 361.31     # 实验室窗户
lat = convert_ll_to_float("2936.1604")
lon = convert_ll_to_float("10618.0286")'''
'''alt = 285.3     # 楼下十字路口
lat = convert_ll_to_float("2936.19689")
lon = convert_ll_to_float("10618.02215")'''
'''alt = 280.2     # 公园林荫
lat = convert_ll_to_float("2936.33728")
lon = convert_ll_to_float("10618.06034")'''
'''alt = 275.2     # 公园开阔地
lat = convert_ll_to_float("2936.33509")
lon = convert_ll_to_float("10618.09311")'''
alt = 100     # 模拟器
lat = convert_ll_to_float("40000.00001")
lon = convert_ll_to_float("11600.00001")

Tlla = (lat, lon, alt)              # 度 （纬经高）
Txyz = lla_to_xyz(lat, lon, alt)    # 米 （X Y Z）

Tlat = degree_to_dms(str(Tlla[0]))[0]   # 度分秒 纬度
Tlon = degree_to_dms(str(Tlla[1]))[0]   # 度分秒 经度


def calc_True_Txyz(path_file):
    # gga中 经度纬度高度的位置
    lat_pos = 1
    lon_pos = 3
    alt_pos = 8
    with open(path_file, 'r') as f_F9P:
        all_XYZ = []
        error_distance = []
        GS_pos = 10  # 高程异常 Geoidal separation, 在第11个逗号后面
        for row in f_F9P:
            idx_lst = [idx for idx, item in enumerate(row) if item == ',']
            if len(idx_lst) < 14:
                continue
            lat_str = row[idx_lst[lat_pos] + 1:idx_lst[lat_pos + 1]]
            lon_str = row[idx_lst[lon_pos] + 1:idx_lst[lon_pos + 1]]
            alt = float(row[idx_lst[alt_pos] + 1:idx_lst[alt_pos + 1]])
            alt_GS = float(row[idx_lst[GS_pos] + 1:idx_lst[GS_pos + 1]])  # 高程异常

            lat = convert_ll_to_float(lat_str)
            lon = convert_ll_to_float(lon_str)
            xyz = lla_to_xyz(lat, lon, alt+alt_GS)
            all_XYZ.append(xyz)
        mean_all_XYZ = np.array(all_XYZ).mean(axis=0)       # [mean(all_x), mean(all_y), mean(all_z)]
        Txyz = list(mean_all_XYZ)
        for each_xyz in all_XYZ:
            distance = np.linalg.norm(np.array(each_xyz) - np.array(Txyz))
            error_distance.append(distance)
        mean_err_dis = np.mean(error_distance)
        std_err_dis = np.std(error_distance)
        Tlla = xyz_to_lla(mean_all_XYZ[0], mean_all_XYZ[1], mean_all_XYZ[2])

        return Txyz, Tlla, mean_err_dis, std_err_dis


if __name__ == "__main__":
    num_argv = len(sys.argv)
    if num_argv < 2:
        path = "/home/kwq/work/lab_test/0201_onenight/"

        F9P_file = path + 'COM8_210201_120953_F9P.txt'
    else:
        path = sys.argv[1]
        F9P_file = path + sys.argv[2]

    file_list = [f for f in os.listdir(path) if f.endswith('.log') or f.endswith('DAT')]
    file_list.sort()
    f9p_gga = path + 'nmea/' + [f for f in os.listdir(path + 'nmea/') if f.endswith('F9P.gga')][0]
    f9p_RMC_GGA = path + 'nmea/' + [f for f in os.listdir(path + 'nmea/') if f.endswith('F9P.rmcgga')][0]

    print(f9p_gga)

    Txyz, Tlla, mean_err_dis, std_err_dis = calc_True_Txyz(f9p_gga)
    print('F9P 均值点 作为 真值点')
    """米"""
    print(Txyz)     # xyz
    """度"""
    print(Tlla)     # 纬 经 椭球高
    Tlat = degree_to_dms(str(Tlla[0]))[0]  # 度分秒 纬度
    Tlon = degree_to_dms(str(Tlla[1]))[0]  # 度分秒 经度
    """度分"""
    print(degree_to_dms(str(Tlla[0]))[1], degree_to_dms(str(Tlla[0]))[2], str(float(degree_to_dms(str(Tlla[0]))[3])/60)[1:6], ', ',
          degree_to_dms(str(Tlla[1]))[1], degree_to_dms(str(Tlla[1]))[2], str(float(degree_to_dms(str(Tlla[1]))[3])/60)[1:6], ', ',
          Tlla[2])
    """度分秒"""
    print(Tlat, Tlon, Tlla[2])
    print("真值点的误差范围 ±", std_err_dis)
