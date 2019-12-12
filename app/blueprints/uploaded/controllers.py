# coding=utf-8

from flask import current_app, make_response, send_from_directory
import os
import mimetypes

from core.utils.response import make_cors_headers


def get_uploads(filepath):
    filename = os.path.basename(filepath)
    try:
        mime_type = mimetypes.guess_type(filename)[0]
    except Exception:
        mime_type = 'text'

    uploads_dir = current_app.db.Media.get_dir()
    send_file = send_from_directory(uploads_dir, filepath)
    response = make_response(send_file)
    response.headers = make_cors_headers(mime_type)
    return response
