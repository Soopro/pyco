# coding=utf8
import os
import re


def content_not_found_relative_path(config):
    content_ext = config.get('CONTENT_FILE_EXT')
    default_404_slug = config.get('DEFAULT_404_SLUG')
    return ["{}{}".format(default_404_slug, content_ext)]


def content_not_found_full_path(config):
    content_dir = config.get('CONTENT_DIR')
    return os.path.join(content_dir, content_not_found_relative_path)


def content_ignore_files(config):
    base_files = content_not_found_relative_path(config)
    base_files.extend(config.get("IGNORE_FILES"))
    return base_files


def content_splitter(file_content):
    pattern = r"(\n)*/\*(\n)*(?P<meta>(.*\n)*)\*/(?P<content>(.*(\n)?)*)"
    re_pattern = re.compile(pattern)
    m = re_pattern.match(file_content)
    if m is None:
        return "", ""
    return m.group("meta"), m.group("content")