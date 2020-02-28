# coding=utf-8

from flask import current_app, url_for, g
import os

from core.utils.misc import replace_startswith
from core.utils.files import ensure_dirs


def url_as(endpoint, **values):
    admin_base_url = current_app.config.get('ADMIN_BASE_URL', '')
    return '{}{}'.format(admin_base_url, url_for(endpoint, **values))


def sync_site_by_theme_opts():
    theme = current_app.db.Theme(current_app.config['THEME_NAME'])
    site = current_app.db.Site()

    # content types
    site['content_types'] = {k: v.get('title')
                             for k, v in theme.content_types.items()}
    content_type_dirs = [os.path.join(site.content_folder, ctype)
                         for ctype in site['content_types']
                         if ctype != site.STATIC_TYPE]
    ensure_dirs(*content_type_dirs)

    # category
    if theme.category:
        cate_name = theme.category.get('name', '')
        cate_content_types = theme.category.get('conten_types', [])
        if not site['categories'] or not isinstance(site['categories'], dict):
            site['categories'] = {'terms': []}
        site['categories'].update({
            'status': 1,
            'name': str(cate_name),
            'conten_types': [c_type for c_type in cate_content_types
                             if isinstance(c_type, str)]
        })
    else:
        site['categories'].update({'status': 0})

    site.save()


def gen_preview_url(content_type, slug):
    if content_type == current_app.db.Document.STATIC_TYPE:
        if slug == current_app.db.Document.INDEX_SLUG:
            preview_path = '/'
        else:
            preview_path = '/{}'.format(slug)
    else:
        preview_path = '/{}/{}'.format(content_type, slug)
    return '{}{}'.format(current_app.config['BASE_URL'], preview_path)


def get_uploads_url():
    configure = g.configure
    base_url = current_app.config['BASE_URL']
    uploads_url = current_app.config.get('UPLOADS_URL')
    acc_url = configure['acc_url']
    if acc_url:
        if configure['acc_mode'] == 1:
            uploads_url = acc_url
        elif configure['acc_mode'] == 2:
            uploads_url = replace_startswith(uploads_url, base_url, acc_url)
    return uploads_url
