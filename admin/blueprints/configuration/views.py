# coding=utf-8

from flask import (Blueprint,
                   current_app,
                   session,
                   request,
                   flash,
                   url_for,
                   redirect,
                   render_template,
                   send_from_directory,
                   g)

import os

from werkzeug.security import generate_password_hash, check_password_hash
from utils.request import get_remote_addr
from utils.misc import hmac_sha, parse_int, now
from utils.files import unzip, zipdir, clean_dirs

from admin.decorators import login_required


blueprint = Blueprint('configuration', __name__, template_folder='pages')


@blueprint.route('/')
@login_required
def index():
    return render_template('configuration.html')


@blueprint.route('/', methods=['POST'])
@login_required
def update():
    title = request.form.get('title')
    welcome_msg = request.form.get('welcome_msg', '')
    register_msg = request.form.get('register_msg', '')
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
    if not check_password_hash(configure['passcode_hash'], old_passcode):
        raise Exception('Old passcode is wrong ...')
    elif passcode != passcode2:
        raise Exception('New passcode is not match ...')
    else:
        configure['passcode_hash'] = generate_password_hash(passcode)
        hmac_key = '{}{}'.format(current_app.secret_key, get_remote_addr())
        session['admin'] = hmac_sha(hmac_key, configure['passcode_hash'])
        configure.save()
    flash('Saved.')
    return_url = url_for('.configuration')
    return redirect(return_url)


@blueprint.route('/backup/download')
@login_required
def backup_download():
    backups_dir = current_app.config['BACKUPS_DIR']
    content_dir = current_app.db.Document.CONTENT_DIR
    temp_zip_file = '{}.zip'.format(now())
    zipdir(os.path.join(backups_dir, temp_zip_file), content_dir)
    return send_from_directory(backups_dir, temp_zip_file,
                               as_attachment=True, cache_timeout=1)


@blueprint.route('/backup/restore', methods=['POST'])
@login_required
def backup_restore():
    f = request.files['file']
    content_dir = current_app.db.Document.CONTENT_DIR
    # cleanup
    clean_dirs(content_dir)
    # unpack files
    unzip(f, content_dir)
    return_url = url_for('.index')
    return redirect(return_url)
