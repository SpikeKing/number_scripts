#!/usr/bin/env python
# -- coding: utf-8 --
"""
Copyright (c) 2021. All rights reserved.
Created by C. L. Wang on 17.8.21
"""
import os

import cv2
import numpy as np

from myutils.cv_utils import show_img_bgr
from root_dir import DATA_DIR


class ImageBkgModified(object):

    def __init__(self):
        self.gray_boundary = 250
        self.s_color = (245, 245, 245)  # F5F5F5

    @staticmethod
    def paste_png_on_bkg(draw_png, bkg_png, offset):
        """
        PNG粘贴到背景之上，支持处理3通道的背景
        """
        bh, bw, bc = bkg_png.shape
        if bc == 3:
            bkg_png = cv2.cvtColor(bkg_png, cv2.COLOR_BGR2BGRA)

        h, w, _ = draw_png.shape
        x, y = offset

        alpha_mask = np.where(draw_png[:, :, 3] == 255, 1, 0)
        alpha_mask = np.repeat(alpha_mask[:, :, np.newaxis], 4, axis=2)  # 将mask复制4次

        y_s, y_e = min(y, bh), min(y + h, bh)
        x_s, x_e = min(x, bw), min(x + w, bw)

        bkg_png[y_s:y_e, x_s:x_e, :] = (1.0 - alpha_mask) * bkg_png[y_s:y_e, x_s:x_e] + alpha_mask * draw_png

        if bc == 3:
            bkg_png = cv2.cvtColor(bkg_png, cv2.COLOR_BGRA2BGR)

        return bkg_png

    def get_center_img(self, img_rgb):
        """
        获取核心图像
        """
        gray_img = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        img_mask = np.where(gray_img > self.gray_boundary, 0, 255)

        # 提取中心透明图像
        h, w, c = img_rgb.shape
        img_png = np.zeros((h, w, 4), dtype=np.uint8)
        img_png[:, :, :3] = img_rgb[:, :, :3]
        img_png[:, :, 3] = img_mask

        bkg = np.ones((h, w, c))
        bkg[:, :, 0] = self.s_color[0]
        bkg[:, :, 1] = self.s_color[1]
        bkg[:, :, 2] = self.s_color[2]

        bkg = bkg.astype(np.uint8)

        img_rgb = self.paste_png_on_bkg(img_png, bkg, offset=(0, 0))

        return img_rgb


def main():
    ibm = ImageBkgModified()

    img_path = os.path.join(DATA_DIR, "img.jpg")
    img_bgr = cv2.imread(img_path)
    show_img_bgr(img_bgr)
    img_bgr = ibm.get_center_img(img_bgr)
    show_img_bgr(img_bgr, save_name="img.out.jpg")


if __name__ == '__main__':
    main()