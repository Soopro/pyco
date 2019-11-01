# coding=utf-8
from __future__ import absolute_import

from flask import (Blueprint,
                   current_app,
                   session,
                   request,
                   flash,
                   url_for,
                   redirect,
                   render_template,
                   g)

from utils.auth import generate_hashed_password, check_hashed_password
from utils.request import get_remote_addr
from utils.misc import hmac_sha, parse_int

from admin.decorators import login_required


blueprint = Blueprint('configuration', __name__, template_folder='pages')


@blueprint.route('/')
@login_required
def index():
    configure = g.configure
    configure['mina_app_secret'] = configure.decrypt('mina_app_secret')
    return render_template('configuration.html', configure=configure)


@blueprint.route('/', methods=['POST'])
@login_required
def update():
    title = request.form.get('title')
    welcome_msg = request.form.get('welcome_msg', u'')
    register_msg = request.form.get('register_msg', u'')
    rental_time_limit = request.form.get('rental_time_limit')
    mina_app_id = request.form.get('mina_app_id')
    mina_app_secret = request.form.get('mina_app_secret')

    configure = g.configure
    configure['rental_time_limit'] = parse_int(rental_time_limit, 0, 0)
    configure['meta'].update({
        'title': title,
        'welcome_msg': welcome_msg,
        'register_msg': register_msg
    })
    configure['mina_app_id'] = mina_app_id
    configure.encrypt('mina_app_secret', mina_app_secret)
    configure.save()
    print configure['meta']
    flash('Saved.')
    return_url = url_for('.index')
    return redirect(return_url)


@blueprint.route('/', methods=['POST'])
@login_required
def change_passcode():
    old_passcode = request.form.get('old_passcode')
    passcode = request.form.get('passcode')
    passcode2 = request.form.get('passcode2')

    configure = g.configure
    if not check_hashed_password(configure['passcode_hash'], old_passcode):
        raise Exception('Old passcode is wrong ...')
    elif passcode != passcode2:
        raise Exception('New passcode is not match ...')
    else:
        configure['passcode_hash'] = generate_hashed_password(passcode)
        hmac_key = u'{}{}'.format(current_app.secret_key, get_remote_addr())
        session['admin'] = hmac_sha(hmac_key, configure['passcode_hash'])
        configure.save()
    flash('Saved.')
    return_url = url_for('.configuration')
    return redirect(return_url)
