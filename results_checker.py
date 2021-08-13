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
        file_name = "relabeled.out-20210812120943"
        # self.file_name = os.path.join(DATA_DIR, "numbers_files", file_name)
        self.file_name = os.path.join(DATA_DIR, file_name + ".txt")
        self.out_file = os.path.join(DATA_DIR, "vs-{}.html".format(get_current_time_str()))

    def process(self):
        data_lines = read_file(self.file_name)
        random.shuffle(data_lines)
        data_lines = data_lines[:500]
        print('[Info] 样本数: {}'.format(len(data_lines)))
        out_lines = []
        for img_idx, data_line in enumerate(data_lines):
            items = data_line.split("\t")
            out_lines.append(items)
        make_html_page(self.out_file, out_lines)
        print('[Info] 输出: {}'.format(self.out_file))


def main():
    rc = ResultsChecker()
    rc.process()


if __name__ == '__main__':
    main()
