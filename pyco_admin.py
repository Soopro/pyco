# coding=utf-8

from flask import Flask, make_response, g

from loaders import load_config, load_admin_conf

from utils.misc import parse_dateformat
from admin.blueprints import register_admin_blueprints

import traceback


app = Flask(__name__,
            static_folder='admin/templates/assets',
            static_url_path='/static',
            template_folder='admin/templates')

load_config(app)


# register blueprints
register_admin_blueprints(app)


@app.template_filter()
def dateformat(t, to_format='%Y-%m-%d'):
    return parse_dateformat(t, to_format)


# inject before request handlers
@app.before_request
def app_before_request():
    g.configure = load_admin_conf(app)


# inject context
@app.context_processor
def inject_global_variable():
    return {
        'assets_url': app.static_url_path,
        'base_url': app.config['ADMIN_BASE_URL'],
        'configure': g.configure
    }


# errors
@app.errorhandler(Exception)
def errorhandler(err):
    err_detail = traceback.format_exc()
    err_detail = '<br />'.join(err_detail.split('\n'))
    err_msg = '<h1>{}</h1><br/>{}'.format(repr(err), err_detail)
    app.logger.error(err)
    return make_response(err_msg, 579)


if __name__ == '__main__':
    host = app.config.get('HOST')
    port = app.config.get('ADMIN_PORT')

    print("-------------------------------------------------------")
    print('Pyco: Admin Panel: {}'.format(port))
    print("-------------------------------------------------------")

    if app.debug:
        print('Pyco is running in DEBUG mode !!!')

    app.run(host=str(host), port=int(port), debug=True, threaded=True)
