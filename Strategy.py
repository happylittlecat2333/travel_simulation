from heapq import heappush, heappop
from math import radians, cos, sin, asin, sqrt
import Data


def parse_time(time_str):  # convert "9:15" to int [9, 15]
    return list(map(int, time_str.split(":")))


#    hour, second = list(map(int, time_str.split(":")))  # convert "9:15" to int (9, 15)
#    return [hour, second]


print(parse_time("9:15"))


def sum_time(time_list):  # 返回总时间（分钟为单位）
    return time_list[0] * 60 + time_list[1]


class PriorityQueue:  # 基于堆实现的优先队列，value=[node,current_time], priority=危险值
    def __init__(self):
        self.heap = []

    def add(self, value, priority=0):
        heappush(self.heap, (priority, value))  # 根据priority排序，保证value和priority一直在一起

    def pop(self):
        priority, value = heappop(self.heap)
        return value

    def __len__(self):
        return len(self.heap)


def get_goal_function():
    def is_end(place, end):
        return place == end

    return is_end


def reconstruct_path(came_from, start, end):  # 构造路线（从终点到起点构造）
    if end not in came_from:  # 如果A*算法执行完找不到路线，返回None
        return None
    reverse_path = []
    while end != start:  # 由后继节点指向父节点
        route_info = came_from[end]  # {"上海": ('北京', '上海', '火车', 'G143', '7:50', '5:22', 553)}
        end = came_from[end][0]  # "北京"
        reverse_path.append(route_info)  # 翻转，变为从起点到终点的顺序
    return list(reversed(reverse_path))


def sum_danger(node, wait_time, trans, route_time):  # 在城市停留的风险值 + 在交通工具上的风险值
    return (Data.city_dangers[node] * wait_time + Data.trans_dangers[trans] * route_time) / 60


def get_successor_function():  # 找到所有后继节点
    def get_adjacent_nodes(node, current_time):
        all_best_successor = []
        successor_dict = {}
        for index, data in enumerate(Data.time_table_values):  # 所有班次的时间表
            if data[0] == node:  # 班次的起点与node相同
                wait_minutes = sum_time(parse_time(data[4])) - sum_time(current_time)  # start_time - current_time
                if wait_minutes >= 0:
                    destination = data[1]
                    trans = data[2]  # 交通工具
                    route_minutes = sum_time(parse_time(data[5]))  # 路程时间
                    if destination not in successor_dict:  # 新增后继节点
                        successor_dict[destination] = [sum_danger(node, wait_minutes, trans, route_minutes), index]
                    else:
                        old_danger = successor_dict[destination][0]
                        new_danger = sum_danger(node, wait_minutes, trans, route_minutes)
                        if old_danger > new_danger:  # 风险更小，更新后继节点信息
                            successor_dict[destination] = [new_danger, index]
        # print(successor_dict)
        return successor_dict

    return get_adjacent_nodes


def geo_distance(lng1, lat1, lng2, lat2):  # 根据经纬坐标计算在地球中的实际距离
    lng1, lat1, lng2, lat2 = map(radians, [float(lng1), float(lat1), float(lng2), float(lat2)])
    dlon = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    r = 2 * asin(sqrt(a)) * 6371 * 1000  # 地球平均半径，6371km
    r = round(r / 1000, 3)
    return r


def get_heuristic():  # 从node到终点的预估危险值
    def heuristic(node, end):
        geo_distance_km = geo_distance(Data.map_geo[node][0],  # node和end的经纬坐标
                                       Data.map_geo[node][1],
                                       Data.map_geo[end][0],
                                       Data.map_geo[end][1])
        return 5 * geo_distance_km / 60  # 按汽车平均时速60，感染风险为5

    return heuristic


def update_time(index):  # 返回经过班次后的时间
    update_minutes = sum_time(parse_time(Data.time_table_values[index][4])) + sum_time(
        parse_time(Data.time_table_values[index][5]))  # 班次的起始时间 + 班次的路程时间
    h = update_minutes // 60
    m = update_minutes % 60
    if h >= 24:  # 设计为每天相同班次，允许跨天
        print("NEXT DAY!!")
        h = h % 24
    return [h, m]


