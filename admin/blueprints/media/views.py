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

from utils.model import make_paginator
from utils.misc import (parse_int,
                        safe_filename,
                        uuid4_hex,
                        parse_dateformat,
                        now)

from admin.decorators import login_required


blueprint = Blueprint('media',
                      __name__,
                      static_folder='static',
                      static_url_path='/static',
                      template_folder='pages')


@blueprint.route('/')
@login_required
def index():
    paged = parse_int(request.args.get('paged'), 1, True)
    mediafiles = current_app.mongodb.Media.find_all()

    p = make_paginator(mediafiles, paged, 60)

    uploads_url = current_app.config.get('UPLOADS_URL')
    mediafiles = list(mediafiles)

    for media in mediafiles:
        media['src'] = u'{}/{}/{}'.format(uploads_url,
                                          media['scope'],
                                          media['key'])

    prev_url = url_for(request.endpoint,
                       paged=p.previous_page)
    next_url = url_for(request.endpoint,
                       paged=p.next_page)

    paginator = {
        'next': next_url if p.has_next else None,
        'prev': prev_url if p.has_previous and p.previous_page else None,
        'paged': p.current_page,
        'start': p.start_index,
        'end': p.end_index,
    }
    return render_template('mediafiles.html',
                           mediafiles=mediafiles,
                           p=paginator)


@blueprint.route('/upload', methods=['POST'])
@login_required
def upload():
    files = request.files.getlist('files')
    for file in files[:12]:
        if not _allowed_file(file.filename):
            flash('{}: file not allowed!'.format(file.filename), 'warning')
            continue

        scope = parse_dateformat(now(), '%Y-%m')
        key = filename = safe_filename(file.filename)
        media = current_app.mongodb.Media.find_one_by_scope_key(scope, key)

        if media:  # rename file if exists.
            fname, ext = os.path.splitext(filename)
            key = filename = u'{}-{}{}'.format(fname, uuid4_hex(), ext)

        media = current_app.mongodb.Media()
        media['scope'] = scope
        media['filename'] = filename
        media['key'] = key
        media['mimetype'] = unicode(file.mimetype)
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


@blueprint.route('/<media_id>/remove')
@login_required
def remove(media_id):
    paged = parse_int(request.args.get('paged'), 1, True)

    media = current_app.mongodb.Media.find_one_by_id(media_id)
    uplaods_dir = current_app.config.get('UPLOADS_FOLDER')
    try:
        os.remove(os.path.join(uplaods_dir, media['scope'], media['key']))
    except Exception:
        pass
    finally:
        media.delete()

    return_url = url_for('.index', paged=paged)
    return redirect(return_url)


# helpers
def _allowed_file(filename):
    file_ext = ''
    allowed_exts = current_app.config.get('ALLOWED_MEDIA_EXTS')
    if '.' in filename:
        file_ext = filename.rsplit('.', 1)[1]
    return file_ext.lower() in allowed_exts
