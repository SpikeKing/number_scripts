#!/usr/bin/env python
# -- coding: utf-8 --
"""
Copyright (c) 2021. All rights reserved.
Created by C. L. Wang on 23.8.21
"""
import collections
import os

import cv2

from myutils.make_html_page import make_html_page
from myutils.project_utils import *
from root_dir import DATA_DIR
from x_utils.vpf_sevices import get_hw_numbers_service


class SymbolGenerator(object):
    def __init__(self):
        # self.folder_dir = os.path.join(DATA_DIR, "0823_lexie")
        # self.out_file = os.path.join(DATA_DIR, "out-{}.txt".format(get_current_time_str()))
        self.file_name = os.path.join(DATA_DIR, "out-urls.txt")

        self.out_dir = os.path.join(DATA_DIR, "out-urls")
        self.out_file_name = os.path.join(DATA_DIR, "out-urls-x.txt")
        self.html_file_name = os.path.join(DATA_DIR, "out-urls-x.html")
        mkdir_if_not_exist(self.out_dir)

    @staticmethod
    def predict_v1_1(img_url):
        res_dict = get_hw_numbers_service(img_url, service_name="uKEda8PCd5m2daQmPCe8tC")
        ocr_text = res_dict['data']['ocr_text']
        return ocr_text

    @staticmethod
    def save_img_path(img_bgr, img_name, oss_root_dir=""):
        """
        上传图像
        """
        from x_utils.oss_utils import save_img_2_oss
        if not oss_root_dir:
            oss_root_dir = "zhengsheng.wcl/Character-Detection/datasets/hw-numbers-imgs-v5/"
        img_url = save_img_2_oss(img_bgr, img_name, oss_root_dir)
        return img_url

    @staticmethod
    def process_line(data_type, path_list):
        label_list = []
        for idx, path in enumerate(path_list):
            img_bgr = cv2.imread(path[idx])
            file_name = "{}_{}.jpg".format(data_type, idx)
            img_url = SymbolGenerator.save_img_path(img_bgr, file_name)
            label = SymbolGenerator.predict_v1_1(img_url)

    def process(self):
        paths_list, names_list = traverse_dir_files(self.out_dir)

        data_dict = collections.defaultdict(list)
        for path in paths_list:
            data_lines = read_file(path)
            for data_line in data_lines:
                url, label = data_line.split("\t")
                data_dict[label].append(url)

        out_list = []
        for key in data_dict.keys():
            urls = data_dict[key]
            for url in urls:
                out_list.append("{}\t{}".format(url, key))

        write_list_to_file(self.out_file_name, out_list)

    def draw_list(self):
        data_lines = read_file(self.out_file_name)
        out_list = []
        for data_line in data_lines:
            url, label = data_line.split("\t")
            out_list.append([label, url])
        make_html_page(self.html_file_name, out_list)





def main():
    sg = SymbolGenerator()
    sg.draw_list()


if __name__ == '__main__':
    main()
