# coding=utf-8

from flask import Blueprint, current_app
import traceback

from core.utils.misc import route_inject
from core.utils.response import make_json_response

from .routes import urlpatterns


bp_name = 'restapi'

blueprint = Blueprint(bp_name, __name__)
route_inject(blueprint, urlpatterns)


@blueprint.before_request
def before_request():
    pass


@blueprint.errorhandler(Exception)
def errorhandler(err):
    err_log = '{}\n{}'.format(repr(err), traceback.format_exc())
    current_app.logger.error(err_log)
    err = {
        'errmsg': repr(err)
    }
    return make_json_response(err, 500)
