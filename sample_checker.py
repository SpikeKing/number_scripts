#!/usr/bin/env python
# -- coding: utf-8 --
"""
Copyright (c) 2021. All rights reserved.
Created by C. L. Wang on 20.8.21
"""

import os
import sys

from myutils.project_utils import read_file, write_line
from root_dir import DATA_DIR


class SampleChecker(object):
    def __init__(self):
        self.file1_path = os.path.join(DATA_DIR, "numbers_files", "clean_hw_numbers_v4_ori.txt")
        self.file2_path = os.path.join(DATA_DIR, "numbers_files", "clean_hw_numbers_v4_test.txt")
        self.out_file_path = os.path.join(DATA_DIR, "numbers_files", "hw_numbers_symbol_check.txt")

    def process(self):
        data1_lines = read_file(self.file1_path)
        data2_lines = read_file(self.file2_path)
        data_lines = data1_lines + data2_lines
        for data_line in data_lines:
            url, label = data_line.split("\t")
            if label == ">" or label == "<" or label == "7" or label == "=":
                write_line(self.out_file_path, data_line)


def main():
    sc = SampleChecker()
    sc.process()


if __name__ == '__main__':
    main()
