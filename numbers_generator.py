#!/usr/bin/env python
# -- coding: utf-8 --
"""
Copyright (c) 2021. All rights reserved.
Created by C. L. Wang on 12.8.21
"""

from myutils.project_utils import *


class NumbersGenerator(object):
    def __init__(self):
        pass

    def generate_type1(self):
        n1 = random.randint(1, 1000)
        n2 = random.randint(3, 5)
        num = int("".join([str(n1)] + n2 * [str(0)]))
        return num

    def generate_type2(self):
        if random_prob(0.5):
            num = random.randint(1000000, 100000000)
        else:
            n1 = random.randint(10, 1000)
            n2 = random.randint(10000, 1000000)
            num = float(str(n1) + "." + str(n2))
        return num

    def generate_type3(self):
        digits_list = [[6, 9, 0], [4, 9], [1, 9, 7], [1, 3, 0]]
        n1 = random.randint(4, 6)
        digits = random_pick(digits_list)
        tmp_str = ""
        for _ in range(n1):
            tmp_str += str(random_pick(digits))
        num = int(tmp_str)
        return num

    def process(self):
        for i in range(100):
            num = self.generate_type3()
            print(num)


def main():
    ng = NumbersGenerator()
    ng.process()


if __name__ == "__main__":
    main()
