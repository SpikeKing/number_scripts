#!/usr/bin/env python
# -- coding: utf-8 --
"""
Copyright (c) 2021. All rights reserved.
Created by C. L. Wang on 13.8.21
"""

import collections
import copy
import os
import re
from fractions import Fraction

from myutils.project_utils import read_excel_file, write_list_to_excel, create_file
from root_dir import DATA_DIR


class NumbersCalculator(object):
    def __init__(self):
        self.xlsx_path = os.path.join(DATA_DIR, '口算分数计算2-20210813.xlsx')
        self.out_xlsx_path = os.path.join(DATA_DIR, '口算分数计算2-20210813.out.xlsx')
        create_file(self.out_xlsx_path)

    @staticmethod
    def repalce_one_by_one(data_str, r_list, func_x):
        """
        逐个替换
        """
        def replace_nth(s, sub, repl, n):
            """
            替换第n个
            """
            find = s.find(sub)
            # If find is not -1 we have found at least one match for the substring
            i = find != -1
            # loop util we find the nth or we find no match
            while find != -1 and i != n:
                # find + 1 means we start searching from after the last match
                find = s.find(sub, find + 1)
                i += 1
            # If i is equal to n we found nth match so replace
            if i == n:
                return s[:find] + repl + s[find + len(sub):]
            return s

        def find_nth(haystack, needle, n):
            """
            找到第n个
            """
            start = haystack.find(needle)
            while start >= 0 and n > 1:
                start = haystack.find(needle, start + len(needle))
                n -= 1
            return start

        res_s = copy.copy(data_str)
        b_list = len(data_str) * [True]  # 判断是否已经处理
        time_dict = collections.defaultdict(int)  # 出现次数
        for sub_str in r_list:
            while True:
                n_time = time_dict[sub_str]  # 出现第几次
                x = find_nth(data_str, sub_str, n_time + 1)
                if x == -1:
                    break
                if b_list[x]:
                    b_list[x:x+len(sub_str)] = [False]*len(sub_str)
                    n_time = time_dict[sub_str] + 1
                    # 自定义replace
                    res_s = replace_nth(res_s, sub_str, func_x(sub_str), n_time)
                    break
                else:
                    time_dict[sub_str] += 1
        return res_s

    @staticmethod
    def process_data(data):
        """
        计算等式
        """
        # 第1部分，拆分等号
        question = data.replace(' ', '').replace('（', '(').replace('）', ')')
        question = question.replace('×', '*').replace('÷', '/')

        left = question.strip().split('=')[0]
        right = question.strip().split('=')[-1]
        print('[Info] left: {}, right: {}'.format(left, right))

        # 第2部分，替换分数
        pattern = re.compile(r'[0-9]+/[0-9]+')
        frac_list = pattern.findall(left)
        frac_list = sorted(list(frac_list), key=len, reverse=True)
        print('[Info] frac_list: {}'.format(frac_list))

        def func1_x(s_str):
            return 'Fraction(\'{}\')'.format(s_str)

        left = NumbersCalculator.repalce_one_by_one(left, frac_list, func1_x)

        # 第3部分，替换小数
        pattern2 = re.compile(r'[0-9]+\.[0-9]+')
        frac2_list = pattern2.findall(left)
        frac2_list = sorted(list(frac2_list), key=len, reverse=True)
        print('[Info] frac2_list: {}'.format(frac2_list))

        def func2_x(s_str):
            return 'Fraction(\'{}\')'.format(Fraction(s_str))

        left = NumbersCalculator.repalce_one_by_one(left, frac2_list, func2_x)

        print('[Info] left: {}'.format(left))

        x_dict = {"Fraction": Fraction}
        res = eval(left, x_dict)
        print("[Info] res: {}".format(res))
        print('-' * 100)
        return res

    def process(self):
        print("[Info] 处理文件: {}".format(self.xlsx_path))
        data_lines = read_excel_file(self.xlsx_path)
        print("[Info] 样本数: {}".format(len(data_lines)))
        title_list = ["转换后题干", "结果"]
        res_list = []
        for data_idx, data_line in enumerate(data_lines):
            if data_idx == 0:
                continue
            data = data_line[0]
            print('[Info] data_idx: {}, data: {}'.format(data_idx, data))
            res = NumbersCalculator.process_data(data)
            res_list.append([data, str(res)])
        write_list_to_excel(self.out_xlsx_path, title_list, res_list)
        print("[Info] 处理完成: {}".format(self.out_xlsx_path))

    def test(self):
        data = "2/4+2/4=?"  # 测试
        self.process_data(data)


def main():
    nc = NumbersCalculator()
    # nc.test()
    nc.process()


if __name__ == '__main__':
    main()
