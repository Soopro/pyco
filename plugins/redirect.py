#coding=utf-8
from __future__ import absolute_import
import re, os

def single_page_meta(page_meta, redirect_to):
    redirect_to["url"] = page_meta.get("redirect")
    return 