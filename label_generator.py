#!/usr/bin/env python
# -- coding: utf-8 --
"""
Copyright (c) 2021. All rights reserved.
Created by C. L. Wang on 30.7.21
"""

import pandas

from myutils.make_html_page import make_html_page
from myutils.project_utils import *
from root_dir import DATA_DIR


class LabelGenerator(object):
    def __init__(self):
        self.file_name = os.path.join(DATA_DIR, "8ad26809-6a2c-48d6-83d3-7133ad7d236f_166331.csv")

    def process(self):
        data = pandas.read_csv(self.file_name)
        out_list = []
        for idx, row in data.iterrows():
            data = json.loads(row["问题内容"])
            url = data[0]
            label = data[1]
            out_list.append([label, url])
        make_html_page("label.html", img_data_list=out_list)


def main():
    lg = LabelGenerator()
    lg.process()


if __name__ == '__main__':
    main()
