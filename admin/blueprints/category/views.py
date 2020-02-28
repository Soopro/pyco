# coding=utf-8

from __future__ import absolute_import

from flask import (Blueprint,
                   current_app,
                   request,
                   redirect,
                   flash,
                   render_template)

from core.utils.misc import (parse_int, process_slug)

from admin.decorators import login_required
from admin import act


blueprint = Blueprint('category', __name__, template_folder='templates')


@blueprint.route('/')
@login_required
def index():
    site = current_app.db.Site()
    categories = {
        'name': site.categories.get('name'),
        'content_types': site.categories.get('content_types'),
        'terms': site.categories.get('terms', []),
        'status': site.categories.get('status', 0),
    }
    return render_template('category.html', categories=categories)


@blueprint.route('/', methods=['POST'])
@login_required
def create_term():
    term_name = request.form.get('name')
    term_key = request.form.get('key')
    site = current_app.db.Site()
    term = site.add_category_term({
        'key': process_slug(term_key or term_name),
        'meta': {
            'name': term_name,
            'caption': '',
            'figure': '',
        },
        'parent': '',
        'priority': 1,
        'status': 0,
    })
    site.save()
    return_url = act.url_as('.term', term_key=term['key'])
    return redirect(return_url)


@blueprint.route('/<term_key>')
@login_required
def term(term_key):
    term = _find_category_term(term_key)
    return render_template('term.html', term=term)


@blueprint.route('/<term_key>', methods=['POST'])
@login_required
def update_term(term_key):
    name = request.form.get('name', '')
    caption = request.form.get('caption', '')
    figure = request.form.get('figure', '')
    parent = request.form.get('parent', '')
    priority = request.form.get('priority', 1)
    status = request.form.get('status', '')

    site = current_app.db.Site()
    site.update_category_term(term_key, {
        'meta': {
            'name': str(name),
            'caption': str(caption),
            'figure': str(figure),
        },
        'parent': str(parent),
        'priority': parse_int(priority, 1),
        'status': parse_int(status),
    })
    site.save()
    flash('SAVED')
    return_url = act.url_as('.index')
    return redirect(return_url)


@blueprint.route('/<term_key>/remove')
@login_required
def remove_term(term_key):
    site = current_app.db.Site()
    site.remove_category_term(term_key)
    site.save()
    flash('REMOVED')
    return_url = act.url_as('.index')
    return redirect(return_url)


# helpers
def _find_category_term(term_key):
    site = current_app.db.Site()
    term = site.get_category_term(term_key)
    if not term:
        raise Exception('Term not found.')
    return term
