# -*- coding: UTF-8 -*-
# Game.py
# Python 3.8.10
# @Time: 2023/12/11
# @Author: Friman

print("加载游戏模块...")
import numpy as np
import math
np.random.seed(3407)
import tqdm
import matplotlib.pyplot as plt
import configparser
import os
import warnings
#warnings.filterwarnings("ignore")
plt.rcParams['font.sans-serif']=['SimHei']

'''
10人进行博弈，你作为其中之一，尽力取得高分
A. 谨慎（+1）
B. 公正（与选此选项的玩家平分3分）
C. 团结（选此选项的玩家最多时，每人+2分）
D. 智慧（人数最少时，每人+2分）
E. 勇气（若仅有你一人选择此项，+4分）
'''

from strategies import normal
from _p5af37c import wtf

class Parameters:
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
        try:
            config.read(config_file)
        except Exception as e:
            raise Exception(f"找不到游戏配置文件: {e}")
        
        wtf(config_file)

        # 读取游戏参数
        self.NUM_PLAYERS = self._get_and_validate(config, 'Game', 'NUM_PLAYERS', int, lambda x: x == 10)
        self.NUM_OPTIONS = self._get_and_validate(config, 'Game', 'NUM_OPTIONS', int, lambda x: x == 5)
        self.NUM_EPOCHS = self._get_and_validate(config, 'Game', 'NUM_EPOCHS', int, lambda x: 0 < x < 100000)
        self.is_communicate = self._get_and_validate(config, 'Game', 'is_communicate', bool)

        self.iter = 0
        self.ans_list = [0] * self.NUM_OPTIONS
        self.crowds_ans = []
        self.score_list = [0] * self.NUM_PLAYERS

        # 读取题目和策略参数
        for folder_name in os.listdir('questions'): # 遍历questions文件夹下的所有文件夹
            q_folder_path = os.path.join('questions', folder_name)
            s_folder_path = os.path.join('strategies', folder_name)
            if os.path.isdir(q_folder_path):
                # 读取default.ini文件
                q_config_file = os.path.join(q_folder_path, 'default.ini')
                s_config_file = os.path.join(s_folder_path, 'default.ini')
                q_config = configparser.ConfigParser()
                s_config = configparser.ConfigParser()
                try:
                    q_config.read(q_config_file)
                except Exception as e:
                    raise Exception(f"第{folder_name[1:]}题的题目配置文件{q_config_file}不存在！:{e}")
                try:
                    s_config.read(s_config_file)
                except Exception as e:
                    raise Exception(f"第{folder_name[1:]}题的策略配置文件{s_config_file}不存在！:{e}")

                if folder_name[1:] == '1':
                    # 读取得分参数
                    self.cautious_score = self._get_and_validate(q_config, 'Q1', 'cautious_score', int)
                    self.fairness_score = self._get_and_validate(q_config, 'Q1', 'fairness_score', int)
                    self.solidarity_score = self._get_and_validate(q_config, 'Q1', 'solidarity_score', int)
                    self.wisdom_score = self._get_and_validate(q_config, 'Q1', 'wisdom_score', int)
                    self.bravery_score = self._get_and_validate(q_config, 'Q1', 'bravery_score', int)

                    # 读取初始概率
                    self.pList = self._get_and_validate(s_config, 'InitialProbabilities', 'pList', 
                                                        lambda x: list(map(float, x.split(','))), 
                                                        lambda x: len(x) == self.NUM_OPTIONS and math.isclose(sum(x), 1, rel_tol=1e-5))

                    # 读取策略超参数
                    self.LEARN_RATE_UP = self._get_and_validate(s_config, 'Strategy', 'LEARN_RATE_UP', float, lambda x: x > 1)
                    self.LEARN_RATE_DOWN = self._get_and_validate(s_config, 'Strategy', 'LEARN_RATE_DOWN', float, lambda x: x > 1)
                    self.WIS_VALUE = self._get_and_validate(s_config, 'Strategy', 'WIS_VALUE', float, lambda x: x > 0)
                    self.SOLID_VALUE = self._get_and_validate(s_config, 'Strategy', 'SOLID_VALUE', float, lambda x: x > 0)
                # elif folder_name[1:] == '2':
                #     pass
                # elif folder_name[1:] == '3':
                #     pass
                # else:
                #     pass

    def _get_and_validate(self, config, section, option, type_func, validation_func=None):
        try:
            value = type_func(config.get(section, option))
        except Exception as e:
            raise Exception(f"无法解析 {section} 中的 {option}: {e}")

        if validation_func and not validation_func(value):
            if option == 'NUM_PLAYERS':
                raise ValueError(f"咱们还是先考虑10人局吧，以后会扩展的QAQ")
            
            elif option == 'NUM_OPTIONS':
                if value > 5:
                    raise ValueError(f"你怎么知道第一题其实不止五个选项的，以后再加吧QAQ")
                if 0 <= value < 5:
                    raise ValueError(f"我好心写了五个选项，你怎么可以不用QAQ")
                if value < 0:
                    raise ValueError(f"负数选项？？？你认真的吗QAQ")
                
            elif option == 'NUM_EPOCHS':
                time = round(SCORE * value)
                if value < 0:
                    raise ValueError(f"循环负数次？？你很有做测试工程师的潜力QAQ")
                if 10 < time < 3600:
                    warnings.warn(f"你想让我循环这么多次吗, 预计需要 {time} 秒QAQ")
                    if input("确定要进行游戏吗？按回车键继续...") == 'q':
                        print("再见~")
                        exit()
                        #raise ValueError(f"你取消了游戏QAQ")
                if time >= 3600:
                    raise ValueError(f"模拟时间预计超过一个小时，还是让电脑歇歇吧QAQ")
                
            elif option == 'cautious_score':
                raise ValueError(f"不要再输入奇怪的值啦，{section} 中 {option} 的值 {value} 是无效的QAQ")
            elif option == 'fairness_score':
                raise ValueError(f"不要再输入奇怪的值啦，{section} 中 {option} 的值 {value} 是无效的QAQ")
            elif option == 'solidarity_score':
                raise ValueError(f"不要再输入奇怪的值啦，{section} 中 {option} 的值 {value} 是无效的QAQ")
            elif option == 'wisdom_score':
                raise ValueError(f"不要再输入奇怪的值啦，{section} 中 {option} 的值 {value} 是无效的QAQ")
            elif option == 'bravery_score':
                raise ValueError(f"不要再输入奇怪的值啦，{section} 中 {option} 的值 {value} 是无效的QAQ")
            elif option == 'pList':
                if len(value) != self.NUM_OPTIONS:
                    raise ValueError(f"初始概率列表 {value} 的长度不是 {self.NUM_OPTIONS}")
                if not math.isclose(sum(value), 1, rel_tol=1e-5):
                    raise ValueError(f"初始概率列表 {value} 的和不是1")
                
            elif option == 'LEARN_RATE_UP':
                raise ValueError(f"不要再输入奇怪的值啦，{section} 中 {option} 的值 {value} 是无效的QAQ")
            elif option == 'LEARN_RATE_DOWN':
                raise ValueError(f"不要再输入奇怪的值啦，{section} 中 {option} 的值 {value} 是无效的QAQ")
            elif option == 'WIS_VALUE':
                raise ValueError(f"不要再输入奇怪的值啦，{section} 中 {option} 的值 {value} 是无效的QAQ")
            elif option == 'SOLID_VALUE':
                raise ValueError(f"不要再输入奇怪的值啦，{section} 中 {option} 的值 {value} 是无效的QAQ")
            
            else:
                raise ValueError(f"不要再输入奇怪的值啦，{section} 中 {option} 的值 {value} 是无效的QAQ")

        return value
    
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
        - cautious_score：“谨慎”选项得分
        - fairness_score：“公平”选项所平分的分值
        - solidarity_score：“团结”选项可能的得分
        - wisdom_score：“智慧”选项可能的得分
        - bravery_score：“勇气”选项可能的得分
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

        # 加载参数
        self.params = Parameters(config_file)

    def main(self):
            """
            游戏主循环。
            """
            while True:  # 游戏主循环
                for i in tqdm.trange(self.params.NUM_EPOCHS):  # 游戏循环次数
                    self.init_single_game()  # 初始化单个游戏的参数
                    for norm in range(self.params.NUM_PLAYERS):
                        self.normal_scheme["one"] = np.random.choice(self.params.NUM_OPTIONS, p=self.params.pList)  # 随机选择初始策略
                        ans = self.normal_scheme["one"]
                        self.params.ans_list[ans] += 1  # 更新每个选项选择的玩家数量
                        self.params.crowds_ans.append(ans)  # 添加玩家答案到列表中
                    self.calc_scores(self.params.ans_list, self.params.score_list)  # 根据玩家答案计算每个玩家的得分
                    
                    if self.params.NUM_EPOCHS <= 100:
                        point_record = i
                    else:
                        point_record = self.params.NUM_EPOCHS // 100
                    if (i+1) % (point_record+1) == 0:
                        self.show += 1
                        # 记录每个选项的概率
                        self.pOption0.append(self.params.pList[0])
                        self.pOption1.append(self.params.pList[1])
                        self.pOption2.append(self.params.pList[2])
                        self.pOption3.append(self.params.pList[3])
                        self.pOption4.append(self.params.pList[4])
                        self.pOption = [self.pOption0, self.pOption1, self.pOption2, self.pOption3, self.pOption4]
                        self.avg_score.append(np.mean(self.params.score_list))  # 计算平均得分
                        #print(i)

                    # 更新参数
                    self.params.iter = i
                    self.params.pList = normal.norm_scheme_adjust(self.params, 1)  # 调整策略概率
                break
    
    def init_single_game(self):
        """
        初始化单个游戏的参数。
        """
        self.normal_scheme = {"one":None}  # 初始策略
        self.params.ans_list = [0] * self.params.NUM_OPTIONS  # 每个选项选择的玩家数量
        self.params.crowds_ans= []  # 玩家答案列表
        self.params.score_list = [0] * self.params.NUM_PLAYERS  # 玩家得分列表
        [i / sum(self.params.pList) for i in self.params.pList] # 归一化概率


    def calc_scores(self, ans_list, score_list):
        """
        根据玩家答案计算每个玩家的得分。

        参数：
        - ans_list：每个选项选择的玩家数量列表
        - score_list：玩家得分列表
        """
        count_que1 = ans_list[2] >= max(ans_list)
        count_que2 = ans_list[3] <= min(ans_list)

        # 计算本轮游戏应得分数
        self.cautious_score = self.params.cautious_score
        self.fairness_score = self.params.fairness_score / ans_list[1] if ans_list[1] != 0 else 0
        self.solidarity_score = 0 if not count_que1 else self.params.solidarity_score
        self.wisdom_score = 0 if not count_que2 else self.params.wisdom_score
        self.bravery_score = 0 if ans_list[4] != 1 else self.params.bravery_score

        # 计算每个玩家的得分
        for i, ans in enumerate(self.params.crowds_ans):
            if ans == 0:  # 谨慎
                score_list[i] = self.cautious_score
            elif ans == 1:  # 公平
                score_list[i] = self.fairness_score
            elif ans == 2:  # 团结
                score_list[i] = self.solidarity_score
            elif ans == 3:  # 智慧
                score_list[i] = self.wisdom_score
            elif ans == 4:  # 勇气
                score_list[i] = self.bravery_score

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

