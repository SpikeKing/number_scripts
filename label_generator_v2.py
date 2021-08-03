#!/usr/bin/env python
# -- coding: utf-8 --
"""
Copyright (c) 2021. All rights reserved.
Created by C. L. Wang on 2.8.21
"""
from multiprocessing.pool import Pool
from urllib.parse import unquote

import cv2
import pandas

from myutils.project_utils import *
from root_dir import DATA_DIR


class LabelGeneratorV2(object):
    def __init__(self):
        file_name = "4c0e0406-cd33-4b90-8607-ad87f5d27e1a_166332"
        self.file_path = os.path.join(DATA_DIR, "numbers_files", "{}.csv".format(file_name))
        self.out_file_path = os.path.join(
            DATA_DIR, 'numbers_files', '{}.out-{}.txt'.format(file_name, get_current_time_str()))

    @staticmethod
    def get_center_img(img_rgb):
        """
        获取核心图像
        """
        gray_boundary = 250

        def is_not_blank(rgb):
            """
            是否非空
            """
            gray = 0.2989 * rgb[0] + 0.5870 * rgb[1] + 0.1140 * rgb[2]
            return gray < gray_boundary

        height, width, channel = img_rgb.shape
        if (height > 0 and width > 0
            and ((is_not_blank(img_rgb[0, 0]) and is_not_blank(img_rgb[height - 1, width - 1]))
                 or (is_not_blank(img_rgb[height - 1, 0]) and is_not_blank(img_rgb[0, width - 1])))):
            return img_rgb
        gray_img = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        coords = cv2.findNonZero((gray_img < gray_boundary).astype(np.uint8)) # Find all non-zero points (text)

        if coords is None:
            return img_rgb
        if coords.shape[0] > width * height - min(width, height):
            return img_rgb

        # 提取中心透明图像
        h, w, _ = img_rgb.shape
        x, y, w, h = cv2.boundingRect(coords)  # Find minimum spanning bounding box

        return img_rgb[y:y+h, x:x+w]

    @staticmethod
    def save_img_path(img_bgr, img_name):
        """
        上传图像
        """
        from x_utils.oss_utils import save_img_2_oss
        oss_root_dir = "zhengsheng.wcl/Character-Detection/datasets/hw-numbers-imgs-v1/"
        img_url = save_img_2_oss(img_bgr, img_name, oss_root_dir)
        return img_url

    @staticmethod
    def format_url(img_url, img_name):
        """
        格式化url
        """
        img_url = unquote(img_url)
        _, img_bgr = download_url_img(img_url)
        img_bgr = LabelGeneratorV2.get_center_img(img_bgr)
        img_url = LabelGeneratorV2.save_img_path(img_bgr, img_name)
        return img_url

    @staticmethod
    def format_label(data_label):
        """
        格式化label
        """
        try:
            x = float(data_label)
        except Exception as e:
            if "&" in data_label:
                return ""
            items = data_label.split("/")
            if len(items) == 2:
                x = "\\frac{%s}{%s}" % (items[0], items[1])
                return x
            else:
                return data_label
        return data_label

    @staticmethod
    def process_line(idx, data_row, out_file):
        """
        处理单行数据
        """
        data_info = json.loads(data_row["问题内容"])
        label_info = json.loads(data_row["回答内容"])
        radio_1 = label_info['radio_1']
        input_1 = label_info['input_1']
        img_url = data_info[0]
        img_label = data_info[1]
        new_img_name = "{}.jpg".format(str(idx).zfill(6))
        new_img_url = LabelGeneratorV2.format_url(img_url, new_img_name)
        new_img_label = LabelGeneratorV2.format_label(img_label)
        if not new_img_label:
            return
        if radio_1 != "0":
            return
        write_line(out_file, "{}\t{}".format(new_img_url, new_img_label))
        print('[Info] 处理完成: {}'.format(idx))

    def process(self):
        data = pandas.read_csv(self.file_path)
        print("[Info] 样本数: {}".format(data.shape[0]))
        num_error = 0
        num_count = 0

        pool = Pool(processes=100)
        for idx, row in data.iterrows():
            # print('-' * 100)
            # LabelGeneratorV2.process_line(idx, row, self.out_file)
            pool.apply_async(LabelGeneratorV2.process_line, (idx, row, self.out_file_path))
            # num_count += 1
            # if idx == 100:
            #     break
        pool.close()
        pool.join()
        print('[Info] error: {}, count: {}, 错误率: {}'
              .format(num_error, num_count, safe_div(num_error, num_count)))

    @staticmethod
    def split_train_test():
        file_name = os.path.join(DATA_DIR, 'numbers_files', "numbers_dataset_v1.out-20210802170953.txt")
        train_file = os.path.join(DATA_DIR, 'numbers_files', "numbers_dataset_v1_train.txt")
        test_file = os.path.join(DATA_DIR, 'numbers_files', "numbers_dataset_v1_test.txt")
        data_lines = read_file(file_name)
        random.seed(47)
        random.shuffle(data_lines)
        test_lines = data_lines[:1000]
        train_lines = data_lines[1000:]
        write_list_to_file(train_file, train_lines)
        write_list_to_file(test_file, test_lines)



def main():
    lg = LabelGeneratorV2()
    # lg.process()
    lg.split_train_test()


if __name__ == '__main__':
    main()
