# coding=utf8
import os


def check_file_exists(file_full_path):
    return os.path.isfile(file_full_path)


def get_file_path(config, url):
    content_dir = config.get('CONTENT_DIR')
    content_ext = config.get('CONTENT_FILE_EXT')
    default_index_slug = config.get("DEFAULT_INDEX_SLUG")

    base_path = os.path.join(content_dir, url[1:]).rstrip("/")
    file_name = "{}{}".format(base_path, content_ext)
    if check_file_exists(file_name):
        return file_name

    tmp_fname = "{}{}".format(default_index_slug, content_ext)
    file_name = os.path.join(base_path, tmp_fname)
    if check_file_exists(file_name):
        return file_name
    return None