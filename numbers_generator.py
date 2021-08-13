#!/usr/bin/env python
# -- coding: utf-8 --
"""
Copyright (c) 2021. All rights reserved.
Created by C. L. Wang on 12.8.21
"""

from myutils.project_utils import *
from root_dir import DATA_DIR


class NumbersGenerator(object):
    def __init__(self):
        self.folder_path = os.path.join(DATA_DIR, "pre_labeled")
        mkdir_if_not_exist(self.folder_path)
        self.file_path = os.path.join(self.folder_path, "pre_labeled_{}.txt")

    def generate_nums(self, n):
        s = ""
        for _ in range(n):
            d = random.randint(1, 10)
            s += str(d)
        return s

    def generate_type1(self):
        n1 = random.randint(2, 3)
        n2 = random.randint(2, 4)
        num = int("".join([str(self.generate_nums(n1))] + n2 * [str(0)]))
        return num

    def generate_type2(self):
        if random_prob(0.5):
            n1 = random.randint(5, 7)
            num = self.generate_nums(n1)
        else:
            n1 = random.randint(2, 3)
            n2 = random.randint(3, 5)
            num = float(str(self.generate_nums(n1)) + "." + str(self.generate_nums(n2)))
        return num

    def generate_type3(self):
        digits_list = [[6, 9, 0], [4, 9], [1, 9, 7], [1, 3, 0], [2, 5, 8]]
        n1 = random.randint(4, 6)
        digits = random_pick(digits_list)
        tmp_str = ""
        for _ in range(n1):
            tmp_str += str(random_pick(digits))
        num = int(tmp_str)
        return num

    def generate_type4(self):
        n1 = random.randint(2, 4)
        n2 = random.randint(2, 5)
        num = str(self.generate_nums(n1)+"\\"+self.generate_nums(n2))
        return num

    def process(self):
        num_list = []
        for i in range(7000):
            num = self.generate_type1()
            num_list.append(num)
        for i in range(7000):
            num = self.generate_type2()
            num_list.append(num)
        for i in range(6000):
            num = self.generate_type3()
            num_list.append(num)
        for i in range(2560):
            num = self.generate_type4()
            num_list.append(num)
        random.shuffle(num_list)
        for idx, i in enumerate(range(0, 22560, 188)):
            write_list_to_file(self.file_path.format(idx), num_list[i:i+188])


def main():
    ng = NumbersGenerator()
    ng.process()


if __name__ == "__main__":
    main()