def is_in_limit_time(limit_time, index):    # 是否在规定的时间
    end_time = sum_time(parse_time(Data.time_table_values[index][4])) + sum_time(
        parse_time(Data.time_table_values[index][5]))  # 班次的起始时间 + 班次的路程时间
    return limit_time >= end_time


def a_star_graph_search(
        start,
        end,
        start_time,
        limit_time,
        goal_function,
        successor_function,
        heuristic
):
    visited = set()  # 关闭列表
    came_from = dict()  # 标记父节点
    dangers = {start: 0}  # 加权危险值
    frontier = PriorityQueue()  # 开启列表（按照加权危险值排序）
    current_time = parse_time(start_time)
    frontier.add([start, current_time], priority=0)  # 出发点入开启列表，优先级最高
    # print(limit_time)
    while frontier:
        node, current_time = frontier.pop()  # node="北京"（开启列表中优先级最高（加权危险值最低）的节点）

        # print("node popped name:", node)
        # print("current time:", current_time)
        if node in visited:  # 已经在关闭列表中
            continue
        if goal_function(node, end):  # 到达终点，返回路线
            return reconstruct_path(came_from, start, node)
        visited.add(node)
        for successor_node, successor_info in successor_function(node,
                                                                 current_time).items():  # successor=[all_danger, index]
            # print(successor_node)
            # print(successor_info)
            update_t = update_time(successor_info[1])  # 更新时间
            priority_update = dangers[node] + successor_info[0] + heuristic(successor_node, end)
            # 计算优先级 F = G + H （到后继节点的危险值 + 从后继节点到终点的预估危险值）

            # print("successor_node:", successor_node)
            print("update_t:", update_t, sum_time(update_t))
            # print("danger:", priority_update)
            if is_in_limit_time(limit_time, successor_info[1]) or limit_time == -1:  # -1代表最小风险策略，否则使用规定时间的策略
                frontier.add(  # 把后继节点添加到开启列表
                    [successor_node, update_t],
                    priority=priority_update
                )
                new_danger = successor_info[0] + dangers[node]  # 经过node到达后继节点的加权危险值
                # print("new_danger:", new_danger, "old_danger:", dangers[node])
                if successor_node not in dangers or new_danger < dangers[successor_node]:  # 经过node到达后继节点危险值更低
                    dangers[successor_node] = new_danger
                    time_table_index = successor_info[1]
                    came_from[successor_node] = Data.time_table_values[time_table_index]  # 更新父节点的指向
                    # print("add:", came_from[successor_node])

    return reconstruct_path(came_from, start, end)


class Solution:

    def __init__(self, start_place="北京", end_place="广州", start_time="9:15", limit_time=-1):
        self.start_place = start_place
        self.start_time = start_time
        self.end_place = end_place
        if limit_time != -1:  # 限时最小风险策略
            self.limit_time = limit_time * 60  # 分钟为单位
        else:  # 最小风险策略
            self.limit_time = -1

    def shortestPath(self, start_place="北京", end_place="广州", start_time="9:15", limit_time=-1):
        self.start_place = start_place
        self.start_time = start_time
        self.end_place = end_place
        if limit_time != -1:  # 限时最小风险策略
            self.limit_time = limit_time * 60  # 分钟为单位
        else:  # 最小风险策略
            self.limit_time = -1
            
        shortest_path = a_star_graph_search(  # A*算法
            start=self.start_place,  # 出发地
            end=self.end_place,  # 终点
            start_time=self.start_time,  # 出发时间
            limit_time=self.limit_time,  # 限制时间
            goal_function=get_goal_function(),  # 判断是否到达终点
            successor_function=get_successor_function(),  # 寻找后继节点
            heuristic=get_heuristic()  # 启发函数，预计到终点的移动耗费
        )
        return shortest_path
