# -*- coding: UTF-8 -*-
# Python 3.9
import random
import numpy as np
import matplotlib.pyplot as plt
import configparser
plt.rcParams['font.sans-serif']=['SimHei']

'''
10人进行博弈，你作为其中之一，尽力取得高分
A. 谨慎（+1）
B. 公正（与选此选项的玩家平分3分）
C. 团结（选此选项的玩家最多时，每人+2分）
D. 智慧（人数最少时，每人+2分）
E. 勇气（若仅有你一人选择此项，+4分）
'''

from Strategy import normal

class StrategyParameters:
    """
    表示游戏策略的参数。

    参数：
        config_file (str)：配置文件的路径。

    属性：
        NUM_PLAYERS (int)：游戏中的玩家数量。
        NUM_OPTIONS (int)：游戏中的选项数量。
        NUM_EPOCHS (int)：游戏中的循环次数。
        is_communicate (bool)：指示游戏中是否允许通信。
        pList (list)：初始概率列表。
        LEARN_RATE_UP (float)：增加概率的学习率。
        LEARN_RATE_DOWN (float)：减少概率的学习率。
        WIS_VALUE (float)：智慧策略的值。
        SOLID_VALUE (float)：团结策略的值。
        show (int)：展示次数。
        avg_score (list)：平均得分列表。
        iter (int)：迭代次数。
        ans_list (list)：答案列表。
        crowds_ans (list)：群体答案列表。
        score_list (list)：每个玩家的得分列表。
    """
    def __init__(self, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)

        # 读取游戏参数
        self.NUM_PLAYERS = config.getint('Game', 'NUM_PLAYERS')
        self.NUM_OPTIONS = config.getint('Game', 'NUM_OPTIONS')
        self.NUM_EPOCHS = config.getint('Game', 'NUM_EPOCHS')
        self.is_communicate = config.getboolean('Game', 'is_communicate')

        # 读取初始概率
        self.pList = list(map(float, config.get('InitialProbabilities', 'pList').split(',')))

        # 读取策略超参数
        self.LEARN_RATE_UP = config.getfloat('Strategy', 'LEARN_RATE_UP')
        self.LEARN_RATE_DOWN = config.getfloat('Strategy', 'LEARN_RATE_DOWN')
        self.WIS_VALUE = config.getfloat('Strategy', 'WIS_VALUE')
        self.SOLID_VALUE = config.getfloat('Strategy', 'SOLID_VALUE')

        self.show = 0
        self.avg_score = []

        self.iter = 0
        self.ans_list = [0] * self.NUM_OPTIONS
        self.crowds_ans = []
        self.score_list = [0] * self.NUM_PLAYERS

