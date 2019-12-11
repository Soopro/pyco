# coding=utf-8

from flask import (Blueprint,
                   current_app,
                   session,
                   request,
                   flash,
                   redirect,
                   render_template,
                   send_from_directory,
                   g)

import os

from werkzeug.security import generate_password_hash, check_password_hash
from utils.request import get_remote_addr
from utils.misc import hmac_sha, now, str_eval, process_slug, parse_int
from utils.files import unzip, zipdir, clean_dirs

from admin.decorators import login_required
from admin.helpers import url_as


blueprint = Blueprint('preference', __name__, template_folder='templates')


# site

@blueprint.route('/site')
@login_required
def site():
    return render_template('site.html')


@blueprint.route('/site', methods=['POST'])
@login_required
def update_site():
    locale = request.form.get('locale', '')
    title = request.form.get('title', '')
    description = request.form.get('description', '')
    logo = request.form.get('logo', '')
    favicon = request.form.get('favicon', '')
    copyright = request.form.get('copyright', '')
    license = request.form.get('license', '')

    site = current_app.db.Site()
    site['locale'] = locale
    site['meta']['title'] = title
    site['meta']['description'] = description
    site['meta']['logo'] = logo
    site['meta']['favicon'] = favicon
    site['meta']['copyright'] = copyright
    site['meta']['license'] = license
    site.save()
    flash('SAVED')
    return_url = url_as('.site')
    return redirect(return_url)


@blueprint.route('/site/adv', methods=['POST'])
@login_required
def update_site_adv():
    head_metadata = request.form.get('head_metadata', '')
    socials = request.form.get('socials', '')
    customs = request.form.get('customs', '')
    slots = request.form.get('slots', '')

    site = current_app.db.Site()
    site['meta']['socials'] = str_eval(socials, [])
    site['meta']['head_metadata'] = head_metadata
    site['meta']['custom'] = str_eval(customs, {})
    site['slots'] = str_eval(slots, {})
    site.save()

    flash('SAVED')
    return_url = url_as('.site')
    return redirect(return_url)


@blueprint.route('/site/language', methods=['POST'])
@login_required
def update_site_language():
    keys = request.form.getlist('key')
    names = request.form.getlist('name')
    urls = request.form.getlist('url')

    languages = []
    for idx, key in enumerate(keys):
        if not key:
            continue

        try:
            name = names[idx]
        except Exception as e:
            name = key
        try:
            url = urls[idx]
        except Exception as e:
            url = '#'

        languages.append({
            'key': key,
            'name': name,
            'url': url,
        })

    site = current_app.db.Site()
    site['meta']['languages'] = languages
    site.save()

    flash('SAVED')
    return_url = url_as('.site')
    return redirect(return_url)


@blueprint.route('/site/social-media', methods=['POST'])
@login_required
def update_site_social():
    keys = request.form.getlist('key')
    names = request.form.getlist('name')
    urls = request.form.getlist('url')
    codes = request.form.getlist('code')

    socials = []
    for idx, key in enumerate(keys):
        if not key:
            continue

        try:
            name = names[idx]
        except Exception:
            name = key
        try:
            url = urls[idx]
        except Exception:
            url = '#'
        try:
            code = codes[idx]
        except Exception:
            code = ''

        socials.append({
            'key': key,
            'name': name,
            'url': url,
            'code': code,
        })

    site = current_app.db.Site()
    site['meta']['socials'] = socials
    site.save()

    flash('SAVED')
    return_url = url_as('.site')
    return redirect(return_url)


@blueprint.route('/site/menu/<menu_key>/node', methods=['POST'])
@login_required
def add_site_menu_node(menu_key):
    parent_key = request.args.get('parent_key', '')

    name = request.form.get('name', '')
    link = request.form.get('link', '')
    target = request.form.get('target', '')
    fixed = request.form.get('fixed', '')
    path_scope = request.form.get('path_scope', '')
    css = request.form.get('css', '')
    pos = request.form.get('pos', 0)

    _index = parse_int(pos)

    new_node = {
        'key': process_slug(name),
        'name': name,
        'link': link,
        'target': target,
        'path_scope': path_scope,
        'fixed': bool(fixed),
        'class': css
    }

    site = current_app.db.Site()
    nodes = site['menus'].get(menu_key, [])
    if parent_key:
        parent = _find_parent_node(nodes, parent_key)
        parent['nodes'].insert(_index, new_node)
    else:
        nodes.insert(_index, new_node)

    site.save()
    flash('SAVED')
    return_url = url_as('.site')
    return redirect(return_url)


