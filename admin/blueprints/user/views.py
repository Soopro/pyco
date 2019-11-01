# coding=utf-8
from __future__ import absolute_import

from flask import (Blueprint,
                   current_app,
                   request,
                   flash,
                   url_for,
                   redirect,
                   render_template)

from utils.model import make_paginator
from utils.misc import parse_int

from admin.decorators import login_required


blueprint = Blueprint('user', __name__, template_folder='pages')


@blueprint.route('/')
@login_required
def index():
    paged = parse_int(request.args.get('paged'), 1, True)
    status = request.args.get('status')

    User = current_app.mongodb.User
    if status is not None:
        status = parse_int(status)
        users = User.find_by_status(status)
    else:
        users = User.find_all()

    p = make_paginator(users, paged, 60)

    prev_url = url_for(request.endpoint,
                       paged=p.previous_page,
                       status=status)
    next_url = url_for(request.endpoint,
                       paged=p.next_page,
                       status=status)

    paginator = {
        'next': next_url if p.has_next else None,
        'prev': prev_url if p.has_previous and p.previous_page else None,
        'paged': p.current_page,
        'start': p.start_index,
        'end': p.end_index,
    }
    return render_template('users.html',
                           users=users,
                           status=status,
                           p=paginator)


@blueprint.route('/<user_id>')
@login_required
def detail(user_id=None):
    User = current_app.mongodb.User

    user = _find_user(user_id)
    allowed_status = [
        {'key': User.STATUS_BEGINNER, 'text': 'Beginner'},
        {'key': User.STATUS_VIP, 'text': 'VIP'},
        {'key': User.STATUS_BANNED, 'text': 'Banned'}
    ]
    records = current_app.mongodb.BookRecord.find_by_uid(user['_id'])
    lend_volumes = current_app.mongodb.\
        BookVolume.find_lend_by_uid(user['_id'])
    pending_volumes = current_app.mongodb.\
        BookVolume.find_pending_by_uid(user['_id'])
    volumes = list(lend_volumes) + list(pending_volumes)
    return render_template('user_detail.html',
                           user=user,
                           records=list(records),
                           volumes=volumes,
                           allowed_status=allowed_status)


@blueprint.route('/<user_id>', methods=['POST'])
@login_required
def update(user_id):
    status = request.form.get('status')
    credit = request.form.get('credit')

    user = _find_user(user_id)
    if credit:
        user['credit'] = parse_int(credit)
    user['status'] = parse_int(status)
    user.save()
    flash('Saved.')
    return_url = url_for('.detail', user_id=user['_id'])
    return redirect(return_url)


@blueprint.route('/<user_id>/remove')
@login_required
def remove(user_id):
    user = _find_user(user_id)
    user.delete()
    return_url = url_for('.index')
    return redirect(return_url)


# helpers
def _find_user(user_id):
    user = current_app.mongodb.User.find_one_by_id(user_id)
    if not user:
        raise Exception('User not found...')
    return user