def benchmark_brief(iter):
    """
    用于性能跑分
    """
    import time
    test_array = np.random.randint(0, 100000, iter*2000)
    start = time.time()
    test_array.sort()
    end = time.time()
    # print((end-start))
    return (end-start)/iter

def benchmark_brief_debug():
    """
    用于开发者测试性能。
    """
    SCORE = benchmark_brief(iter=5000)
    game_time = []
    test_time = []
    # 随机生成一个长度为100000的列表，列表中的每个元素都是0到100000之间的随机整数，确定随机种子
    import time

    game = Game('normal.ini')
    for i in tqdm.trange(2000, 2010):
        start = time.time()
        game.params.NUM_EPOCHS = i
        game.main()
        end = time.time()
        game_time.append(end-start)

    for i in tqdm.trange(2000, 2010):
        start = time.time()
        test_array = np.random.randint(0, 100000, i*2000)
        test_array.sort()
        end = time.time()
        test_time.append(end-start)

    #计算game_time，test_time相关系数
    print(np.corrcoef(game_time, test_time))

    plt.plot(game_time, label = "游戏")
    plt.plot(test_time, label = "测试")
    plt.ylabel("时间")
    plt.legend(loc="upper right")
    plt.show()


if __name__ == "__main__":
    is_benchmark_debug = False
    if not is_benchmark_debug:
        print("测试性能")
        SCORE = benchmark_brief(iter=5000)
        print("加载游戏配置")
        game = Game('normal.ini')
        #benchmark(game.params.NUM_EPOCHS)
        print("进行游戏模拟...")
        game.main()

        print("得分", game.params.score_list)
        print("选项", game.params.ans_list)
        print("答案", game.params.crowds_ans)
        print("概率", game.params.pList)
        print(f"均分{np.mean(game.avg_score):.4f}")
        print(" ")
        #print("没有人选择“勇气”的比例", round(game.count_brave/game.NUM_EPOCHS*100, 2), "%")
        game.graph()
    else:
        benchmark_brief_debug()