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

from werkzeug.security import generate_password_hash, check_password_hash

from utils.request import get_remote_addr
from utils.misc import hmac_sha

from admin.decorators import login_required


blueprint = Blueprint('dashboard', __name__, template_folder='templates')


@blueprint.route('/')
@login_required
def index():
    configure = g.configure
    return render_template('dashboard.html')


@blueprint.route('/login')
def login():
    configure = g.configure
    if not configure.exists():
        return redirect(url_for('.initialize'))
    elif session.get('admin'):
        return redirect('/')
    return render_template('login.html')


@blueprint.route('/login', methods=['POST'])
def exec_login():
    configure = g.configure
    passcode = request.form['passcode']
    if not configure:
        return redirect(url_for('.initialize'))
    elif check_password_hash(configure['passcode_hash'], passcode):
        hmac_key = '{}{}'.format(current_app.secret_key, get_remote_addr())
        session['admin'] = hmac_sha(hmac_key, configure['passcode_hash'])
        return redirect('/')
    else:
        flash('Wrong passcode!', 'danger')
        return redirect(url_for('.login'))


@blueprint.route('/initialize')
def initialize():
    configure = g.configure
    if configure.exists():
        return redirect(url_for('.login'))
    return render_template('initialize.html')


@blueprint.route('/initialize', methods=['POST'])
def exec_initialize():
    configure = g.configure
    passcode = request.form['passcode']
    passcode2 = request.form['passcode2']
    if passcode != passcode2:
        flash('Setup passcode is not match!', 'danger')
        return redirect(url_for('.initialize'))
    else:
        configure['passcode_hash'] = generate_password_hash(passcode)
        configure.save()
        return redirect(url_for('.login'))


@blueprint.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('.login'))
