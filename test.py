from heapq import heappop, heappush


class PriorityQueue:

    def __init__(self, iterable=[]):
        self.heap = []
        for value in iterable:
            heappush(self.heap, (0, value))

    def add(self, value, priority=0):
        heappush(self.heap, (priority, value))

    def pop(self):
        priority, value = heappop(self.heap)
        return value

    def __len__(self):
        return len(self.heap)



p = PriorityQueue()

p.add(-1, "bei")
print(p.heap)
p.add(-2, "bei")
print(p.heap)

city_dangers = {'南京': 0.5, '北京': 0.9, '成都': 0.5, '杭州': 0.2, '广州': 0.5, '武汉': 0.9, '上海': 0.9, '重庆': 0.2, '青岛': 0.9,
                '深圳': 0.2, '郑州': 0.5, '西安': 0.2}
dangers_arg = [0.2, 0.5, 0.9]
trans_dangers = {"汽车": 2, "火车": 5, "飞机": 9}

print( (city_dangers["南京"] * 10 + trans_dangers["火车"] * 10) / 60 )

def parse_time(time_str):
    return list(map(int, time_str.split(":")))

print(parse_time("9:15"))

