#!/usr/bin/env python
# -- coding: utf-8 --
"""
Copyright (c) 2021. All rights reserved.
Created by C. L. Wang on 6.8.21
"""

from multiprocessing.pool import Pool

from myutils.project_utils import *
from root_dir import DATA_DIR
from x_utils.vpf_sevices import get_hw_numbers_service


class DatasetOperation(object):
    """
    清洗数据集
    """
    def __init__(self):
        self.file_path = os.path.join(DATA_DIR, 'numbers_files', 'clean_hw_numbers_v2_train.txt')
        time_str = get_current_time_str()
        self.out_file_path = os.path.join(DATA_DIR, 'numbers_files', 'relabeled.out-{}.txt'.format(time_str))

    @staticmethod
    def predict_danjing(img_url):
        res_dict = get_hw_numbers_service(img_url, service_name="9jWztNxT4jqq35TjGDAXZk")
        ocr_text = res_dict['data']['ocr_text']
        return ocr_text

    @staticmethod
    def predict_v1(img_url):
        res_dict = get_hw_numbers_service(img_url, service_name="z3GuvWo8AWMS9cde46ky2K")
        ocr_text = res_dict['data']['ocr_text']
        return ocr_text

    @staticmethod
    def predict_v1_1(img_url):
        res_dict = get_hw_numbers_service(img_url, service_name="uKEda8PCd5m2daQmPCe8tC")
        ocr_text = res_dict['data']['ocr_text']
        return ocr_text

    @staticmethod
    def check_label(img_url, img_label):
        pre_label = DatasetOperation.predict_v1(img_url)
        pre_label = str(pre_label)
        len_pre_label = len(pre_label)
        len_img_label = len(img_label)
        res_label = img_label
        other = pre_label.replace(".", "") == img_label or pre_label == img_label + "0"
        if abs(len_pre_label - len_img_label) == 1 and other:
            res_label = pre_label if len_pre_label > len_img_label else img_label
        return res_label

    @staticmethod
    def process_line(img_idx, img_url, img_label, out1_file_path):
        # try:
        res1_label = DatasetOperation.predict_danjing(img_url)
        res2_label = DatasetOperation.predict_v1(img_url)
        if res1_label != img_label or res2_label != img_label:
            print('[Info] img_idx: {}, img_label: {}, res1_label: {}, res2_label: {}, img_url: {}'
                  .format(img_idx, img_label, res1_label, res2_label, img_url))
            write_line(out1_file_path, "{}\t{}\t{}\t{}".format(img_url, img_label, res1_label, res2_label))
        if img_idx % 100 == 0:
            print('[Info] img_idx: {}'.format(img_idx))

    def process(self):
        print('[Info] 文本名称: {}'.format(self.file_path))
        data_lines = read_file(self.file_path)
        print('[Info] 样本数: {}'.format(len(data_lines)))
        pool = Pool(processes=40)
        for img_idx, data_line in enumerate(data_lines):
            items = data_line.split("\t")
            img_url, img_label = items
            # DatasetOperation.process_line(img_idx, img_url, img_label, self.out1_file_path)
            pool.apply_async(DatasetOperation.process_line, (img_idx, img_url, img_label, self.out_file_path))
        pool.close()
        pool.join()
        print('[Info] 处理完成: {}'.format(self.out_file_path))


def main():
    do = DatasetOperation()
    do.process()


if __name__ == '__main__':
    main()
