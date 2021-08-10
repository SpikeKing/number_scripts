#!/usr/bin/env python
# -- coding: utf-8 --
"""
Copyright (c) 2021. All rights reserved.
Created by C. L. Wang on 3.8.21
"""

from myutils.make_html_page import make_html_page
from myutils.project_utils import *
from root_dir import DATA_DIR


class ResultsChecker(object):
    def __init__(self):
        # file_name = "a2e455ff-b77b-4f65-ae59-864cfa20bdd8_166274.out-20210803112232.vs-20210803181749.txt"
        file_name = "relabeled.out-20210809094605.txt"
        self.file_name = os.path.join(DATA_DIR, "numbers_files", file_name)
        self.out_file = os.path.join(DATA_DIR, "vs-{}.html".format(get_current_time_str()))

    def process(self):
        data_lines = read_file(self.file_name)
        print('[Info] 样本数: {}'.format(len(data_lines)))
        out_lines = []
        for data_line in data_lines:
            items = data_line.split("\t")
            out_lines.append(items)
        make_html_page(self.out_file, out_lines)
        print('[Info] 输出: {}'.format(self.out_file))


def main():
    rc = ResultsChecker()
    rc.process()


if __name__ == '__main__':
    main()
