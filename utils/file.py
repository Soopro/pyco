# coding=utf8
import os


def check_file_exists(file_full_path):
    return os.path.isfile(file_full_path)