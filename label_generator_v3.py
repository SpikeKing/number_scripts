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


class LabelGeneratorV3(object):
    def __init__(self):
        self.file1_path = os.path.join(DATA_DIR, "numbers_files", "706d7791-b96c-4524-b116-aa6af45f7e24_166344.csv")
        self.file2_path = os.path.join(DATA_DIR, "numbers_files", "4c0e0406-cd33-4b90-8607-ad87f5d27e1a_166332.csv")
        self.file3_path = os.path.join(DATA_DIR, "numbers_files", "3d30b85f-5318-4bbb-ab1b-7262ad74fd7c_166330.csv")
        self.file4_path = os.path.join(DATA_DIR, "numbers_files", "beab7dca-931a-4b67-ab16-02daa8f3199e_166322.csv")
        self.file5_path = os.path.join(DATA_DIR, "numbers_files", "clean_num_and_op_train.txt")
        self.file6_path = os.path.join(DATA_DIR, "numbers_files", "e0588eb6-f3e9-41f7-86c8-a019e33c7a33_166355.csv")
        self.file7_path = os.path.join(DATA_DIR, "numbers_files", "8ad26809-6a2c-48d6-83d3-7133ad7d236f_166331.csv")
        self.out_file_path = os.path.join(DATA_DIR, 'numbers_files', 'out-{}.txt'.format(get_current_time_str()))

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
            oss_root_dir = "zhengsheng.wcl/Character-Detection/datasets/hw-numbers-imgs-v1/"
        img_url = save_img_2_oss(img_bgr, img_name, oss_root_dir)
        img_url = img_url.replace("http://quark-cv-data.oss-cn-hangzhou.aliyuncs.com",
                                  "https://quark-cv-data.oss-cn-hangzhou.alibaba-inc.com")
        return img_url

    @staticmethod
    def format_url(img_url, img_name):
        """
        格式化url
        """
        img_url = unquote(img_url)
        _, img_bgr = download_url_img(img_url)
        img_bgr = LabelGeneratorV3.get_center_img(img_bgr)
        img_url = LabelGeneratorV3.save_img_path(img_bgr, img_name)
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
    def process_line(idx, img_url, img_label, out_file):
        """
        处理单行数据
        """
        try:
            new_img_name = "v1_1-{}-{}.jpg".format(get_current_day_str(), str(idx).zfill(6))
            new_img_url = LabelGeneratorV3.format_url(img_url, new_img_name)
            new_img_label = LabelGeneratorV3.format_label(img_label)
            if not new_img_label:
                return
            write_line(out_file, "{}\t{}".format(new_img_url, new_img_label))
            print('[Info] 处理完成: {}'.format(idx))
        except Exception as e:
            print('[Info] 处理失败: {}'.format(idx))

    @staticmethod
    def process_file(file_path):
        print('[Info] file_path: {}'.format(file_path))
        data = pandas.read_csv(file_path)
        print("[Info] 样本数: {}".format(data.shape[0]))
        image_label_dict = dict()
        for idx, data_row in data.iterrows():
            data_info = json.loads(data_row["问题内容"])
            label_info = json.loads(data_row["回答内容"])
            radio_1 = label_info['radio_1']
            input_1 = label_info['input_1']
            if len(data_info) != 2:
                continue
            img_url = data_info[0]
            img_label = data_info[1]
            img_label = LabelGeneratorV3.format_label(img_label)
            if radio_1 != "0" and input_1:
                # print('[Info] input_1: {}'.format(input_1))
                # print('[Info] img_url: {}, img_label: {}'.format(img_url, img_label))
                image_label_dict[img_url] = img_label
            elif radio_1 == "0":
                image_label_dict[img_url] = img_label
        print('[Info] 清洗之后样本数: {}'.format(len(image_label_dict.keys())))
        print('[Info] ' + "-" * 50)
        return image_label_dict

    @staticmethod
    def process_file_ex(file_path):
        print('[Info] file_path: {}'.format(file_path))
        data_lines = read_file(file_path)
        print("[Info] 样本数: {}".format(len(data_lines)))
        image_label_dict = dict()
        for data_line in data_lines:
            items = data_line.split("\t")
            img_url = items[0]
            label_str = items[1]
            image_label_dict[img_url] = label_str
        print('[Info] 清洗之后样本数: {}'.format(len(image_label_dict.keys())))
        print('[Info] ' + "-" * 50)
        return image_label_dict

    def process_v1(self):
        """
        处理数据
        """
        image1_label_dict = LabelGeneratorV3.process_file(self.file1_path)
        image2_label_dict = LabelGeneratorV3.process_file(self.file2_path)
        image3_label_dict = LabelGeneratorV3.process_file(self.file3_path)
        image4_label_dict = LabelGeneratorV3.process_file(self.file4_path)
        image5_label_dict = LabelGeneratorV3.process_file_ex(self.file5_path)

        res_label_dict = dict()
        for image_x_label_dict in [image2_label_dict, image3_label_dict, image4_label_dict, image5_label_dict]:
            for image_url in image_x_label_dict.keys():
                if image_url not in image1_label_dict.keys():
                    continue
                label_ex1 = image1_label_dict[image_url]
                label_ex2 = image_x_label_dict[image_url]
                if label_ex1 != label_ex2:
                    continue
                else:
                    res_label_dict[image_url] = label_ex1
        print('[Info] 样本数: {}'.format(len(res_label_dict.keys())))
        print('[Info] 样本数ex: {}'.format(len(image1_label_dict.keys())))

        pool = Pool(processes=100)
        for img_idx, img_url in enumerate(res_label_dict.keys()):
            img_label = res_label_dict[img_url]
            # LabelGeneratorV3.process_line(img_idx, img_url, img_label, self.out_file_path)
            pool.apply_async(LabelGeneratorV3.process_line, (img_idx, img_url, img_label, self.out_file_path))
            # if img_idx == 10:
            #     break
        pool.close()
        pool.join()

        print('[Info] 处理完成: {}'.format(self.out_file_path))

    def process_v1_1(self):
        """
        处理数据
        """
        image1_label_dict = LabelGeneratorV3.process_file(self.file6_path)
        image2_label_dict = LabelGeneratorV3.process_file(self.file7_path)

        res_label_dict = dict()
        for image_x_label_dict in [image2_label_dict]:
            for image_url in image_x_label_dict.keys():
                if image_url not in image1_label_dict.keys():
                    continue
                label_ex1 = image1_label_dict[image_url]
                label_ex2 = image_x_label_dict[image_url]
                if label_ex1 != label_ex2:
                    continue
                else:
                    res_label_dict[image_url] = label_ex1
        print('[Info] 样本数: {}'.format(len(res_label_dict.keys())))
        print('[Info] 样本数ex: {}'.format(len(image1_label_dict.keys())))

        pool = Pool(processes=100)
        for img_idx, img_url in enumerate(res_label_dict.keys()):
            img_label = res_label_dict[img_url]
            pool.apply_async(LabelGeneratorV3.process_line, (img_idx, img_url, img_label, self.out_file_path))
            # LabelGeneratorV3.process_line(img_idx, img_url, img_label, self.out_file_path)
            # if img_idx == 10:
            #     break
        pool.close()
        pool.join()

        print('[Info] 处理完成: {}'.format(self.out_file_path))

    @staticmethod
    def split_train_test():
        file1_name = os.path.join(DATA_DIR, 'numbers_files', "clean_hw_numbers_v1.txt")
        file2_name = os.path.join(DATA_DIR, 'numbers_files', "clean_hw_numbers_v1_1.txt")
        train_file = os.path.join(DATA_DIR, 'numbers_files', "clean_hw_numbers_v1_train.txt")
        test_file = os.path.join(DATA_DIR, 'numbers_files', "clean_hw_numbers_v1_test.txt")
        data1_lines = read_file(file1_name)
        data2_lines = read_file(file2_name)
        data_lines = data1_lines + data2_lines
        random.seed(47)
        random.shuffle(data_lines)
        test_lines = data_lines[:2000]
        train_lines = data_lines[2000:]
        write_list_to_file(train_file, train_lines)
        write_list_to_file(test_file, test_lines)

    @staticmethod
    def process_line_x(img_idx, img_url, img_label, out_file, oss_root_dir):
        _, img_bgr = download_url_img(img_url)
        img_name = "pressed-v1-{}-{}.jpg".format(get_current_day_str(), str(img_idx).zfill(6))
        out_url = LabelGeneratorV3.save_img_path(img_bgr, img_name, oss_root_dir)
        write_line(out_file, "{}\t{}".format(out_url, img_label))
        print('[Info] 处理完成: {}'.format(img_idx))

    @staticmethod
    def upload_jpg_imgs():
        file_path = os.path.join(DATA_DIR, "numbers_files", "706d7791-b96c-4524-b116-aa6af45f7e24_166344.csv")
        out_file = os.path.join(DATA_DIR, "numbers_files", "pressed_test_10000.txt")
        data_dict = LabelGeneratorV3.process_file(file_path)
        oss_root_dir = "zhengsheng.wcl/Character-Detection/datasets/hw-numbers-imgs-ori/"

        pool = Pool(processes=100)
        for img_idx, img_url in enumerate(data_dict.keys()):
            img_label = data_dict[img_url]
            # LabelGeneratorV3.process_line_x(img_idx, img_url, img_label, out_file, oss_root_dir)
            pool.apply_async(LabelGeneratorV3.process_line_x, (img_idx, img_url, img_label, out_file, oss_root_dir))
            if img_idx == 10000 - 1:
                break
        pool.close()
        pool.join()
        print("[Info] 处理完成: {}".format(out_file))


def main():
    lg = LabelGeneratorV3()
    # lg.process_v1()
    # lg.process_v1_1()
    # lg.split_train_test()
    lg.upload_jpg_imgs()


if __name__ == '__main__':
    main()
