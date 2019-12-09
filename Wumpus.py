'''
Created on Apr 10, 2019

@author: neal
'''
import random
import numpy as np
import math


class WumpusWorld(object):

    def __init__(self, width=10, height=10, startloc=0, endloc=99):
        self.size = width*height
        self.width = width
        self.height = height

        self.current = 0
        self.point = 0

        # 使用5个长度为100的list记录地图
        # 1为该房间内存在该元素，0为不存在，初始状态均为0
        self.stenchloc = [0]*self.size
        self.breezeloc = [0]*self.size
        self.wumpusloc = [0]*self.size
        self.pitloc = [0]*self.size
        self.goldloc = [0]*self.size

        self.startloc = startloc
        self.endloc = endloc

    def generate(self, number=3):
        # 生成随机地图
        banList = set([self.startloc, self.endloc])  # 用来记录禁止生成新元素的位置

        # 生成金矿
        temp = random.randint(0, self.size-1)
        while temp in banList:
            temp = random.randint(0, self.size-1)
        self.goldloc[temp] = 1
        banList.add(temp)

        for _ in range(number):
            # 生成怪兽
            temp = random.randint(0, self.size-1)
            while temp in banList:
                temp = random.randint(0, self.size-1)
            self.setwumpus(temp)
            banList.add(temp)
            # 生成陷阱
            temp = random.randint(0, self.size-1)
            while temp in banList:
                temp = random.randint(0, self.size-1)
            self.setpit(temp)
            banList.add(temp)

    def neighbors(self, location):
        # 生成某个位置的相邻位置
        result = []
        # 上
        if location//self.width != self.height-1:
            result.append(location+self.width)
        # 左
        if location % self.width != self.width-1:
            result.append(location+1)
        # 下
        if location//self.width != 0:
            result.append(location-self.width)
        # 右
        if location % self.width != 0:
            result.append(location-1)
        return result

    def setwumpus(self, location):
        # 给定相应位置，生成怪兽
        self.wumpusloc[location] = 1
        # 添加臭味
        for i in self.neighbors(location):
            self.stenchloc[i] += 1

    def setpit(self, location):
        # 给定相应位置，生成陷阱
        self.pitloc[location] = 1
        # 添加风
        for i in self.neighbors(location):
            self.breezeloc[i] = 1

    def setwumpusManually(self, coordination):
        # 输入二维坐标，利用坐标生成怪兽
        # 将坐标转换为0—100的数字
        self.setwumpus(coordination[0]+self.width*coordination[1]-1-self.width)

    def setpitManually(self, coordination):
        # 输入二维坐标，利用坐标生成陷阱
        # 将坐标转换为0—100的数字
        self.setpit(coordination[0]+self.width*coordination[1]-1-self.width)

    def setgoldManually(self, coordination):
        # 输入二维坐标，利用坐标生成金矿
        # 将坐标转换为0—100的数字
        self.goldloc[coordination[0]+self.width *
                     coordination[1]-1-self.width] = 1

    def wumpusDie(self, location):
        # 怪兽死亡时，清空尸体和臭味
        self.wumpusloc[location] = 0
        for i in self.neighbors(location):
            self.stenchloc[i] -= 1

    def move(self, location, shoot=False, teleportation=False):
        # 当勇者移动到新房间时，处理事件，并返回房间的内容给勇者
        # 瞬间移动默认为False
        # 检查该移动是否是相邻的移动
        if location not in self.neighbors(self.current) and teleportation == False:
            print("illegal movement!")
            return
        self.point -= 1
        self.current = location
        # 处理死亡情况
        isDead = (self.pitloc[location] or (
            self.wumpusloc[location] and not shoot))
        if isDead:
            self.point -= 1000
        # 处理杀死怪兽的情况
        isKilled = self.wumpusloc[location] and shoot
        if isKilled:
            self.wumpusDie(location)
        # 进到金矿房时，自动奖分、挖坑
        isDig = False
        if self.goldloc[location]:
            self.point += 1000
            self.goldloc[self.current] = 0
            isDig = True
        return self.stenchloc[location], self.breezeloc[location], isDead, isKilled, isDig

    def printworld(self):
        # 将世界可视化
        printed_world = ["nnn"]*100
        # nnn表示什么都没有的空房间
        # w=wumpus, s=stench, b=breeze, p=pit, g=gold.
        for i in range(100):
            if self.breezeloc[i] and self.stenchloc[i]:
                if self.wumpusloc[i]:
                    printed_world[i] = "wbs"
                elif self.pitloc[i]:
                    printed_world[i] = "pbs"
                else:
                    printed_world[i] = "bbs"
            elif self.breezeloc[i] and not self.stenchloc[i]:
                if self.wumpusloc[i]:
                    printed_world[i] = "wwb"
                elif self.pitloc[i]:
                    printed_world[i] = "ppb"
                else:
                    printed_world[i] = "bbb"
            elif self.stenchloc[i] and not self.breezeloc[i]:
                if self.wumpusloc[i]:
                    printed_world[i] = "wws"
                elif self.pitloc[i]:
                    printed_world[i] = "pps"
                else:
                    printed_world[i] = "sss"
            else:
                if self.wumpusloc[i]:
                    printed_world[i] = "www"
                elif self.pitloc[i]:
                    printed_world[i] = "ppp"
            if self.goldloc[i]:
                printed_world[i] = "ggg"
        result = []
        for i in range(10):
            result.append(printed_world[10*i:10*(i+1)])
        print(np.matrix(result))

    def printworld_detail(self):
        # 打印确切的元素的坐标
        print("the locations of wumpuses are: ", end="")
        for i in range(100):
            if self.wumpusloc[i] == 1:
                print("("+str(i % 10+1)+","+str(i//10+1)+") ", end="")
        print("\nthe locations of pits are: ", end="")
        for i in range(100):
            if self.pitloc[i] == 1:
                print("("+str(i % 10+1)+","+str(i//10+1)+") ", end="")
        print("\nthe location of GOLD is: ", end="")
        for i in range(100):
            if self.goldloc[i] == 1:
                print("("+str(i % 10+1)+","+str(i//10+1)+") ", end="")
        print("")


class Protagonist(object):
    # 勇者
    def __init__(self, world: WumpusWorld, current=0, destination=99):

        self.current = current
        self.destination = destination
        self.wumpusworld = world

        # 这些表示勇者的知识，-1表示不知道有没有，1表示知道有，0表示知道没有
        self.knowstench = [-1]*self.wumpusworld.size
        self.knowBreeze = [-1]*self.wumpusworld.size
        self.knowWumpus = [-1]*self.wumpusworld.size
        self.knowPit = [-1]*self.wumpusworld.size
        # gold比较特殊，我们不需要区分-1和0，此处统一使用0表示
        self.knowGold = [0]*self.wumpusworld.size
        self.visitTimes = [0]*self.wumpusworld.size  # 记录每个位置到过的次数
        self.needUpdate = [0]*self.wumpusworld.size

        # 这些表示目前能确定位置的pit/wumpus的个数
        self.findPitNumber = 0
        self.findWumpusNumber = 0

        self.alive = True
        self.arrowNumber = 3
        self.isShoot = False  # 表示进入下一个房间前是否射箭
        self.findGold = False  # 表示是否已经找到了金矿

        self.point = 0

    def startAdventure(self):
        print("Start adventure!")
        print("Now you are in ("+str(self.current %
                                     10+1)+","+str(self.current//10+1)+")!")
        # 初始化勇者
        count = 0
        previous_location = -1
        self.move(self.current, teleportation=True)  # 将勇者瞬间移动到入口
        # 告诉勇者入口、出口都是安全的
        self.knowPit[self.destination] = self.knowWumpus[self.destination] = 0
        while self.alive == True and not (self.current == self.destination and self.findGold == True):
            count += 1
            # 遍历相邻房间，选择启发式函数值最小的走
            next_location = 0
            best_score = float("inf")
            neighbors = self.neighbors(self.current)
            random.shuffle(neighbors)
            for i in neighbors:
                score = self.Astar(i, previous_location)
                if score < best_score:
                    next_location = i
                    best_score = score
            previous_location = self.current
            # 怀疑下一步有怪兽时，准备射箭
            if self.knowWumpus[next_location] != 0:
                self.shot()
            self.move(next_location)
            # 重置开枪状态
            self.isShoot = False
            print("The "+str(count)+"-th step is ("+str(self.current % 10+1)+","+str(self.current//10+1)+")")
        if self.alive:
            print("Congratulations! you reach the destination with GOLD!")
        else:
            print("Sorry, you are dead.")
        print("Game Ends! Your point is", self.wumpusworld.point, "\n")
        return

    def neighbors(self, location):
        return self.wumpusworld.neighbors(location)

    def neighborsOfneighbors(self, location):
        # 返回目标房间距离小于等于2的所有房间
        result = self.neighbors(location)
        for i in self.neighbors(location):
            result += self.neighbors(i)
        return list(set(result))

    def Astar(self, i, previous_location):
        # 启发式函数，越小越好
        # 计算离终点的距离
        dist = abs(self.destination//10-i//10) + \
            abs(self.destination % 10-i % 10)
        # 计算怪物产生的权重
        wumpusScore = 50*(self.knowWumpus[i] == -1)/(self.arrowNumber+1)+100*(
            self.knowWumpus[i] == 1)*(self.arrowNumber == 0)
        # 计算陷阱产生的权重
        pitScore = 100*(self.knowPit[i] == -1)+100*(self.knowPit[i] == 1)
        # 鼓励往未探索过的区域走
        newroadScore = self.newroadScore(
            i)-math.sqrt((100-i)*(self.visitTimes[i] == 0))
        if self.findGold:
            # 找到金矿后，直线往终点走
            return dist+pitScore+wumpusScore+50*(i == previous_location)+self.visitTimes[i]
        else:
            # 未找到金矿时，鼓励往未探索过的位置走
            return dist+pitScore+wumpusScore+5*(i == previous_location)+10*self.visitTimes[i]+newroadScore

    def newroadScore(self, location):
        # 鼓励往未探索过的区域走
        result1 = 0
        result2 = 0
        count = 0
        for i in range(100):
            if self.visitTimes[i] == 0 and self.knowPit[i] != 1 and self.knowWumpus[i] != 1:
                count += 1
                result1 += (abs(location//10-i//10) +
                            abs(location % 10-i % 10))**(0.33)
                result2 += 100*(abs(location//10-i//10) +
                                abs(location % 10-i % 10))
        # 如果未探测过的格子太少的话，即使这些格子可能有危险，也要进去试一下运气
        # 不加wumpusNumber是因为到后期怪兽基本都杀光了
        if count >= 8-self.findPitNumber:
            return result1
        else:
            return result2

    def move(self, location, teleportation=False):
        # 勇者走向新的位置
        self.current = location
        self.visitTimes[location] += 1
        # 更新信息，并执行房间中的事件
        self.updateKnow(location, teleportation)
        # 如果是第一次来，或者房间信息需要更新，则利用更新的信息进行推理
        if self.visitTimes[location] == 1 or self.needUpdate[location] == 1:
            self.needUpdate[location] = 0
            # 没有风或臭味，周围就一定没有陷阱或怪兽
            if self.knowBreeze[location] == 0:
                for i in self.neighbors(location):
                    self.knowPit[i] = 0
            if self.knowstench[location] == 0:
                for j in self.neighbors(location):
                    self.knowWumpus[j] = 0
            # 判断是否可以推断出pit或wumpus的位置
            if self.findPitNumber < 3:
                self.updatePit()
            if self.findWumpusNumber < 3:
                self.updateWumpus()
            # 若找齐pit/wumpus，则把其他怀疑的位置标记为0
            if self.findPitNumber == 3:
                self.clearPit()
                self.findPitNumber += 100
            if self.findWumpusNumber == 3:
                self.clearWumpus()
                self.findWumpusNumber += 100

    def shot(self):
        print("Prepare to Shoot!")
        # 若没箭了，就告诉勇者没箭了。。。
        if self.arrowNumber == 0:
            print("No Arrow!")
            return
        self.isShoot = True
        self.arrowNumber -= 1

    def updateKnow(self, location, teleportation=False):
        # 更新勇者的知识并处理事件
        # 接受房间的事件处理情况
        self.knowstench[location], self.knowBreeze[location], isDead, isKilled, isDig = self.wumpusworld.move(
            location, self.isShoot, teleportation)
        # isDead表示勇者是否死亡
        if isDead:
            self.alive = False
        # isKilled表示是否有怪兽被杀死
        if isKilled:
            # 若杀死的怪兽是属于未知位置的怪兽，则找到的怪兽计数+1
            if self.knowWumpus[location] != 1:
                self.findWumpusNumber += 1
            # 重置周围的房间的臭味信息，标记为未知，且标记为信息需要更新
            for i in self.neighbors(location):
                self.knowstench[i] = -1
                self.needUpdate[location] = 1
            print("you KILL a wumpus!!")
        elif self.isShoot:
            print("Oops, no wumpus.")
        # 若存活，则更新信息
        if self.alive:
            self.knowWumpus[location] = self.knowPit[location] = 0
        # 处理挖到金矿的事件
        if isDig:
            self.findGold = True
            self.knowGold[location] = 1
            print("You find GOLD!!")

    def updatePit(self):
        # 判断能否确定某个房间一定有陷阱
        for i in self.neighborsOfneighbors(self.current):
            # 判断范围是现在所处的房间距离为2以内的全部房间
            if self.knowBreeze[i] == 1:
                # 如果一个有风的房间相邻房间中，只有一格不能确定没有陷阱，
                # 并且其他相邻房间都能确定没有陷阱，则不能确定没有陷阱的那格一定有陷阱
                safePitCount = 0  # 标记能确定没有陷阱的格数
                for neighbor in self.neighbors(i):
                    if self.knowPit[neighbor] == 0:
                        safePitCount += 1
                    if self.knowPit[neighbor] == 1:
                        safePitCount -= 100
                    if self.knowPit[neighbor] == -1:
                        loc = neighbor
                if safePitCount == len(self.neighbors(i))-1:
                    self.findPitNumber += 1
                    self.knowPit[loc] = 1

    def updateWumpus(self):
        # 判断能否确定某个房间一定有怪兽
        for i in self.neighborsOfneighbors(self.current):
            # 判断范围是现在所处的房间距离为2以内的全部房间
            if self.knowstench[i] == 1:
                # 如果一个有臭味的房间相邻房间中，只有一格不能确定没有怪兽，
                # 并且其他相邻房间都能确定没有怪兽，则不能确定没有陷阱的那格一定有怪兽
                safeWumpusCount = 0  # 标记能确定没有怪兽的格数
                for neighbor in self.neighbors(i):
                    if self.knowWumpus[neighbor] == 0:
                        safeWumpusCount += 1
                    if self.knowWumpus[neighbor] == 1:
                        safeWumpusCount -= 100
                    if self.knowWumpus[neighbor] == -1:
                        loc = neighbor
                if safeWumpusCount == len(self.neighbors(i))-1:
                    self.findWumpusNumber += 1
                    self.knowWumpus[loc] = 1

    def clearPit(self):
        # 找齐陷阱后，将所有不确定有无陷阱的房间都标记为没有陷阱
        for i in range(100):
            self.knowPit[i] = (self.knowPit[i] == 1)

    def clearWumpus(self):
        # 找齐怪兽后，将所有不确定有无陷阱的房间都标记为没有怪兽
        for i in range(100):
            self.knowWumpus[i] = (self.knowWumpus[i] == 1)

    def printhero(self):
        # 打印目前勇者的知识空间
        printed_world = ["nnn"]*100
        for i in range(100):
            if self.knowGold[i] == 1:
                printed_world[i] = "ggg"
            elif self.knowPit[i] == 1:
                printed_world[i] = "ppp"
            elif self.knowPit[i] == -1:
                printed_world[i] = "-p-"  # 表示不确定有没有陷阱
            elif self.knowWumpus[i] == 1:
                printed_world[i] = "www"
            elif self.knowWumpus[i] == -1:
                printed_world[i] = "-w-"  # 表示不确定有没有怪兽
            elif self.knowBreeze[i] and self.knowstench[i]:
                printed_world[i] = "bbs"
            elif self.knowBreeze[i] and not self.knowstench[i]:
                printed_world[i] = "bbb"
            elif self.knowstench[i] and not self.knowBreeze[i]:
                printed_world[i] = "sss"

            if self.visitTimes[i] == self.knowWumpus[i] == self.knowPit[i] == 0:
                printed_world[i] = "uuu"
            if i == self.current:
                printed_world[i] = "aaa"
        result = []
        for i in range(10):
            result.append(printed_world[10*i:10*(i+1)])
        print(np.matrix(result))


def test1():
    print("==================================================================")
    print("===================this is the TEST CASE test=====================")
    print("==================================================================")
    world = WumpusWorld()
    # 生成测试状态
    world.setpitManually((2, 6))
    world.setpitManually((5, 5))
    world.setpitManually((9, 9))
    world.setwumpusManually((3, 8))
    world.setwumpusManually((3, 3))
    world.setwumpusManually((8, 3))
    world.setgoldManually((5, 6))
    # 左上角是(1,1)，右下角是(10,10)，横向是x轴，纵向是y轴
    print("the real world is:")
    world.printworld()
    world.printworld_detail()
    # 开始冒险
    fighter = Protagonist(world)
    fighter.startAdventure()


def test2():
    print("==================================================================")
    print("==================this is the RANDOM CASE test====================")
    print("==================================================================")
    result = 0
    testtime = 10
    for i in range(testtime):
        print("This is the "+str(i+1)+"-th"+" test")
        # 生成测试状态
        world = WumpusWorld()
        world.generate()
        print("the real world is:")
        world.printworld()
        world.printworld_detail()
        # 开始冒险！
        fighter = Protagonist(world)
        fighter.startAdventure()
        result += fighter.wumpusworld.point
    print("the final average point is:")
    print(result/testtime)


if __name__ == '__main__':
    test1()
