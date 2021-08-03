#!/usr/bin/env python
# -- coding: utf-8 --
"""
Copyright (c) 2021. All rights reserved.
Created by C. L. Wang on 3.8.21
"""
from multiprocessing.pool import Pool

from myutils.project_utils import *
from root_dir import DATA_DIR
from x_utils.vpf_sevices import get_hw_numbers_service


class ServicesVersus(object):
    """
    对比模型
    """
    def __init__(self):
        self.file_name = os.path.join(DATA_DIR, 'numbers_files',
                                      'a2e455ff-b77b-4f65-ae59-864cfa20bdd8_166274.out-20210803112232.txt')
        self.out_file = os.path.join(DATA_DIR, 
                                     'a2e455ff-b77b-4f65-ae59-864cfa20bdd8_166274.out-20210803112232.vs-{}.txt'.format(get_current_time_str()))

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
    def process_line(data_idx, img_url, out_file):
        res1 = ServicesVersus.predict_danjing(img_url)
        res2 = ServicesVersus.predict_v1(img_url)
        if res1 != res2:
            print('[Info] res1: {}, res2: {}, img_url: {}'.format(res1, res2, img_url))
            write_line(out_file, ",".join([res1, res2, img_url]))
        if data_idx % 100 == 0:
            print('[Info] idx: {}'.format(data_idx))

    def process(self):
        data_lines = read_file(self.file_name)
        print('[Info] 样本数: {}'.format(len(data_lines)))
        pool = Pool(processes=40)
        for data_idx, data_line in enumerate(data_lines):
            img_url = data_line.split("\t")[0]
            # ServicesVersus.process_line(data_idx, img_url, self.out_file)
            pool.apply_async(ServicesVersus.process_line, (data_idx, img_url, self.out_file))
        pool.close()
        pool.join()
        print('[Info] 全部处理完成! {}'.format(self.file_name))


def main():
    sv = ServicesVersus()
    sv.process()


if __name__ == '__main__':
    main()
