class fsol_cd_t(BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        # (字段名, c类型 )
        ('lst', 'I'),   # unsigned short
        ('sys', 'B'),   # unsigned char
        ('val', 'B'),   # unsigned char
        ('STU_COOR_LLA', 'p'),
        ('fall_t', c_uint16),
        ('arrOptional', c_char * 20),
    ]

    def encode(self):
        return string_at(addressof(self), sizeof(self))

    def decode(self, data):
        memmove(addressof(self), data, sizeof(self))
        return len(data)

"""
Typedef struct
{
    U16 lst； // 闰秒，保留
    U08 sys;  // 闰秒系统，保留
    U08 val；// 当前顺时定位有效标志，保留
    STU_COOR_LLA plla; // 最终定位位置（经纬高）
    fall_t fall;	// 所有累计定位的统计平均信息
    fstat_t fstat; // 定位读写更新时间段内的状态统计平均信息
} fsol_cd_t;

Typedef struct
{
    TYP_F32 lon；// 经度
    TYP_F32 lat； // 纬度
    F32 alt； // 高度
} STU_COOR_LLA；

Typedef struct
{
    U08 avepli;	//用于定位星的平均pli
    U08 avecnr; // 用于定位星的平均载噪比
    U32 ircnt； // 累计中断数
    U32 nval;  // 累计有效定位数
    F32 warn_pv_rate[2]；// 静态警告率，普通警告率
    F32 avensv; // 定位时间段内的平均定位卫星数
} fall_t;

Typedef struct
{
    U32 nsv;  // sv数组中有效卫星数量
    U08 sv[12]；// 定位卫星的sv 索引
    U08 avepli[12]; // 各定位卫星用于定位的平均pli
    U08 avecnr[12]; // 各定位卫星用于定位的平均载噪比
    U32 svnfix[10];	// 各定位卫星用于定位的次数
    U32 rw_flag； // 本地读写flag
    U32 ircnt;	 // 累计中断数
    U32 nval;	// 累计有效定位数
    F32 warn_pv_rate[2];// 静态警告率，普通警告率
    F32 avensv; //  定位时间段内的平均定位卫星数
} fsol_stat_t;
"""