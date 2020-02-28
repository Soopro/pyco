# coding=utf-8
from __future__ import absolute_import

from flask import (Blueprint,
                   current_app,
                   request,
                   redirect,
                   flash,
                   jsonify,
                   render_template)
import math

from core.utils.request import get_param
from core.utils.misc import (parse_int, process_slug)

from admin.decorators import login_required
from admin import act


blueprint = Blueprint('content', __name__, template_folder='templates')


@blueprint.route('/<content_type>')
@login_required
def index(content_type):
    paged = parse_int(request.args.get('paged'), 1, 1)

    curr_content_type = _find_content_type(content_type)
    files = current_app.db.Document.find(content_type)

    limit = current_app.db.Media.MAXIMUM_QUERY
    offset = max(limit * (paged - 1), 0)
    total_count = len(files)

    max_pages = max(int(math.ceil(total_count / float(limit))), 1)

    has_next = paged < max_pages
    has_previous = paged > 1

    contents = files[offset:offset + limit]

    for content in contents:
        content.url = act.gen_preview_url(content.content_type, content.slug)

    prev_url = act.url_as(request.endpoint,
                          content_type=content_type,
                          paged=max(paged - 1, 1))
    next_url = act.url_as(request.endpoint,
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
    slug = request.form.get('slug')
    template = request.form.get('template', '')

    content = current_app.db.Document()
    slug = process_slug(slug or title)
    content.add({
        'slug': slug,
        'content_type': content_type,
        'template': template,
        'meta': {
            'title': title,
        }
    })
    content.save()
    return_url = act.url_as('.content_detail',
                            content_type=content_type,
                            slug=content.slug)
    return redirect(return_url)


@blueprint.route('/<content_type>/<slug>')
@login_required
def content_detail(content_type, slug):
    curr_content_type = _find_content_type(content_type)
    document = current_app.db.Document.find_one(slug, content_type)

    template = document.get('template')
    custom_fields = _find_custom_fields(template)
    hidden_field_keys = _find_hidden_field_keys(template)

    document.url = act.gen_preview_url(document.content_type, document.slug)

    # category
    site = current_app.db.Site()
    terms = site.categories.get('terms', [])

    def display_field(key, hidden_fields=hidden_field_keys):
        return key not in hidden_fields

    return render_template('content_detail.html',
                           document=document,
                           meta=document['meta'],
                           content=document['content'],
                           content_type=curr_content_type,
                           custom_fields=custom_fields,
                           display_field=display_field,
                           terms=terms)


@blueprint.route('/<content_type>/<slug>', methods=['POST'])
@login_required
def update_content(content_type, slug):
    meta = get_param('meta', dict, True, default={})
    content = get_param('content', str, default='')

    document = current_app.db.Document.find_one(slug, content_type)
    try:
        _save_document(document, meta, content)
    except Exception as e:
        current_app.logger.error(e)
        raise e

    flash('SAVED')

    return jsonify({'saved': True})


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
    return_url = act.url_as('.content_raw',
                            content_type=content_type,
                            slug=slug)
    return redirect(return_url)


@blueprint.route('/<content_type>/<slug>/remove')
@login_required
def remove(content_type, slug):
    content = current_app.db.Document.find_one(slug, content_type)
    content.delete()
    flash('REMOVED')
    return_url = act.url_as('.index', content_type=content_type)
    return redirect(return_url)


# helpers
def _find_content_type(content_type_slug):
    theme = current_app.db.Theme(current_app.config['THEME_NAME'])
    content_type = theme.content_types.get(content_type_slug)
    if not content_type:
        raise Exception('Content type not exists')
    return content_type


def _find_custom_fields(template):
    theme = current_app.db.Theme(current_app.config['THEME_NAME'])
    custom_fields = theme.custom_fields.get(template)
    if isinstance(custom_fields, dict):
        return custom_fields
    else:
        return {}


def _find_hidden_field_keys(template):
    theme = current_app.db.Theme(current_app.config['THEME_NAME'])
    hidden_field_keys = theme.hidden_fields.get(template)
    if isinstance(hidden_field_keys, list):
        return hidden_field_keys
    else:
        return []


def _save_document(document, meta, content):
    tags = meta.pop('tags', [])
    terms = meta.pop('terms', [])
    date = meta.pop('date', '')
    parent = meta.pop('parent', '')
    template = meta.pop('template', '')
    redirect_url = meta.pop('redirect', '')
    priority = meta.pop('priority', 1)
    status = meta.pop('status')

    title = meta.pop('title', '')
    description = meta.pop('description', '')
    featured_img_src = meta.pop('featured_img', '')

    document['meta'] = {k: v for k, v in meta.items() if k}  # clear no key.
    document['meta'].update({
        'title': title,
        'description': description,
        'featured_img': {
            'src': featured_img_src
        }
    })
    document['date'] = date
    document['tags'] = [tag.strip() for tag in tags
                        if tag and isinstance(tag, str)]
    document['terms'] = [term.strip() for term in terms
                         if term and isinstance(term, str)]
    document['template'] = template
    document['parent'] = parent
    document['redirect'] = redirect_url
    document['priority'] = parse_int(priority, 1)
    document['status'] = parse_int(status)
    document['content'] = content
    document.save()

    return document
