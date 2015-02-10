#coding=utf-8
from __future__ import absolute_import
from flask import request, current_app
import math, os


# filters
def filter_thumbnail(pic_url):
    try:
        pic_url = str(pic_url)
    except Exception:
        return pic_url

    static_host = current_app.config.get("STATIC_HOST")
    if static_host not in pic_url:
        return pic_url
    
    UPLOAD_FOLDER = "uploads"
    THUMB_FOLDER = os.path.join(UPLOAD_FOLDER,"thumbnails")
    new_pic_url = pic_url.replace(UPLOAD_FOLDER,THUMB_FOLDER)
    
    return new_pic_url