@blueprint.route('/site/menu/<menu_key>/node/update', methods=['POST'])
@login_required
def update_site_menu_node(menu_key):
    parent_key = request.args.get('parent_key', '')
    node_key = request.args.get('node_key', '')

    name = request.form.get('name', '')
    link = request.form.get('link', '')
    target = request.form.get('target', '')
    fixed = request.form.get('fixed', '')
    path_scope = request.form.get('path_scope', '')
    css = request.form.get('css', '')
    pos = request.form.get('pos', 0)

    _index = parse_int(pos)

    new_node = {
        'key': process_slug(name),
        'name': name,
        'link': link,
        'target': target,
        'path_scope': path_scope,
        'fixed': fixed,
        'class': css
    }

    site = current_app.db.Site()
    nodes = site['menus'].get(menu_key, [])
    if parent_key:
        parent = _find_parent_node(nodes, parent_key)
        node = _find_node(parent['nodes'], node_key)
        new_node.update({
            'meta': node['meta'],
            'nodes': node['nodes']
        })
        parent['nodes'].insert(_index, new_node)
        parent['nodes'].remove(node)
    else:
        node = _find_node(nodes, node_key)
        new_node.update({
            'meta': node['meta'],
            'nodes': node['nodes']
        })
        nodes.remove(node)
        nodes.insert(_index, new_node)
    site.save()
    flash('SAVED')
    return_url = url_as('.site')
    return redirect(return_url)


@blueprint.route('/site/menu/<menu_key>/node/remove')
@login_required
def remove_site_menu_node(menu_key):
    parent_key = request.args.get('parent_key', '')
    node_key = request.args.get('node_key', '')

    site = current_app.db.Site()
    nodes = site['menus'].get(menu_key, [])
    if parent_key:
        parent = _find_parent_node(nodes, parent_key)
        node = _find_node(parent['nodes'], node_key)
        parent['nodes'].remove(node)
    else:
        node = _find_node(nodes, node_key)
        nodes.remove(node)
    site.save()
    flash('REMOVED')
    return_url = url_as('.site')
    return redirect(return_url)


@blueprint.route('/site/menu/<menu_key>', methods=['POST'])
@login_required
def hardcore_site_menu(menu_key):
    hardcore = request.form.get('hardcore', '')

    site = current_app.db.Site()
    site['menus'][menu_key] = str_eval(hardcore, {})
    site.save()
    flash('SAVED')
    return_url = url_as('.site')
    return redirect(return_url)


# appearance

@blueprint.route('/appearance')
@login_required
def appearance():
    return render_template('appearance.html')


@blueprint.route('/appearance', methods=['POST'])
@login_required
def install_theme():
    f = request.files['file']
    theme_dir = current_app.current_theme_dir

    clean_dirs(theme_dir)
    unzip(f, theme_dir)

    _update_site()
    flash('INSTALLED')
    return_url = url_as('.appearance')
    return redirect(return_url)


@blueprint.route('/appearance/reload')
@login_required
def reload_theme():
    _update_site()
    flash('RELOADED')
    return_url = url_as('.appearance')
    return redirect(return_url)


# configuration

@blueprint.route('/configuration')
@login_required
def configuration():
    configure = g.configure
    return render_template('configuration.html', configure=configure)


@blueprint.route('/configuration', methods=['POST'])
@login_required
def update_configure():
    locale = request.form.get('locale', 'en_US')
    configure = g.configure
    configure['locale'] = locale
    configure.save()
    flash('SAVED')
    return_url = url_as('.configuration')
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
        session['pyco_admin'] = hmac_sha(hmac_key, configure['passcode_hash'])
        configure.save()
        flash('SAVED')

    return_url = url_as('.configuration')
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
    return_url = url_as('.configuration')
    return redirect(return_url)


# helpers
def _find_parent_node(nodes, parent_key):
    for node in nodes:
        if parent_key and node.get('key') == parent_key:
            if not isinstance(node.get('nodes'), list):
                node['nodes'] = []
            return node
    raise Exception('Menu item pranet is not found')


def _find_node(nodes, node_key):
    for node in nodes:
        if node_key and node.get('key') == node_key:
            return node
    raise Exception('Menu item is not found')


def _update_site():
    theme = current_app.db.Theme(current_app.current_theme_dir)
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
