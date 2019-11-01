# coding=utf-8
from __future__ import absolute_import

from functools import wraps
from flask import current_app, session, redirect, url_for, g
from utils.request import get_remote_addr
from utils.misc import hmac_sha


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        hmac_key = u'{}{}'.format(current_app.secret_key, get_remote_addr())
        configure = g.configure
        if not configure or not session.get('admin') or \
           session['admin'] != hmac_sha(hmac_key, configure['passcode_hash']):
            session.clear()
            return redirect(url_for('gate.login'))
        return f(*args, **kwargs)
    return wrapper
