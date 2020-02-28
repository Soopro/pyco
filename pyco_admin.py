# coding=utf-8

from flask import Flask, make_response, g
import traceback
import os

from core.loaders import load_config, load_modal_pretreat
from core.utils.misc import parse_dateformat
from core.models import DBConnection, Configure, Document, Site, Theme, Media
from core.services.i18n import Translator

from admin.blueprints import register_admin_blueprints
from admin import act

import info


app = Flask(__name__,
            static_folder='admin/templates/assets',
            static_url_path='/static',
            template_folder='admin/templates')

app.version = info.__version__

load_config(app)

app.db = DBConnection(app.config['PAYLOAD_DIR'], load_modal_pretreat(app))
app.db.register([Configure, Document, Site, Theme, Media])

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
    # theme config
    theme = app.db.Theme(app.config['THEME_NAME'])
    theme_lang_path = os.path.join(theme.theme_folder, 'languages')
    translator.append(theme_lang_path)
    return {
        'static_url': '{}{}'.format(app.config['ADMIN_BASE_URL'],
                                    app.static_url_path),
        'base_url': app.config['BASE_URL'],
        'theme_url': app.config['THEME_URL'],
        'uploads_url': app.config['UPLOADS_URL'],
        'locale': locale,
        'lang': locale.split('_')[0],
        '_': translator.gettext,
        'site': site,
        'theme': theme,
        'url_as': act.url_as,
        'ver': app.version
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
    debug = app.config.get('DEBUG')

    print("-------------------------------------------------------")
    print('Pyco: Admin Panel: {}'.format(port))
    print("-------------------------------------------------------")

    if app.debug:
        print('Pyco is running in DEBUG mode !!!')

    app.run(host=str(host), port=int(port), debug=bool(debug), threaded=True)
