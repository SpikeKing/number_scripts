#!/usr/bin/env python
# -- coding: utf-8 --
"""
Copyright (c) 2021. All rights reserved.
Created by C. L. Wang on 2.8.21
"""

from multiprocessing.pool import Pool
from myutils.cv_utils import *
from myutils.make_html_page import make_html_page
from myutils.project_utils import *
from root_dir import DATA_DIR
from x_utils.vpf_sevices import get_hw_numbers_service


class LabelGeneratorV4(object):
    def __init__(self):
        self.folder_path = os.path.join(DATA_DIR, "hw-numbers-imgs-v3_1-raw")
        self.out_file_path = os.path.join(DATA_DIR, "hw-numbers-imgs-v3_1-raw.check.txt")
        self.out_html_path = os.path.join(DATA_DIR, "hw-numbers-imgs-v3_1-raw.check.html")

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
            oss_root_dir = "zhengsheng.wcl/Character-Detection/datasets/hw-numbers-imgs-v3_1/"
        img_url = save_img_2_oss(img_bgr, img_name, oss_root_dir)
        return img_url

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
    def process_line(p_idx, path, out_file):
        img_bgr = cv2.imread(path)
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        img_rgb = LabelGeneratorV4.get_center_img(img_rgb)
        img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        # show_img_bgr(img_bgr)
        img_name = "v3_1-{}-{}.jpg".format(p_idx, get_current_day_str())
        img_url = LabelGeneratorV4.save_img_path(img_bgr, img_name)
        res1 = LabelGeneratorV4.predict_v1(img_url)
        res2 = LabelGeneratorV4.predict_v1_1(img_url)
        write_line(out_file, "\t".join([img_url, res1, res2]))
        print('[Info] img_url: {}, res1: {}, res2: {}'.format(img_url, res1, res2))
        print('[Info] 处理完成: {}'.format(p_idx))

    def process(self):
        print('[Info] 处理文件: {}'.format(self.folder_path))
        paths_list, names_list = traverse_dir_files(self.folder_path)
        print('[Info] 样本数: {}'.format(len(paths_list)))
        pool = Pool(processes=40)
        for p_idx, path in enumerate(paths_list):
            if p_idx == 100:
                break
            # LabelGeneratorV4.process_line(p_idx, path, self.out_file_path)
            pool.apply_async(LabelGeneratorV4.process_line, (p_idx, path, self.out_file_path))
        pool.close()
        pool.join()
        print('[Info] 输出: {}'.format(self.out_file_path))
        data_lines = read_file(self.out_file_path)
        print('[Info] 检测行数: {}'.format(len(data_lines)))
        out_lines = []
        for img_idx, data_line in enumerate(data_lines):
            items = data_line.split("\t")
            out_lines.append(items)
        make_html_page(self.out_html_path, out_lines)
        print('[Info] 输出: {}'.format(self.out_html_path))



def main():
    lg = LabelGeneratorV4()
    lg.process()


if __name__ == '__main__':
    main()
