# coding=utf-8

from flask import current_app, url_for


def url_as(endpoint, **values):
    admin_base_url = current_app.config.get('ADMIN_BASE_URL', '')
    return '{}{}'.format(admin_base_url, url_for(endpoint, **values))
