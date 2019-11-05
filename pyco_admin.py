# coding=utf-8

from flask import Flask, make_response, g
import os

from loaders import load_config

from utils.misc import parse_dateformat
from admin.blueprints import register_admin_blueprints
from models import DBConnection, Configure, Document, Site, Theme

from services.i18n import Translator

import traceback


app = Flask(__name__,
            static_folder='admin/templates/assets',
            static_url_path='/static',
            template_folder='admin/templates')

load_config(app)

app.db = DBConnection()
app.db.register([Configure, Document, Site, Theme])

# register blueprints
register_admin_blueprints(app)


@app.template_filter()
def dateformat(t, to_format='%Y-%m-%d'):
    return parse_dateformat(t, to_format)


# inject before request handlers
@app.before_request
def app_before_request():
    g.configure = app.db.Configure()


# inject context
@app.context_processor
def inject_global_variable():
    configure = g.configure
    # make i18n support
    locale = configure['locale']
    lang_path = os.path.join(app.template_folder, 'languages')
    translator = Translator(configure['locale'], lang_path)

    # site data
    site = app.db.Site()
    return {
        'assets_url': app.static_url_path,
        'base_url': app.config['ADMIN_BASE_URL'],
        'configure': g.configure,
        'locale': locale,
        'lang': locale.split('_')[0],
        '_': translator.gettext,
        '_t': translator.t_gettext,
        'site': site,
    }


# errors
@app.errorhandler(Exception)
def errorhandler(err):
    err_log = '{}\n{}'.format(repr(err), traceback.format_exc())
    err_msg = '<h1>{}</h1><p>{}</p>'.format(repr(err), err_log)
    app.logger.error(err_log)
    return make_response(err_msg, 500)


if __name__ == '__main__':
    host = app.config.get('HOST')
    port = app.config.get('ADMIN_PORT')

    print("-------------------------------------------------------")
    print('Pyco: Admin Panel: {}'.format(port))
    print("-------------------------------------------------------")

    if app.debug:
        print('Pyco is running in DEBUG mode !!!')

    app.run(host=str(host), port=int(port), debug=True, threaded=True)
