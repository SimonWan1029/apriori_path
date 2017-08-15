# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 10:05:42 2016

@author: Administrator
"""
from numpy import *  # 扩展，用于存储和处理大型矩阵
import itertools  # 模块，可进行循环操作
import pandas as pd  # 基于数组和数据框数据分析

support_dic = {}  # 数据字典,字典是由键对值组组成


# 生成原始数据，用于测试


def loadDataSet():  # 读取数据源
    data = pd.read_csv('/Users/SimonWan/Develop/Fangdd/Script/path001.csv', usecols=['type', 'city_id', 'page_list'])
    dt_sh = data.loc[(data['type'] == 'no') & (data['city_id'] == 121), ['page_list']]  # loc,索引字符串索引,选取行，列的数据
    sh_list = []  # 列表数据类型，一种可变的序列
    for i in range(0, len(dt_sh) - 1):
        a = dt_sh.iloc[i, 0]  # iloc,索整型索引，取i行的数据
        a = str(a)
        a1 = a.split(';')
        a2 = [x for x in a1]
        sh_list.append(list(a2))

    return sh_list


# 获取整个数据库中的一阶元素
# C1 = {1, 2, 3, 4, 5}


def createC1(dataSet):
    C1 = set([])
    for item in dataSet:
        C1 = C1.union(set(item))
    return [frozenset([i]) for i in C1]


# 输入数据库（dataset） 和 由第K-1层数据融合后得到的第K层数据集（Ck），
# 用最小支持度（minSupport)对 Ck 过滤，得到第k层剩下的数据集合（Lk）


def getLk(dataset, Ck, minSupport):
    global support_dic
    Lk = {}
    # 计算Ck中每个元素在数据库中出现次数
    for item in dataset:
        for Ci in Ck:
            if Ci.issubset(item):
                if not Ci in Lk:
                    Lk[Ci] = 1
                else:
                    Lk[Ci] += 1
    # 用最小支持度过滤
    Lk_return = []
    for Li in Lk:
        support_Li = Lk[Li] / float(len(dataSet))
        if support_Li >= minSupport:
            Lk_return.append(Li)
            support_dic[Li] = support_Li
    return Lk_return


# 将经过支持度过滤后的第K层数据集合（Lk）融合
# 得到第k+1层原始数据Ck1
'''连接步'''


def genLk1(Lk):
    Ck1 = []
    for i in range(len(Lk) - 1):
        for j in range(i + 1, len(Lk)):
            if sorted(list(Lk[i]))[0:-1] == sorted(list(Lk[j]))[0:-1]:
                Ck1.append(Lk[i] | Lk[j])
    return Ck1


# 遍历所有二阶及以上的频繁项集合


def genItem(freqSet, support_dic):
    for i in range(1, len(freqSet)):
        for freItem in freqSet[i]:
            genRule(freItem)


# 输入一个频繁项，根据“置信度”生成规则
# 采用了递归，对规则树进行剪枝

# minConf 最小置信度
def genRule(Item, minConf=0.5):
    global result_df
    if len(Item) >= 2:
        for element in itertools.combinations(list(Item), 1):
            print(element)
            print(Item - frozenset(element))
            if support_dic[Item] / float(support_dic[Item - frozenset(element)]) >= minConf:
                # print(str([Item - frozenset(element)]) +
                #      "----->" + str(element))
                # print(support_dic[Item] /
                #      float(support_dic[Item - frozenset(element)]))
                Itemtypes = str([Item - frozenset(element)]) + "----->" + str(element)
                Confidence = support_dic[Item] / float(support_dic[Item - frozenset(element)])
                result_df = result_df.append([{'Itemtypes': Itemtypes, 'Confidence': Confidence}])
                genRule(Item - frozenset(element))


# 输出结果
if __name__ == '__main__':
    dataSet = loadDataSet()
    result_list = []
    Ck = createC1(dataSet)
    # 循环生成频繁项集合，直至产生空集
    while True:
        Lk = getLk(dataSet, Ck, 0.6)  # 最小支持度
        if not Lk:
            break
        result_list.append(Lk)
        Ck = genLk1(Lk)
        if not Ck:
            break
    # 输出频繁项及其“支持度”
    print(result_list)
    support_dic = pd.Series(support_dic)
    # support_dic.to_csv('E:\\my_file\\py\\support1.csv')
    support_dic.to_csv('/Users/SimonWan/Develop/Fangdd/Script/support1.csv', encoding="utf_8_sig")
    # 输出规则置信度
    result_df = pd.DataFrame(columns=['Itemtypes', 'Confidence'])
    genItem(result_list, support_dic)
    result_df.to_csv('/Users/SimonWan/Develop/Fangdd/Script/confidence1.csv', index=None, encoding="utf_8_sig")