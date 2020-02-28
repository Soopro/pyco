# coding=utf-8
from __future__ import absolute_import

from flask import (Blueprint,
                   current_app,
                   request,
                   redirect,
                   flash,
                   render_template)
import os
import math

from core.utils.response import output_json
from core.utils.misc import parse_int, safe_filename

from admin.decorators import login_required
from admin import act


blueprint = Blueprint('media', __name__, template_folder='templates')


@blueprint.route('/')
@login_required
def index():
    paged = parse_int(request.args.get('paged'), 1, 1)

    files = current_app.db.Media.find()
    limit = current_app.db.Media.MAXIMUM_QUERY
    offset = max(limit * (paged - 1), 0)
    total_count = len(files)

    max_pages = max(int(math.ceil(total_count / float(limit))), 1)

    has_next = paged < max_pages
    has_previous = paged > 1

    mediafiles = [f.info for f in files[offset:offset + limit]]

    uploads_url = act.get_uploads_url()
    for media in mediafiles:
        media['src'] = '{}/{}'.format(uploads_url, media['filename'])

    prev_url = act.url_as(request.endpoint, paged=max(paged - 1, 1))
    next_url = act.url_as(request.endpoint, paged=min(paged + 1, max_pages))

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
    uploads_dir = current_app.db.Media.get_dir()
    uploaded_files = []
    upload_fails = []
    for file in files[:60]:
        filename = safe_filename(file.filename)
        file_path = os.path.join(uploads_dir, filename)
        if os.path.isfile(file_path):
            upload_fails.append(file.filename)
        else:
            file.save(file_path)
            uploaded_files.append(file.filename)
    for f in uploaded_files:
        flash('{}'.format(f), 'MEDIA_UPLOADED')
    for f in upload_fails:
        flash('{}'.format(f), 'MEDIA_EXISTS')
    return redirect(request.referrer)


@blueprint.route('/<filename>/remove')
@login_required
def remove(filename):
    media = current_app.db.Media.find_one(filename)
    media.delete()
    flash('REMOVED')
    return redirect(request.referrer)


@blueprint.route('/repository')
@login_required
@output_json
def repository():
    offset = parse_int(request.args.get('offset'), 0)

    files = current_app.db.Media.find_images()
    offset = parse_int(offset, 0)
    limit = current_app.db.Media.MAXIMUM_QUERY

    count = len(files)
    mediafiles = [f.info for f in files[offset:offset + limit]]
    has_more = offset + limit < count

    uploads_url = act.get_uploads_url()
    for media in mediafiles:
        media['src'] = '{}/{}'.format(uploads_url, media['filename'])
        media['_more'] = has_more
        media['_count'] = count

    return mediafiles


@blueprint.route('/repository', methods=['POST'])
@login_required
@output_json
def repository_upload():
    file = request.files.get('file')

    filename = safe_filename(file.filename)
    uploads_dir = current_app.db.Media.get_dir()
    file_path = os.path.join(uploads_dir, filename)
    if os.path.isfile(file_path):
        return {
            'duplicated': True
        }
    else:
        file.save(file_path)

    media = current_app.db.Media.find_one(filename)

    uploads_url = act.get_uploads_url()
    output_media = media.info
    output_media.update({
        'type': output_media['type'],
        'src': '{}/{}'.format(uploads_url, output_media['filename'])
    })
    return output_media
