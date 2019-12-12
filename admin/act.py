# coding=utf-8

from flask import current_app, url_for


def url_as(endpoint, **values):
    admin_base_url = current_app.config.get('ADMIN_BASE_URL', '')
    return '{}{}'.format(admin_base_url, url_for(endpoint, **values))


def sync_site_by_theme_opts():
    theme = current_app.db.Theme(current_app.config['THEME_NAME'])
    site = current_app.db.Site()
    site['content_types'] = {k: v.get('title')
                             for k, v in theme.content_types.items()}
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
