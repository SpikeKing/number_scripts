#!/usr/bin/env python
# -- coding: utf-8 --
"""
Copyright (c) 2021. All rights reserved.
Created by C. L. Wang on 16.8.21
"""

from multiprocessing.pool import Pool

import pandas

from myutils.cv_utils import *
from myutils.project_utils import *
from root_dir import DATA_DIR


class LabelGeneratorV6(object):
    def __init__(self):
        self.file1_path = os.path.join(DATA_DIR, "numbers_files", "1c5f7277-a78b-4637-8143-b8656fc58798_166438.csv")
        self.file2_path = os.path.join(DATA_DIR, "numbers_files", "75d3342e-2fc9-4849-95fb-a5c5b687ada3_166438.csv")
        self.file3_path = os.path.join(DATA_DIR, "numbers_files", 'clean_hw_numbers_v3_train-new.txt')
        self.out_file_path = os.path.join(DATA_DIR, "numbers_files", "clean_hw_numbers_v4_1_ori.txt")

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
            oss_root_dir = "zhengsheng.wcl/Character-Detection/datasets/hw-numbers-imgs-v4_1/"
        img_url = save_img_2_oss(img_bgr, img_name, oss_root_dir)
        # img_url = img_url.replace("http://quark-cv-data.oss-cn-hangzhou.aliyuncs.com",
        #                           "https://quark-cv-data.oss-cn-hangzhou.alibaba-inc.com")
        return img_url

    @staticmethod
    def format_label(data_label):
        """
        格式化label
        """
        try:
            x = float(data_label)
            return data_label
        except Exception as e:
            if "&" in data_label:
                return ""
            items = data_label.split("/")
            if len(items) == 2 and items[0] and items[1]:
                x = "\\frac{%s}{%s}" % (items[0], items[1])
                return x
            items = data_label.split("\\")
            if len(items) == 2 and items[0] and items[1]:
                x = "\\frac{%s}{%s}" % (items[0], items[1])
                return x
        return ""

    @staticmethod
    def process_file(file_path):
        """
        处理文件
        """
        print('[Info] file_path: {}'.format(file_path))
        data = pandas.read_csv(file_path)
        print("[Info] 样本数: {}".format(data.shape[0]))
        image_label_dict = dict()
        for idx, data_row in data.iterrows():
            data_info = json.loads(data_row["问题内容"])
            label_info = json.loads(data_row["回答内容"])
            input_1 = label_info['input_1']

            img_url = data_info[0]
            img_label = input_1
            img_label = LabelGeneratorV6.format_label(img_label)

            if img_url not in image_label_dict.keys():
                image_label_dict[img_url] = img_label
            else:
                label1 = str(img_label)
                label2 = str(image_label_dict[img_url])
                if label1 != label2:
                    if len(label1) > len(label2):
                        image_label_dict[img_url] = label1
                    if len(label1) == len(label2):
                        # print('[Info] label1: {}, label2: {}, url: {}'.format(label1, label2, img_url))
                        pass
        print('[Info] 清洗之后样本数: {}'.format(len(image_label_dict.keys())))
        print('[Info] ' + "-" * 50)
        return image_label_dict

    @staticmethod
    def process_file_v2(file_path):
        """
        处理文件
        """
        print('[Info] file_path: {}'.format(file_path))
        data = pandas.read_csv(file_path)
        print("[Info] 样本数: {}".format(data.shape[0]))
        image_label_dict = dict()
        for idx, data_row in data.iterrows():
            data_info = json.loads(data_row["question_content"])
            label_info = data_row["input_1"]

            img_url = data_info[0]
            img_label = label_info.split("[")[0]
            img_label = LabelGeneratorV6.format_label(img_label)

            if img_url not in image_label_dict.keys():
                image_label_dict[img_url] = img_label
            else:
                label1 = str(img_label)
                label2 = str(image_label_dict[img_url])
                if label1 != label2:
                    if len(label1) > len(label2):
                        image_label_dict[img_url] = label1
                    if len(label1) == len(label2):
                        print('[Info] label1: {}, label2: {}, url: {}'.format(label1, label2, img_url))
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

    def process(self):
        image_label_dict1 = self.process_file(self.file1_path)
        image_label_dict2 = self.process_file_v2(self.file2_path)
        err_count = 0

        image_label_dict12 = dict()
        for image_url in image_label_dict2.keys():
            label1 = image_label_dict1[image_url]
            label2 = image_label_dict2[image_url]
            if label1 != label2:
                err_count += 1
            else:
                image_label_dict12[image_url] = label1
        print('[Info] 样本总数: {}, error_count: {}'.format(len(image_label_dict2.keys()), err_count))
        print('[Info] 正确样本数: {}'.format(len(image_label_dict12.keys())))

        # image_label_dict3 = self.process_file_ex(self.file3_path)
        # image_label_dict_re = dict(image_label_dict3, **image_label_dict12)
        # print('[Info] 样本总数: {}'.format(len(image_label_dict_re.keys())))

        out_list = []
        for image_url in image_label_dict12.keys():
            img_label = image_label_dict12[image_url]
            out_list.append('{}\t{}'.format(image_url, img_label))

        random.seed(47)
        random.shuffle(out_list)
        write_list_to_file(self.out_file_path, out_list)
        print('[Info] 写入完成: {}'.format(self.out_file_path))

    @staticmethod
    def process_line(img_idx, img_url, img_label, angle_range, out_file):
        try:
            write_line(out_file, "{}\t{}".format(img_url, img_label))
            _, img_bgr_ori = download_url_img(img_url)
            for i in range(2):
                angle = random.randint(angle_range * (-1), angle_range)
                img_bgr, _ = rotate_img_with_bound(img_bgr_ori, angle, border_value=(255, 255, 255))
                img_bgr = LabelGeneratorV6.get_center_img(img_bgr)
                img_name = img_url.split("/")[-1].split(".")[0]
                img_name_new = "{}-angle-{}.jpg".format(img_name, angle)
                img_url_new = LabelGeneratorV6.save_img_path(img_bgr, img_name_new)
                write_line(out_file, "{}\t{}".format(img_url_new, img_label))

            for i in range(2):
                x_size = round(random.uniform(0.7, 1.3), 1)
                y_size = round(random.uniform(0.7, 1.3), 1)
                img_bgr = cv2.resize(img_bgr_ori, None, fx=x_size, fy=y_size)
                img_bgr = LabelGeneratorV6.get_center_img(img_bgr)
                img_name = img_url.split("/")[-1].split(".")[0]
                img_name_new = "{}-size-{}x{}.jpg".format(img_name, x_size, y_size)
                img_url_new = LabelGeneratorV6.save_img_path(img_bgr, img_name_new)
                write_line(out_file, "{}\t{}".format(img_url_new, img_label))
            print('[Info] 处理完成: {}'.format(img_idx))
        except Exception as e:
            print('[Error] e: {}'.format(e))

    @staticmethod
    def process_line_v2(img_idx, img_url, img_label, angle_range, out_file):
        try:
            write_line(out_file, "{}\t{}".format(img_url, img_label))
            _, img_bgr_ori = download_url_img(img_url)
            angle = random.randint(angle_range * (-1), angle_range)
            img_bgr, _ = rotate_img_with_bound(img_bgr_ori, angle, border_value=(255, 255, 255))
            img_bgr = LabelGeneratorV6.get_center_img(img_bgr)
            img_name = img_url.split("/")[-1].split(".")[0]
            img_name_new = "val-{}.jpg".format(img_name, img_idx)
            img_url_new = LabelGeneratorV6.save_img_path(img_bgr, img_name_new)
            write_line(out_file, "{}\t{}".format(img_url_new, img_label))
        except Exception as e:
            print('[Error] e: {}'.format(e))

    def process_v1(self):
        file_path = os.path.join(DATA_DIR, "numbers_files", "clean_hw_numbers_v4_1_ori.txt")
        out_file_path = os.path.join(
            DATA_DIR, "numbers_files", "clean_hw_numbers_v4_1_train-{}.txt".format(get_current_time_str()))
        print('[Info] file_path: {}'.format(file_path))
        image_label_dict = self.process_file_ex(file_path)
        print('[Info] 样本数: {}'.format(len(image_label_dict.keys())))
        angle_range = 15
        pool = Pool(processes=100)
        for img_idx, img_url in enumerate(image_label_dict.keys()):
            img_label = image_label_dict[img_url]
            # LabelGeneratorV6.process_line(img_idx, img_url, img_label, angle_range, out_file_path)
            pool.apply_async(LabelGeneratorV6.process_line, (img_idx, img_url, img_label, angle_range, out_file_path))
            # if img_idx == 0:
            #     break
        pool.close()
        pool.join()
        print('[Info] 处理完成: {}'.format(out_file_path))

    def process_val(self):
        file_path = os.path.join(DATA_DIR, "numbers_files", "clean_hw_numbers_v4_1_ori.txt")
        out_file_path = os.path.join(
            DATA_DIR, "numbers_files", "clean_hw_numbers_v4_1_test-{}.txt".format(get_current_time_str()))
        print('[Info] file_path: {}'.format(file_path))
        image_label_dict = self.process_file_ex(file_path)
        print('[Info] 样本数: {}'.format(len(image_label_dict.keys())))
        angle_range = 15
        pool = Pool(processes=100)
        for img_idx, img_url in enumerate(image_label_dict.keys()):
            if img_idx == 1000:
                break
            img_label = image_label_dict[img_url]
            pool.apply_async(LabelGeneratorV6.process_line_v2,
                             (img_idx, img_url, img_label, angle_range, out_file_path))
        pool.close()
        pool.join()
        print('[Info] 处理完成: {}'.format(out_file_path))


    def split_file(self):
        file_path = os.path.join(DATA_DIR, "numbers_files", "clean_hw_numbers_v4_train.txt")
        out_file_format = os.path.join(DATA_DIR, "numbers_files", "clean_hw_numbers_v4_train.s{}.txt")
        data_lines = read_file(file_path)
        n_split = 4
        gap = len(data_lines) // n_split
        for i in range(n_split):
            end = min(i+1*gap, len(data_lines))
            sub_lines = data_lines[i:end]
            out_file = out_file_format.format(str(i))
            write_list_to_file(out_file, sub_lines)


def main():
    lg = LabelGeneratorV6()
    lg.process_val()


if __name__ == '__main__':
    main()