class Game:
    def __init__(self, config_file):
        """
        初始化游戏对象。

        参数：
        - config_file：配置文件路径

        属性：
        - NUM_PLAYERS：玩家数量
        - NUM_OPTIONS：选项数量
        - NUM_EPOCHS：游戏循环次数
        - is_communicate：是否允许玩家之间进行通信
        - player_types：玩家类型字典
        - pList：初始概率列表
        - LEARN_RATE_UP：策略学习率（增加）
        - LEARN_RATE_DOWN：策略学习率（减少）
        - WIS_VALUE：智慧值
        - SOLID_VALUE：团结值
        - pOption：每个选项随时间变化的概率列表
        - pOption0：选项0随时间变化的概率列表
        - pOption1：选项1随时间变化的概率列表
        - pOption2：选项2随时间变化的概率列表
        - pOption3：选项3随时间变化的概率列表
        - pOption4：选项4随时间变化的概率列表
        - show：游戏展示次数
        - avg_score：平均得分列表
        - params：策略参数对象
        """
        config = configparser.ConfigParser()
        config.read(config_file)

        # 读取游戏参数
        self.NUM_PLAYERS = config.getint('Game', 'NUM_PLAYERS')
        self.NUM_OPTIONS = config.getint('Game', 'NUM_OPTIONS')
        self.NUM_EPOCHS = config.getint('Game', 'NUM_EPOCHS')
        self.is_communicate = config.getboolean('Game', 'is_communicate')

        # 读取玩家类型
        self.player_types = {
            "radicals": config.getint('PlayerTypes', 'radicals'),
            "conservative": config.getint('PlayerTypes', 'conservative'),
            "neutral": config.getint('PlayerTypes', 'neutral'),
            "normal": config.getint('PlayerTypes', 'normal'),
            "learner": config.getint('PlayerTypes', 'learner'),
            "fun": config.getint('PlayerTypes', 'fun'),
            "villain": config.getint('PlayerTypes', 'villain')
        }

        # 读取初始概率
        self.pList = list(map(float, config.get('InitialProbabilities', 'pList').split(',')))

        # 读取策略超参数
        self.LEARN_RATE_UP = config.getfloat('Strategy', 'LEARN_RATE_UP')
        self.LEARN_RATE_DOWN = config.getfloat('Strategy', 'LEARN_RATE_DOWN')
        self.WIS_VALUE = config.getfloat('Strategy', 'WIS_VALUE')
        self.SOLID_VALUE = config.getfloat('Strategy', 'SOLID_VALUE')

        # 存储每个选项随时间变化的概率的列表
        self.pOption = []
        self.pOption0 = []
        self.pOption1 = []
        self.pOption2 = []
        self.pOption3 = []
        self.pOption4 = []

        # 计数
        self.show = 0
        self.avg_score = []

        # 参数
        self.params = StrategyParameters(config_file)

    def main(self):
            """
            游戏主循环。
            """
            while True:  # 游戏主循环
                for i in range(self.NUM_EPOCHS):  # 游戏循环次数
                    self.init_single_game()  # 初始化单个游戏的参数
                    for norm in range(self.NUM_PLAYERS):
                        self.normal_scheme["one"] = np.random.choice(self.NUM_OPTIONS, p=self.pList)  # 随机选择初始策略
                        ans = self.normal_scheme["one"]
                        self.ans_list[ans] += 1  # 更新每个选项选择的玩家数量
                        self.crowds_ans.append(ans)  # 添加玩家答案到列表中
                    self.OTraw(self.ans_list, self.score_list)  # 根据玩家答案计算每个玩家的得分
                    
                    if i % (self.NUM_EPOCHS // 100) == 0:
                        self.show += 1
                        # 记录每个选项的概率
                        self.pOption0.append(self.pList[0])
                        self.pOption1.append(self.pList[1])
                        self.pOption2.append(self.pList[2])
                        self.pOption3.append(self.pList[3])
                        self.pOption4.append(self.pList[4])
                        self.pOption = [self.pOption0, self.pOption1, self.pOption2, self.pOption3, self.pOption4]
                        self.avg_score.append(np.mean(self.score_list))  # 计算平均得分
                        print(i)

                    # 更新参数
                    self.params.pList = self.pList
                    self.params.iter = i
                    self.params.ans_list = self.ans_list
                    self.params.crowds_ans = self.crowds_ans
                    self.params.score_list = self.score_list
                    self.pList = normal.norm_scheme_adjust(self.params)  # 调整策略概率
                break
    
    def init_single_game(self):
        """
        初始化单个游戏的参数。
        """
        self.normal_scheme = {"one":None}  # 初始策略
        self.ans_list = [0] * self.NUM_OPTIONS  # 每个选项选择的玩家数量
        self.crowds_ans= []  # 玩家答案列表
        self.score_list = [0] * self.NUM_PLAYERS  # 玩家得分列表

    def OTraw(self, ans_list, score_list):
        """
        根据玩家答案计算每个玩家的得分。

        参数：
        - ans_list：每个选项选择的玩家数量列表
        - score_list：玩家得分列表
        """
        self.count_que1 = 0
        self.count_que2 = 0
        self.fairness_score = 0
        self.wisdom_score = 0
        self.bravery_score = 0

        for anst in ans_list:  # 判断是否满足“团结”和“智慧”的条件
            if ans_list[2] >= anst:
                self.count_que1 += 1
            if ans_list[3] <= anst:
                self.count_que2 += 1

        if self.count_que1 == len(ans_list):
            self.fairness_score = 2
        if self.count_que2 == len(ans_list):
            self.wisdom_score = 2
        if ans_list[4] == 1:
            self.bravery_score = 4

        count = 0
        for i in self.crowds_ans:
            if i == 0:                                      # 谨慎
                score_list[count] = 1
            elif i == 1:                                    # 公平
                if ans_list != 0:
                    score_list[count] = 3 / ans_list[1]
            elif i == 2:                                    # 团结
                score_list[count] = self.fairness_score
            elif i == 3:                                    # 智慧
                score_list[count] = self.wisdom_score
            elif i == 4:                                    # 勇气
                score_list[count] = self.bravery_score
            count += 1

    def graph(self):
        """
        绘制每个选项随时间变化的概率图。
        """
        X = np.linspace(1, self.show, self.show)
        plt.plot(X, self.pOption[0], label = "谨慎")
        plt.plot(X, self.pOption[1], label = "公平")
        plt.plot(X, self.pOption[2], label = "团结")
        plt.plot(X, self.pOption[3], label = "智慧")
        plt.plot(X, self.pOption[4], label = "勇气")
        plt.ylabel("概率")
        plt.legend(loc="upper right")
        plt.show()



if __name__ == "__main__":
    game = Game('normal.ini')
    game.main()

    print("得分", game.score_list)
    print("选项", game.ans_list)
    print("答案", game.crowds_ans)
    print("概率", game.pList)
    print("均分", np.mean(game.avg_score))
    print(" ")
    #print("没有人选择“勇气”的比例", round(game.count_brave/game.NUM_EPOCHS*100, 2), "%")
    game.graph()