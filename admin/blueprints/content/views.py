# coding=utf-8
from __future__ import absolute_import

from flask import (Blueprint,
                   current_app,
                   request,
                   url_for,
                   redirect,
                   flash,
                   render_template)
import math

from utils.misc import (parse_int, process_slug)

from admin.decorators import login_required


blueprint = Blueprint('content', __name__, template_folder='templates')


@blueprint.route('/<content_type>')
@login_required
def index(content_type):
    paged = parse_int(request.args.get('paged'), 1, True)

    curr_content_type = _find_content_type(content_type)
    files = current_app.db.Document.find(content_type)

    limit = current_app.db.Media.MAXIMUM_QUERY
    offset = max(limit * (paged - 1), 0)
    total_count = len(files)

    max_pages = max(int(math.ceil(total_count / float(limit))), 1)

    has_next = paged < max_pages
    has_previous = paged > 1

    contents = files[offset:offset + limit]

    prev_url = url_for(request.endpoint,
                       content_type=content_type,
                       paged=max(paged - 1, 1))
    next_url = url_for(request.endpoint,
                       content_type=content_type,
                       paged=min(paged + 1, max_pages))

    paginator = {
        'next': next_url if has_next else None,
        'prev': prev_url if has_previous else None,
        'paged': paged,
    }
    return render_template('content_files.html',
                           contents=contents,
                           content_type=curr_content_type,
                           count=total_count,
                           p=paginator)


@blueprint.route('/<content_type>/<slug>')
@login_required
def content_detail(content_type, slug):
    curr_content_type = _find_content_type(content_type)
    content = current_app.db.Document.find_one(slug, content_type)
    return render_template('content_detail.html',
                           content=content,
                           content_type=curr_content_type)


@blueprint.route('/<content_type>/<slug>/remove')
@login_required
def remove(content_type, slug):
    content = current_app.db.Document.find_one(slug, content_type)
    content.delete()
    flash('REMOVED')
    return_url = url_for('.index', content_type=content_type)
    return redirect(return_url)


# helpers
def _find_content_type(content_type_slug):
    theme = current_app.db.Theme(current_app.current_theme_dir)
    content_type = theme.content_types.get(content_type_slug)
    if not content_type:
        raise Exception('Content type not exists')
    return content_type
