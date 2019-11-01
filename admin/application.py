# coding=utf-8
from __future__ import absolute_import

from flask import Flask, make_response, send_from_directory, g
from redis import ConnectionPool, Redis
from mongokit import Connection as MongodbConn

from utils.encoders import Encoder
from utils.files import ensure_dirs
from utils.misc import parse_dateformat

from common_models import (User, Book, BookVolume, BookRecord, Term,
                           Media, Notify, Configuration)

from .blueprints import register_blueprints

from config import config
import envs
import traceback


def create_app(config_name='default'):
    config_name = envs.CONFIG_NAME or config_name

    app = Flask(__name__,
                static_folder='static',
                static_url_path='/static',
                template_folder='templates')

    @app.template_filter()
    def dateformat(t, to_format='%Y-%m-%d'):
        return parse_dateformat(t, to_format)

    # config
    app.config.from_object(config[config_name])
    app.debug = app.config.get('DEBUG')
    app.json_encoder = Encoder
    app.jinja_env.cache = None

    ensure_dirs(
        app.config.get('LOG_FOLDER'),
        app.config.get('TEMPORARY_FOLDER'),
        app.config.get('UPLOADS_FOLDER')
    )

    # database connections
    rds_pool = ConnectionPool(host=app.config.get('REDIS_HOST'),
                              port=app.config.get('REDIS_PORT'),
                              db=app.config.get('REDIS_DB'),
                              password=app.config.get('REDIS_PASSWORD'))
    rds_conn = Redis(connection_pool=rds_pool)

    mongodb_conn = MongodbConn(
        host=app.config.get('MONGODB_HOST'),
        port=app.config.get('MONGODB_PORT'),
        max_pool_size=app.config.get('MONGODB_MAX_POOL_SIZE')
    )
    mongodb = mongodb_conn[app.config.get('MONGODB_DATABASE')]
    mongodb_user = app.config.get('MONGODB_USER')
    mongodb_pwd = app.config.get('MONGODB_PASSWORD')
    if mongodb_user and mongodb_pwd:
        mongodb.authenticate(mongodb_user, mongodb_pwd)

    # register mongokit models
    mongodb_conn.register([User, Book, BookVolume, BookRecord, Term,
                           Media, Notify, Configuration])

    # inject database connections to app object
    app.redis = rds_conn
    app.mongodb_conn = mongodb_conn
    app.mongodb = mongodb

    # register blueprints
    register_blueprints(app)

    # register before request handlers
    @app.before_request
    def app_before_request():
        g.configure = app.mongodb.Configuration.get_conf() or {}

    # uploads
    @app.route('{}/<path:filepath>'.format(app.config['UPLOADS_URL_PATH']))
    def send_file(filepath):
        return send_from_directory(app.config['UPLOADS_FOLDER'], filepath)

    # errors
    @app.errorhandler(Exception)
    def errorhandler(err):
        err_detail = traceback.format_exc()
        err_detail = '<br />'.join(err_detail.split('\n'))
        err_msg = '<h1>{}</h1><br/>{}'.format(repr(err), err_detail)
        app.logger.error(err)
        return make_response(err_msg, 579)

    return app
