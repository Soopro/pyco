#coding=utf-8
from __future__ import absolute_import

from flask import current_app, make_response, redirect, send_from_directory
from flask.views import MethodView

import os, mimetypes



class UploadsView(MethodView):
    def get(self, filepath):
        
        filename = os.path.basename(filepath)

        try:
            mime_type = mimetypes.guess_type(filename)[0]
        except:
            mime_type = 'text'

        headers = dict()
        headers["Content-Type"] = mime_type

        base_set = ["origin", "accept", "content-type", "authorization"]
        headers["Access-Control-Allow-Headers"] = ", ".join(base_set)
        headers_options = "OPTIONS, HEAD, POST, PUT, DELETE"
        headers["Access-Control-Allow-Methods"] = headers_options
        headers["Access-Control-Allow-Origin"] = '*'
        headers["Access-Control-Max-Age"] = 60 * 60 * 24
        
        uploads_dir = current_app.config.get("UPLOADS_DIR")
        send_file = send_from_directory(uploads_dir, filepath)
        response = make_response(send_file)
        response.headers = headers
        return response
