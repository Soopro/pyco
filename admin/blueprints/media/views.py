# coding=utf-8
from __future__ import absolute_import

from flask import (Blueprint,
                   current_app,
                   request,
                   url_for,
                   redirect,
                   flash,
                   render_template)
import os
import math

from utils.misc import (parse_int,
                        safe_filename,
                        parse_dateformat,
                        uuid4_hex,
                        now)

from admin.decorators import login_required


blueprint = Blueprint('media', __name__, template_folder='templates')


@blueprint.route('/')
@login_required
def index():
    paged = parse_int(request.args.get('paged'), 1, True)

    files = current_app.db.Media.find()

    limit = current_app.db.Media.MAXIMUM_QUERY
    offset = max(limit * (paged - 1), 0)
    total_count = len(files)

    max_pages = max(int(math.ceil(total_count / float(limit))), 1)

    has_next = paged < max_pages
    has_previous = paged > 1

    mediafiles = [f.info for f in files[offset:offset + limit]]

    uploads_url = current_app.config.get('UPLOADS_URL')
    for media in mediafiles:
        media['src'] = '{}/{}'.format(uploads_url, media['filename'])

    prev_url = url_for(request.endpoint, paged=max(paged - 1, 1))
    next_url = url_for(request.endpoint, paged=min(paged + 1, max_pages))

    paginator = {
        'next': next_url if has_next else None,
        'prev': prev_url if has_previous else None,
        'paged': paged,
    }
    print(mediafiles)
    return render_template('mediafiles.html',
                           mediafiles=mediafiles,
                           p=paginator)


@blueprint.route('/upload', methods=['POST'])
@login_required
def upload():
    files = request.files.getlist('files')
    for file in files[:12]:
        scope = parse_dateformat(now(), '%Y-%m')
        key = filename = safe_filename(file.filename)
        media = current_app.mongodb.Media.find_one_by_scope_key(scope, key)

        if media:  # rename file if exists.
            fname, ext = os.path.splitext(filename)
            key = filename = '{}-{}{}'.format(fname, uuid4_hex(), ext)

        media = current_app.mongodb.Media()
        media['scope'] = scope
        media['filename'] = filename
        media['key'] = key
        media['mimetype'] = file.mimetype
        media['size'] = parse_int(file.content_length)
        media.save()

        uplaods_dir = current_app.config.get('UPLOADS_FOLDER')
        uploads_folder = os.path.join(uplaods_dir, scope)
        if not os.path.isdir(uploads_folder):
            try:
                os.makedirs(uploads_folder)
            except Exception:
                pass
        file.save(os.path.join(uploads_folder, key))

    return redirect(request.referrer)


@blueprint.route('/<filename>/remove')
@login_required
def remove(filename):
    media = current_app.db.Media.find_one(filename)
    media.delete()
    flash('REMOVED')
    return redirect(request.referrer)
