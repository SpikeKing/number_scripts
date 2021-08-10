#!/usr/bin/env python
# -- coding: utf-8 --
"""
Copyright (c) 2021. All rights reserved.
Created by C. L. Wang on 2.8.21
"""
from urllib.parse import unquote

import pandas

from multiprocessing.pool import Pool
from myutils.cv_utils import *
from myutils.project_utils import *
from root_dir import DATA_DIR


class LabelGeneratorV4(object):
    def __init__(self):
        self.file1_path = os.path.join(DATA_DIR, "numbers_files", "clean_hw_numbers_v2_train.txt")
        self.file2_path = os.path.join(DATA_DIR, "numbers_files", "dc00803b-74ce-433d-9cfa-faf2f5f8d034_166400.csv")
        self.out_file_path = os.path.join(DATA_DIR, 'numbers_files',
                                          'clean_hw_numbers_v3_train-{}.txt'.format(get_current_time_str()))

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
    def save_img_path(img_bgr, img_name, oss_root_dir=""):
        """
        上传图像
        """
        from x_utils.oss_utils import save_img_2_oss
        if not oss_root_dir:
            oss_root_dir = "zhengsheng.wcl/Character-Detection/datasets/hw-numbers-imgs-v3/"
        img_url = save_img_2_oss(img_bgr, img_name, oss_root_dir)
        # img_url = img_url.replace("http://quark-cv-data.oss-cn-hangzhou.aliyuncs.com",
        #                           "https://quark-cv-data.oss-cn-hangzhou.alibaba-inc.com")
        return img_url

    @staticmethod
    def format_url(img_url, img_name):
        """
        格式化url
        """
        img_url = unquote(img_url)
        _, img_bgr = download_url_img(img_url)
        img_bgr = LabelGeneratorV4.get_center_img(img_bgr)
        img_url = LabelGeneratorV4.save_img_path(img_bgr, img_name)
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
    def process_file(file_path):
        print('[Info] file_path: {}'.format(file_path))
        data = pandas.read_csv(file_path)
        print("[Info] 样本数: {}".format(data.shape[0]))
        image_label_dict = dict()
        for idx, data_row in data.iterrows():
            data_info = json.loads(data_row["问题内容"])
            label_info = json.loads(data_row["回答内容"])
            radio_1 = label_info['checkbox_1']
            input_1 = label_info['input_1']
            img_url = data_info[0]
            img_label = data_info[1:]
            res_label = ""
            if input_1:
                res_label = res_label
            else:
                label_idx = int(radio_1.split(",")[0])
                if label_idx <= 2:
                    res_label = img_label[label_idx]
            image_label_dict[img_url] = res_label
        print('[Info] 清洗之后样本数: {}'.format(len(image_label_dict.keys())))
        print('[Info] ' + "-" * 50)
        return image_label_dict

    @staticmethod
    def process_file_v2(file_path):
        print('[Info] file_path: {}'.format(file_path))
        data_lines = read_file(file_path)
        print("[Info] 样本数: {}".format(len(data_lines)))
        image_label_dict = dict()
        for data_line in data_lines:
            items = data_line.split("\t")
            img_url = items[0]
            img_label = items[1]
            image_label_dict[img_url] = img_label
        print('[Info] 清洗之后样本数: {}'.format(len(image_label_dict.keys())))
        print('[Info] ' + "-" * 50)
        return image_label_dict

    def process(self):
        image1_label_dict = LabelGeneratorV4.process_file(self.file2_path)
        image2_label_dict = LabelGeneratorV4.process_file_v2(self.file1_path)

        res_list = []
        for img_url in image2_label_dict.keys():
            res_label = image2_label_dict[img_url]
            if img_url in image1_label_dict.keys():
                img_label = image1_label_dict[img_url]
                if not img_label:
                    continue
                res_label = img_label
            res_list.append("{}\t{}".format(img_url, res_label))
        print('[Info] 处理之后: {}'.format(len(res_list)))
        write_list_to_file(self.out_file_path, res_list)
        print('[Info] 处理完成: {}'.format(self.out_file_path))

    @staticmethod
    def process_line(img_idx, img_url, img_label, angle_range, out_file):
        _, img_bgr = download_url_img(img_url)
        angle = random.randint(angle_range * (-1), angle_range)
        img_bgr, _ = rotate_img_with_bound(img_bgr, angle, border_value=(255, 255, 255))
        img_bgr = LabelGeneratorV4.get_center_img(img_bgr)
        img_name = img_url.split("/")[-1].split(".")[0]
        img_name_new = "{}-{}.jpg".format(img_name, angle)
        img_url_new = LabelGeneratorV4.save_img_path(img_bgr, img_name_new)
        write_line(out_file, "{}\t{}".format(img_url_new, img_label))
        print('[Info] 处理完成: {}'.format(img_idx))

    def process_v1(self):
        file_path = os.path.join(DATA_DIR, "numbers_files", "clean_hw_numbers_v3_train-new.txt")
        out_file_path = os.path.join(DATA_DIR, "numbers_files",
                                     "clean_hw_numbers_v3_train-{}.txt".format(get_current_time_str()))
        print('[Info] file_path: {}'.format(file_path))
        image_label_dict = self.process_file_v2(file_path)
        angle_range = 45
        pool = Pool(processes=100)
        for img_idx, img_url in enumerate(image_label_dict.keys()):
            img_label = image_label_dict[img_url]
            # LabelGeneratorV4.process_line(img_idx, img_url, img_label, angle_range, out_file_path)
            pool.apply_async(LabelGeneratorV4.process_line, (img_idx, img_url, img_label, angle_range, out_file_path))
        pool.close()
        pool.join()
        print('[Info] 处理完成: {}'.format(out_file_path))


def main():
    lg = LabelGeneratorV4()
    lg.process_v1()


if __name__ == '__main__':
    main()
