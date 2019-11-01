# coding=utf-8
from __future__ import absolute_import

from flask import (Blueprint,
                   current_app,
                   request,
                   flash,
                   url_for,
                   redirect,
                   render_template)

from utils.misc import slug_uuid_suffix, process_slug

from admin.decorators import login_required

import json


blueprint = Blueprint('notify', __name__, template_folder='pages')


@blueprint.route('/')
@login_required
def index():
    notifies = current_app.mongodb.Notify.find_all()
    return render_template('notifies.html', notifies=notifies)


@blueprint.route('/<notify_id>')
@login_required
def detail(notify_id=None):
    notify = _find_notify(notify_id)
    return render_template('notify_detail.html', notify=notify)


@blueprint.route('/<notify_id>', methods=['POST'])
@login_required
def update(notify_id):
    slug = request.form['slug']
    template_id = request.form.get('template_id')
    source = request.form.get('source')
    params = request.form.get('params')

    notify = _find_notify(notify_id)
    notify['slug'] = _uniqueify_notify_slug(slug, notify)
    notify['template_id'] = template_id
    notify['source'] = source
    try:
        notify['params'] = json.loads(params)
    except Exception:
        pass
    notify.save()
    flash('Saved.')
    return_url = url_for('.detail', notify_id=notify['_id'])
    return redirect(return_url)


@blueprint.route('/<notify_id>/remove')
@login_required
def remove(notify_id):
    notify = _find_notify(notify_id)
    notify.delete()
    return_url = url_for('.index')
    return redirect(return_url)


@blueprint.route('/create', methods=['POST'])
@login_required
def create():
    slug = request.form['slug']

    notify = current_app.mongodb.Notify()
    notify['slug'] = _uniqueify_notify_slug(slug)
    notify.save()
    flash('Created.')
    return_url = url_for('.detail', notify_id=notify['_id'])
    return redirect(return_url)


# helpers
def _find_notify(notify_id):
    notify = current_app.mongodb.Notify.find_one_by_id(notify_id)
    if not notify:
        raise Exception('Notify not found...')
    return notify


def _uniqueify_notify_slug(slug, notify=None):
    slug = process_slug(slug)
    if notify and slug == notify['slug']:
        # don't process if it self.
        return slug

    _book = current_app.mongodb.Notify.find_one_by_slug(slug)
    if _book is not None:
        slug = slug_uuid_suffix(slug)
        slug = _uniqueify_notify_slug(slug, notify)

    return slug
