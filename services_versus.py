#!/usr/bin/env python
# -- coding: utf-8 --
"""
Copyright (c) 2021. All rights reserved.
Created by C. L. Wang on 3.8.21
"""
from multiprocessing.pool import Pool

from myutils.make_html_page import make_html_page
from myutils.project_utils import *
from root_dir import DATA_DIR
from x_utils.vpf_sevices import get_hw_numbers_service


class ServicesVersus(object):
    """
    对比模型
    """
    def __init__(self):
        # file_name = "a2e455ff-b77b-4f65-ae59-864cfa20bdd8_166274.out-20210803112232.vs-20210803150735"
        file_name = "hw_numbers_check_2200"
        # file_name = "hw_numbers_check_v2_1000"
        # file_name = "hw_numbers_symbol_check"
        time_str = get_current_time_str()
        self.file_path = os.path.join(DATA_DIR, 'numbers_files', '{}.txt'.format(file_name))
        self.out_file_path = os.path.join(DATA_DIR, 'numbers_files', '{}.vs-{}.txt'.format(file_name, time_str))
        self.html_file_path = os.path.join(DATA_DIR, 'numbers_files', '{}.vs-{}.html'.format(file_name, time_str))

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
    def predict_online(img_url):
        res_dict = get_hw_numbers_service(img_url, service_name="LcfC3ATXgDBFWkGMtkQV77")
        ocr_text = res_dict['data']['ocr_text']
        return ocr_text

    @staticmethod
    def process_line(data_idx, img_url, label_str, out_file):
        # try:
        # res1 = ServicesVersus.predict_online(img_url)
        # res2 = ServicesVersus.predict_v1(img_url)
        res3 = ServicesVersus.predict_v1_1(img_url)
        # img_url = img_url.replace("http://quark-cv-data.oss-cn-hangzhou.aliyuncs.com",
        #                           "https://quark-cv-data.oss-cn-hangzhou.alibaba-inc.com")
        # if res1 != label_str or res2 != label_str or res3 != label_str:
        #     print('[Info] data_idx: {}, label_str: {}, res1: {}, res2: {}, res3: {}, img_url: {}'
        #           .format(data_idx, label_str, res1, res2, res3, img_url))
        #     write_line(out_file, ",".join([label_str, res1, res2, res3, img_url]))
        res = res3
        if res != label_str:
            img_url_show = img_url.replace("http://quark-cv-data.oss-cn-hangzhou.aliyuncs.com",
                                           "https://quark-cv-data.oss-cn-hangzhou.alibaba-inc.com")
            print('[Info] data_idx: {}, label_str: {}, res1: {}, img_url_show: {}'
                  .format(data_idx, label_str, res, img_url_show))
            write_line(out_file, ",".join([label_str, res, img_url]))
        if data_idx % 10 == 0:
            print('[Info] idx: {}'.format(data_idx))
        # except Exception as e:
        #     print('[Error] data_idx: {}'.format(data_idx))

    def process(self):
        print('[Info] file_path: {}'.format(self.file_path))
        data_lines = read_file(self.file_path)
        print('[Info] 样本数: {}'.format(len(data_lines)))
        pool = Pool(processes=40)
        for data_idx, data_line in enumerate(data_lines):
            img_url = data_line.split("\t")[0]
            label_str = data_line.split("\t")[1]
            # ServicesVersus.process_line(data_idx, img_url, label_str, self.out_file_path)
            pool.apply_async(ServicesVersus.process_line, (data_idx, img_url, label_str, self.out_file_path))
        pool.close()
        pool.join()
        print('[Info] 全部处理完成! {}'.format(self.out_file_path))

        out_data_lines = read_file(self.out_file_path)
        print('[Info] 样本数: {}'.format(len(out_data_lines)))
        html_lines = []
        for data_line in out_data_lines:
            item_list = data_line.split(",")
            html_lines.append(item_list)
        make_html_page(self.html_file_path, html_lines)
        print('[Info] 输出: {}'.format(self.html_file_path))
        print('[Info] 正确率: {}'.format(safe_div(len(data_lines)-len(out_data_lines), len(data_lines))))

    def process_v1(self):
        print('[Info] file_path: {}'.format(self.file_path))
        data_lines = read_file(self.file_path)
        print('[Info] 样本数: {}'.format(len(data_lines)))
        data_dict = collections.defaultdict(int)
        for data_idx, data_line in enumerate(data_lines):
            img_url = data_line.split("\t")[0]
            label_str = data_line.split("\t")[1]
            data_dict[label_str] += 1
        print(data_dict)


def main():
    sv = ServicesVersus()
    sv.process()


if __name__ == '__main__':
    main()
