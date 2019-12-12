# coding=utf-8

from functools import wraps
from flask import current_app, session, redirect, g

from core.utils.request import get_remote_addr
from core.utils.misc import hmac_sha

from .act import url_as


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        hmac_key = '{}{}'.format(current_app.secret_key, get_remote_addr())
        configure = g.configure
        if not configure.exists() or not session.get('pyco_admin') or \
           session['pyco_admin'] != hmac_sha(hmac_key,
                                             configure['passcode_hash']):
            session.clear()
            return redirect(url_as('dashboard.login'))
        return f(*args, **kwargs)
    return wrapper
