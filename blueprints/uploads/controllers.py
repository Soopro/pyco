# coding=utf-8
from __future__ import absolute_import

from flask import current_app, make_response, send_from_directory
from utils.response import make_cors_headers
import os
import mimetypes


def get_uploads(filepath):
    filename = os.path.basename(filepath)
    try:
        mime_type = mimetypes.guess_type(filename)[0]
    except Exception:
        mime_type = 'text'

    uploads_dir = current_app.config.get("UPLOADS_DIR")
    send_file = send_from_directory(uploads_dir, filepath)
    response = make_response(send_file)
    response.headers = make_cors_headers(mime_type)
    return response
