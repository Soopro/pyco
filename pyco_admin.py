# coding=utf-8

from flask import Flask, current_app, request, make_response, g
from loaders import load_config

app = Flask(__name__)

load_config(app)

if __name__ == '__main__':
    app.run(debug=True, host=host, port=9009, threaded=True)
