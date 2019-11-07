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
    return render_template('mediafiles.html',
                           mediafiles=mediafiles,
                           p=paginator)


@blueprint.route('/upload', methods=['POST'])
@login_required
def upload():
    files = request.files.getlist('files')
    uploads_dir = current_app.db.Media.UPLOADS_DIR
    uploaded_files = []
    upload_fails = []
    for file in files[:60]:
        file_path = os.path.join(uploads_dir, file.filename)
        if os.path.isfile(file_path):
            upload_fails.append(file.filename)
        else:
            file.save(file_path)
            uploaded_files.append(file.filename)
    for f in uploaded_files:
        flash('UPLOADED: {}'.format(f))
    for f in upload_fails:
        flash('EXISTS: {}'.format(f), 'warning')
    return redirect(request.referrer)


@blueprint.route('/<filename>/remove')
@login_required
def remove(filename):
    media = current_app.db.Media.find_one(filename)
    media.delete()
    flash('REMOVED')
    return redirect(request.referrer)
