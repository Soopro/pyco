# coding=utf-8
from __future__ import absolute_import

from flask import (Blueprint,
                   current_app,
                   session,
                   request,
                   flash,
                   redirect,
                   render_template,
                   g)

from werkzeug.security import generate_password_hash, check_password_hash

from core.utils.request import get_remote_addr
from core.utils.misc import hmac_sha

from admin.decorators import login_required
from admin import act


blueprint = Blueprint('dashboard', __name__, template_folder='templates')


@blueprint.route('/')
@login_required
def index():
    total_count = {
        'content': current_app.db.Document.count(),
        'media': current_app.db.Media.count(),
    }
    contents = current_app.db.Document.find_recent()
    return render_template('dashboard.html',
                           total_count=total_count,
                           recent_contents=contents)


@blueprint.route('/login')
def login():
    configure = g.configure
    if not configure.exists():
        return redirect(act.url_as('.initialize'))
    elif session.get('pyco_admin'):
        return redirect(act.url_as('.index'))
    return render_template('login.html', configure=configure)


@blueprint.route('/login', methods=['POST'])
def exec_login():
    configure = g.configure
    passcode = request.form['passcode']

    if not configure:
        return redirect(act.url_as('.initialize'))
    elif check_password_hash(configure['passcode_hash'], passcode):
        try:
            act.sync_site_by_theme_opts()
        except Exception as e:
            raise Exception('Not installed properly: {}'.format(e))
        hmac_key = '{}{}'.format(current_app.secret_key, get_remote_addr())
        session['pyco_admin'] = hmac_sha(hmac_key, configure['passcode_hash'])
        return redirect(act.url_as('.index'))
    else:
        flash('WRONG_PASSCODE', 'danger')
        return redirect(act.url_as('.login'))


@blueprint.route('/initialize')
def initialize():
    configure = g.configure
    if configure.exists():
        return redirect(act.url_as('.login'))
    return render_template('initialize.html')


@blueprint.route('/initialize', methods=['POST'])
def exec_initialize():
    configure = g.configure
    passcode = request.form['passcode']
    passcode2 = request.form['passcode2']
    if passcode != passcode2:
        flash('CONFIRM_PASSCODE_NOT_MATCH', 'danger')
        return redirect(act.url_as('.initialize'))
    else:
        configure['passcode_hash'] = generate_password_hash(passcode)
        configure.save()
        return redirect(act.url_as('.login'))


@blueprint.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(act.url_as('.login'))
