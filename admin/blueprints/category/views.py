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


blueprint = Blueprint('category', __name__, template_folder='templates')


@blueprint.route('/')
@login_required
def index(content_type):
    return render_template('category.html')


@blueprint.route('/<term_key>')
@login_required
def term(term_key):
    return render_template('term.html')


@blueprint.route('/<term_key>', methods=['POST'])
@login_required
def update_term(term_key):
    name = request.form.get('name', '')

    flash('SAVED')
    return_url = url_for('.term')
    return redirect(return_url)


@blueprint.route('/<term_key>/remove')
@login_required
def remove(content_type, slug):
    flash('REMOVED')
    return_url = url_for('.index')
    return redirect(return_url)


# helpers
