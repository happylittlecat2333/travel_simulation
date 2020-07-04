city_dangers = {'南京': 0.5, '北京': 0.9, '成都': 0.5, '杭州': 0.2, '广州': 0.5, '武汉': 0.9, '上海': 0.9, '重庆': 0.2, '青岛': 0.9,
                '深圳': 0.2, '郑州': 0.5, '西安': 0.2}    # 在城市停留的风险值
trans_dangers = {"汽车": 2, "火车": 5, "飞机": 9}     # 交通工具的风险值

time_table_values = []  # 所有班次时间表
map_values = []     # 所有城市的经纬度信息
map_geo = {}        # 所有城市的经纬度，字典性的结构
all_place = []      # 所有航班里的城市


def load_data(cursor):  # 从数据库加载数据
    global time_table_values, map_values, map_geo, all_place  # 定义变量为全局变量，实现在函数内部改变变量值
    cursor.execute("select * from time_table where Tran=? ORDER BY RANDOM() limit 30", ('火车',))  # 30班次的火车
    time_table_values = cursor.fetchall()
    cursor.execute("select * from time_table where Tran=? ORDER BY RANDOM() limit 30", ('飞机',))  # 10班次的飞机
    tmp = cursor.fetchall()
    for i in tmp:
        time_table_values.append(i)
    cursor.execute("select * from time_table where Tran!=? and Tran!=?", ('飞机', '火车'))  # 所有汽车班次
    tmp = cursor.fetchall()
    for i in tmp:
        time_table_values.append(i)

    for i in time_table_values:
        if i[0] not in all_place:
            all_place.append(i[0])  # 全部班次的城市的集合

    cursor.execute("select * from map")  # 城市位置：经纬坐标
    map_values = cursor.fetchall()
    for i in map_values:
        if i[0] in all_place:
            map_geo[i[0]] = [i[1], i[2]]
    print(map_geo)
