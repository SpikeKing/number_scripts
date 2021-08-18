#!/usr/bin/env python
# -- coding: utf-8 --
"""
Copyright (c) 2021. All rights reserved.
Created by C. L. Wang on 10.8.21
"""

import cv2
import os

from root_dir import DATA_DIR


def main():
    img_path = os.path.join(DATA_DIR, 'img.jpg')
    img_bgr = cv2.imread(img_path)


if __name__ == '__main__':
    main()
