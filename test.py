#!/usr/bin/env python
# -- coding: utf-8 --
"""
Copyright (c) 2021. All rights reserved.
Created by C. L. Wang on 10.8.21
"""

def main():
    from swtloc import SWTLocalizer
    from swtloc.utils import imgshow
    import numpy as np

    swtl = SWTLocalizer()
    # Stroke Width Transform
    imgpath = "mydata/v2-20210805-028538.jpg"
    swtl.swttransform(imgpaths=imgpath, text_mode='lb_df',
                      save_results=True, save_rootpath='swtres/',
                      ac_sigma=1.0, gs_blurr=False,
                      minrsw=3, maxrsw=50, max_angledev=np.pi / 3)
    imgshow(swtl.swt_labelled3C)

if __name__ == '__main__':
    main()
