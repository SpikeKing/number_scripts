#!/usr/bin/env python
# -- coding: utf-8 --
"""
Copyright (c) 2021. All rights reserved.
Created by C. L. Wang on 28.7.21
"""

from PIL import Image

from myutils.cv_utils import *
from myutils.project_utils import *
from root_dir import DATA_DIR


class ImageResized(object):
    def __init__(self):
        self.gray_boundary = 250
        pass

    def get_center_img(self, img_rgb):
        """
        获取核心图像
        """
        height, width, channel = img_rgb.shape
        if (height > 0 and width > 0
            and ((self.is_not_blank(img_rgb[0, 0]) and self.is_not_blank(img_rgb[height - 1, width - 1]))
                or (self.is_not_blank(img_rgb[height - 1, 0]) and self.is_not_blank(img_rgb[0, width - 1]))
            )
        ):
            return img_rgb
        gray_img = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        coords = cv2.findNonZero((gray_img < self.gray_boundary).astype(np.uint8)) # Find all non-zero points (text)

        if coords is None:
            return img_rgb
        if coords.shape[0] > width * height - min(width, height):
            return img_rgb
        img_mask = np.where(gray_img > self.gray_boundary, 0, 255)

        # 提取中心透明图像
        h, w, _ = img_rgb.shape
        img_png = np.zeros((h, w, 4), dtype=np.uint8)
        img_png[:, :, :3] = img_rgb[:, :, :3]
        img_png[:, :, 3] = img_mask
        x, y, w, h = cv2.boundingRect(coords)  # Find minimum spanning bounding box

        if x == 0 and y == 0 and w == width and h == height:
            return img_rgb
        img_png = img_png[y:y+h, x:x+w]

        img_rgb = cv2.cvtColor(img_png, cv2.COLOR_RGBA2RGB)
        size = max(w, h)

        img_rgb = resize_with_padding(img_rgb, size)

        # 添加边框
        pad_size = size // 50  # 边框比例
        top, bottom, left, right = [pad_size] * 4
        img_rgb = cv2.copyMakeBorder(img_rgb, top, bottom, left, right,
                                     borderType=cv2.BORDER_CONSTANT, value=(255, 255, 255))
        return img_rgb

    def is_not_blank(self, rgb):
        gray = 0.2989 * rgb[0] + 0.5870 * rgb[1] + 0.1140 * rgb[2]
        return gray < self.gray_boundary

    def get_thumbnail_num_img(self, img_bgr, size=80):
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        img_rgb = self.get_center_img(img_rgb)

        img = Image.fromarray(img_rgb)
        img_r = img.resize((80, 80), Image.ANTIALIAS)
        img_rgb = np.array(img_r)
        # img_rgb = cv2.resize(img_rgb, (size, size), cv2.INTER_AREA)  # 必须选择INTER_AREA
        img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        return img_bgr

    def process_url(self, idx, img_url, out_path):
        _, img_bgr = download_url_img(img_url)
        img_out = self.get_thumbnail_num_img(img_bgr)
        cv2.imwrite(out_path, img_out)
        print('[Info] {} 处理完成: {}'.format(idx, out_path))

    def process(self):
        file_name = os.path.join(DATA_DIR, "numbers_dataset_v1.txt")
        out_dir = os.path.join(DATA_DIR, "numbers_thumbnail_v2")
        mkdir_if_not_exist(out_dir)
        data_lines = read_file(file_name)
        random.seed(47)
        random.shuffle(data_lines)
        data_lines = data_lines[:100]
        print('[Info] 样本数: {}'.format(len(data_lines)))
        for idx, data_line in enumerate(data_lines):
            out_name = data_line.split("/")[-1].split(".")[0]
            img_name = "{}.jpg".format(out_name)
            out_path = os.path.join(out_dir, img_name)
            self.process_url(idx, data_line, out_path)
        print('[Info] 全部完成: {}'.format(out_dir))


def main():
    ir = ImageResized()
    ir.process()


if __name__ == '__main__':
    main()
