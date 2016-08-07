# coding=utf8
import os
import re


def gen_base_url(config):
    return config.get("BASE_URL")


def gen_theme_url(config):
    return "{}/{}/{}".format(config.get("BASE_URL"),
                             config.get('STATIC_PATH'),
                             config.get('THEME_NAME'))


def gen_libs_url(config):
    return config.get("LIBS_URL")


def gen_api_baseurl(config):
    return config.get("API_URL")


def gen_id(config, relative_path):
    content_dir = config.get('CONTENT_DIR')
    page_id = relative_path.replace(content_dir + "/", '', 1).lstrip('/')
    return page_id


def gen_page_url(config, relative_path):
    content_dir = config.get('CONTENT_DIR')
    content_ext = config.get('CONTENT_FILE_EXT')
    default_index_slug = config.get("DEFAULT_INDEX_SLUG")

    if relative_path.endswith(content_ext):
        relative_path = os.path.splitext(relative_path)[0]
    front_page_content_path = "{}/{}".format(content_dir,
                                             default_index_slug)
    if relative_path.endswith(front_page_content_path):
        len_index_str = len(default_index_slug)
        relative_path = relative_path[:-len_index_str]

    relative_url = relative_path.replace(content_dir, '', 1)
    url = "{}/{}".format(config.get("BASE_URL"),
                         relative_url.lstrip('/'))
    return url


def gen_page_slug(config, relative_path):
    content_ext = config.get('CONTENT_FILE_EXT')
    if relative_path.endswith(content_ext):
        relative_path = os.path.splitext(relative_path)[0]
    slug = relative_path.split('/')[-1]
    return slug


def gen_excerpt(config, content, opts):
    default_excerpt_length = config.get('DEFAULT_EXCERPT_LENGTH')
    excerpt_length = opts.get('excerpt_length',
                              default_excerpt_length)
    default_excerpt_ellipsis = config.get('DEFAULT_EXCERPT_ELLIPSIS')
    excerpt_ellipsis = opts.get('excerpt_ellipsis',
                                default_excerpt_ellipsis)

    excerpt = re.sub(r'<[^>]*?>', '', content).strip()
    if excerpt:
        excerpt = u" ".join(excerpt.split())
        excerpt = excerpt[0:excerpt_length] + excerpt_ellipsis
    return excerpt