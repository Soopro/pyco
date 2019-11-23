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

from utils.misc import (parse_int, process_slug, str_eval)

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


@blueprint.route('/<content_type>', methods=['POST'])
@login_required
def create_content(content_type):
    title = request.form.get('title')
    content = current_app.db.Document()
    slug = process_slug(title)
    content.add({
        'slug': slug,
        'content_type': content_type,
        'meta': {
            'title': title,
        }
    })
    content.save()
    flash('SAVED')
    return_url = url_for('.content_detail',
                         content_type=content_type,
                         slug=slug)
    return redirect(return_url)


@blueprint.route('/<content_type>/<slug>')
@login_required
def content_detail(content_type, slug):
    curr_content_type = _find_content_type(content_type)
    document = current_app.db.Document.find_one(slug, content_type)
    custom_fields = _find_custom_fields(document.get('template'))
    return render_template('content_detail.html',
                           document=document,
                           meta=document['meta'],
                           content=document['content'],
                           content_type=curr_content_type,
                           custom_fields=custom_fields)


@blueprint.route('/<content_type>/<slug>', methods=['POST'])
@login_required
def update_content(content_type, slug):
    tags = request.form.get('tags', '')
    terms = request.form.get('terms', [])
    date = request.form.get('date', '')
    parent = request.form.get('parent', '')
    template = request.form.get('template', '')
    priority = request.form.get('priority', 0)
    redirect_url = request.form.get('redirect', '')
    status = request.form.get('status', '')

    title = request.form.get('title', '')
    description = request.form.get('description', '')
    featured_img_src = request.form.get('featured_img_src', '')
    content = request.form.get('content', '')
    custom_fields = {key: request.form.get(key, '')
                     for key in _find_custom_fields(template)}

    tags = [tag.strip() for tag in tags.split(',')]
    meta = {k: str_eval(v) for k, v in custom_fields.items()}
    meta.update({
        'title': title,
        'description': description,
        'featured_img': {
            'src': featured_img_src
        }
    })

    document = current_app.db.Document.find_one(slug, content_type)
    document['meta'] = meta
    document['date'] = date
    document['tags'] = tags
    document['terms'] = terms
    document['template'] = template
    document['parent'] = parent
    document['redirect'] = redirect_url
    document['priority'] = parse_int(priority)
    document['status'] = parse_int(status)
    document['content'] = content
    document.save()
    flash('SAVED')
    return_url = url_for('.content_detail',
                         content_type=content_type,
                         slug=slug)
    return redirect(return_url)


@blueprint.route('/<content_type>/<slug>/raw')
@login_required
def content_raw(content_type, slug):
    document = current_app.db.Document.find_one(slug, content_type)
    return render_template('content_raw.html', document=document)


@blueprint.route('/<content_type>/<slug>/raw', methods=['POST'])
@login_required
def hardcore_content(content_type, slug):
    raw = request.form.get('raw', '')

    document = current_app.db.Document.find_one(slug, content_type)
    document.hardcore(raw)
    document.save()
    flash('SAVED')
    return_url = url_for('.content_raw',
                         content_type=content_type,
                         slug=slug)
    return redirect(return_url)


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


def _find_custom_fields(template):
    theme = current_app.db.Theme(current_app.current_theme_dir)
    custom_fields = theme.custom_fields.get(template)
    if isinstance(custom_fields, dict):
        return custom_fields
    else:
        return {}
