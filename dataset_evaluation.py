#!/usr/bin/env python
# -- coding: utf-8 --
"""
Copyright (c) 2021. All rights reserved.
Created by C. L. Wang on 4.8.21
"""

from multiprocessing.pool import Pool

from myutils.project_utils import *
from root_dir import DATA_DIR
from x_utils.vpf_sevices import get_hw_numbers_service


class DatasetEvaluation(object):
    def __init__(self):
        file_name = "clean_hw_numbers_v2_train"
        self.file_path = os.path.join(DATA_DIR, "numbers_files", '{}.txt'.format(file_name))
        time_str = get_current_time_str()
        self.out_file_path = os.path.join(
            DATA_DIR, "numbers_files", '{}.out-{}.txt'.format(file_name, time_str))
        self.diff_file_path = os.path.join(
            DATA_DIR, "numbers_files", '{}.diff-{}.txt'.format(file_name, time_str))

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
    def process_line(data_idx, img_url, label_str, out_file_path, diff_file_path):
        # res1 = DatasetEvaluation.predict_danjing(img_url)
        res2 = DatasetEvaluation.predict_v1(img_url)
        # res3 = DatasetEvaluation.predict_v1_1(img_url)
        # if res1 != label_str or res2 != label_str or res3 != label_str:
        #     print('[Info] label_str: {}, res1: {}, res2: {}, res3: {}, img_url: {}'
        #           .format(label_str, res1, res2, res3, img_url))
        #     write_line(diff_file_path, ",".join([label_str, res1, res2, res3, img_url]))
        if res2 != label_str:
            img_url_show = img_url.replace("http://quark-cv-data.oss-cn-hangzhou.aliyuncs.com",
                                           "https://quark-cv-data.oss-cn-hangzhou.alibaba-inc.com")
            print('[Info] label_str: {}, res2: {}, img_url_show: {}'.format(label_str, res2, img_url_show))
            write_line(diff_file_path, ",".join([label_str, res2, img_url]))
        else:
            write_line(out_file_path, "\t".join([img_url, label_str]))
        if data_idx % 100 == 0:
            print('[Info] idx: {}'.format(data_idx))

    def process(self):
        data_lines = read_file(self.file_path)
        print('[Info] ????????????: {}'.format(self.file_path))
        print('[Info] ?????????: {}'.format(len(data_lines)))
        pool = Pool(processes=100)
        for data_idx, data_line in enumerate(data_lines):
            items = data_line.split("\t")
            img_url = items[0]
            label_str = items[1]
            # DatasetEvaluation.process_line(data_idx, img_url, label_str, self.out_file_path, self.diff_file_path)
            pool.apply_async(DatasetEvaluation.process_line,
                             (data_idx, img_url, label_str, self.out_file_path, self.diff_file_path))
        pool.close()
        pool.join()
        print('[Info] ????????????: {}'.format(self.out_file_path))
        print('[Info] ????????????: {}'.format(self.diff_file_path))

    @staticmethod
    def replace_host():
        file_name = os.path.join(DATA_DIR, "numbers_files", "clean_hw_numbers_v1_train_good.txt")
        print('[Info] ????????????: {}'.format(file_name))
        out_file_path = os.path.join(DATA_DIR, "numbers_files", "clean_hw_numbers_v1_train_good_x.txt")
        data_lines = read_file(file_name)
        print('[Info] ?????????: {}'.format(len(data_lines)))
        out_lines = []
        for data_line in data_lines:
            items = data_line.split("\t")
            img_url = items[0]
            img_label = items[1]
            img_url = img_url.replace("https://quark-cv-data.oss-cn-hangzhou.alibaba-inc.com",
                                      "http://quark-cv-data.oss-cn-hangzhou.aliyuncs.com")
            out_lines.append("\t".join([img_url, img_label]))
        write_list_to_file(out_file_path, out_lines)
        print('[Info] ????????????: {}'.format(out_file_path))



def main():
    de = DatasetEvaluation()
    de.process()
    # de.replace_host()


if __name__ == "__main__":
    main()
