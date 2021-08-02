#!/usr/bin/env python
# -- coding: utf-8 --
"""
Copyright (c) 2021. All rights reserved.
Created by C. L. Wang on 28.7.21
"""
import urllib
from myutils.project_utils import *
from root_dir import DATA_DIR


class DataGenerator(object):
    def __init__(self):
        self.ds_type = "v2"
        self.file_path = os.path.join(DATA_DIR, 'numbers_dataset_v2.txt')
        self.folder_path = os.path.join(DATA_DIR, 'table_v2')
        self.out_path = os.path.join(DATA_DIR, 'numbers_dataset_v2.out.{}.txt'.format(get_current_time_str()))
        create_file(self.out_path)

    def parse_urls(self):
        """
        解析urls
        """
        data_lines = read_file(self.file_path)

        data_dict = collections.defaultdict(dict)
        for data_line in data_lines:
            # print('[Info] data_line: {}'.format(data_line))
            items = data_line.split("/")
            image_name = items[-1]
            folder_name = items[-2]
            # image_name = image_name.split('.')[0].split("_")[-1]
            image_name = urllib.parse.unquote(image_name)
            data_dict[folder_name][image_name] = data_line

        img_name_dict = dict()
        for data_line in data_lines:
            items = data_line.split("/")
            image_name = items[-1]
            image_name = urllib.parse.unquote(image_name)
            if image_name in img_name_dict.keys():
                img_name_dict[image_name] = ""
            else:
                img_name_dict[image_name] = data_line

        return data_dict, img_name_dict

    def parse_img_name(self, img_name):
        img_name = img_name.split('.')[0].split("_")[-1]
        img_name = img_name.split(' ')[-1]
        img_name = img_name.replace("jpg", '')
        return img_name

    def read_file_ex(self, path):
        data_list = []
        try:
            data_list = read_excel_file(path)
            out_list = []
            for data_line in data_list:
                try:
                    label_str, img_name = data_line[:2]
                    # img_name = self.parse_img_name(img_name)
                    out_list.append([label_str, img_name])
                except Exception as e:
                    continue
            data_list = out_list
        except Exception as e:
            try:
                data_lines = read_file(path)
                for data_line in data_lines:
                    label_str = data_line.split(",")[0]
                    img_name = data_line.split(",")[1]
                    # img_name = self.parse_img_name(img_name)
                    data_list.append([label_str, img_name])
            except Exception as e:
                pass
        print('[Info] 文件数: {}'.format(len(data_list)))
        return data_list

    def type_format(self, a):
        try:
            a = [str(a), str(int(a))][int(a) == a]
        except Exception as e:
            pass
        return a

    def process(self):
        """
        处理脚本
        """
        data_dict, image_name_dict = self.parse_urls()
        paths_list, names_list = traverse_dir_files(self.folder_path)
        # paths_list = [paths_list[68]]

        for path_idx, path in enumerate(paths_list):
            print('-' * 100)
            data_lines = self.read_file_ex(path)
            print('[Info] path_idx: {}, path: {}'.format(path_idx, path))
            folder_name = path.split("/")[-1].split(".")[-2]
            folder_name = folder_name.replace("csv", "")
            print('[Info] folder_name: {}'.format(folder_name))
            # if folder_name in ["1250", "num_and_op_13_1_0", "1381", "1425"]:
            #     continue
            group_dict = data_dict[folder_name]
            num_error = 0
            num_empty = 0
            for idx, data_list in enumerate(data_lines):
                if idx == 0:
                    continue
                label_str = self.type_format(data_list[0])
                img_name = data_list[1]
                if not img_name:
                    num_empty += 1
                    continue
                img_url = ""
                if group_dict and img_name in group_dict.keys():
                    img_url = image_name_dict[img_name]
                else:
                    if img_name in image_name_dict.keys():
                        img_url = image_name_dict[img_name]
                    else:
                        # print('[Error] data_line: {}'.format(data_list))
                        num_error += 1
                        # if num_error > 10:
                        #     raise Exception("error: {}".format(folder_name))
                if img_url:
                    write_line(self.out_path, '<sep>'.join([label_str, img_url]))

            print('[Info] folder_name: {}, 正确率: {}'.format(
                folder_name, safe_div(len(data_lines) - num_error, len(data_lines))))


def main():
    dg = DataGenerator()
    dg.process()


if __name__ == '__main__':
    main()
