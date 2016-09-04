# coding=utf-8
from __future__ import absolute_import

from flask import Blueprint, current_app

from utils.misc import route_inject
from utils.response import make_json_response

from .routes import urlpatterns


bp_name = "restapi"

blueprint = Blueprint(bp_name, __name__)
route_inject(blueprint, urlpatterns)


@blueprint.before_request
def before_request():
    pass


@blueprint.errorhandler(Exception)
def errorhandler(err):
    current_app.logger.error(err)
    return make_json_response(err, 500)
