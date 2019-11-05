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
from utils.misc import hmac_sha, now
from utils.files import unzip, zipdir, clean_dirs

from admin.decorators import login_required


blueprint = Blueprint('preference', __name__, template_folder='pages')


@blueprint.route('/site')
@login_required
def site():

    return render_template('site.html')


@blueprint.route('/site', methods=['POST'])
@login_required
def update_site():
    flash('SAVED')
    return_url = url_for('.site')
    return redirect(return_url)


@blueprint.route('/site/adv', methods=['POST'])
@login_required
def update_site_adv():
    flash('SAVED')
    return_url = url_for('.site')
    return redirect(return_url)


@blueprint.route('/site/menu', methods=['POST'])
@login_required
def update_site_menu():
    flash('SAVED')
    return_url = url_for('.site')
    return redirect(return_url)


@blueprint.route('/configuration')
@login_required
def configuration():
    return render_template('configuration.html')


@blueprint.route('/configuration', methods=['POST'])
@login_required
def update_configure():
    locale = request.form.get('locale', 'en_US')
    print('-----------------------------', locale)
    configure = g.configure
    configure['locale'] = locale
    configure.save()
    flash('SAVED')
    return_url = url_for('.configuration')
    return redirect(return_url)


@blueprint.route('/configuration/passcode', methods=['POST'])
@login_required
def change_passcode():
    old_passcode = request.form.get('old_passcode')
    passcode = request.form.get('passcode')
    passcode2 = request.form.get('passcode2')

    configure = g.configure

    if not check_password_hash(configure['passcode_hash'], old_passcode):
        flash('WRONG_PASSCODE', 'danger')
    elif passcode != passcode2:
        flash('CONFIRM_PASSCODE_NOT_MATCH', 'danger')
    else:
        configure['passcode_hash'] = generate_password_hash(passcode)
        hmac_key = '{}{}'.format(current_app.secret_key, get_remote_addr())
        session['admin'] = hmac_sha(hmac_key, configure['passcode_hash'])
        configure.save()
        flash('SAVED')

    return_url = url_for('.configuration')
    return redirect(return_url)


@blueprint.route('/backup')
@login_required
def backup_download():
    backups_dir = current_app.config['BACKUPS_DIR']
    content_dir = current_app.db.Document.CONTENT_DIR
    temp_zip_file = 'pyco-backup-{}.zip'.format(now())
    zipdir(os.path.join(backups_dir, temp_zip_file), content_dir)
    return send_from_directory(backups_dir, temp_zip_file,
                               as_attachment=True, cache_timeout=1)


@blueprint.route('/backup', methods=['POST'])
@login_required
def backup_restore():
    f = request.files['file']
    content_dir = current_app.db.Document.CONTENT_DIR
    # cleanup
    clean_dirs(content_dir)
    # unpack files
    unzip(f, content_dir)
    flash('RESTORED')
    return_url = url_for('.configuration')
    return redirect(return_url)
