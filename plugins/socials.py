#coding=utf-8
from __future__ import absolute_import
import gettext
import os
from flask import current_app

_SOCIALS = {}


def config_loaded(config):
    global _SOCIALS
    site_meta = config.get("SITE", {}).get("meta", {})
    _SOCIALS = site_meta.pop("socials", None)
    return


def before_render(var, template):
    """ socials json sample
    {
       "facebook":{
           "name":"Facebook",
           "code":"..."
       },
       "twitter":{
           "name":"Twitter",
           "code":"..."
       }
    }
    """
    social_list = []
    socials = _SOCIALS
    
    if socials:
        # directly append if is list
        if isinstance(socials, list):
            for social in socials:
                if social.get('key'):
                    social_list.append(social)

        # change to list if is dict
        if isinstance(socials, dict):
            for social in socials:
                tmp_social = socials[social]
                tmp_social.update({"key": social})
                social_list.append(tmp_social)

    var["socials"] = social_list
    return