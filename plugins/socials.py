#coding=utf-8
from __future__ import absolute_import
import gettext
import os
from flask import current_app

_SOCIALS = {}


def config_loaded(config):
    global _SOCIALS
    site_meta = config.get("SITE", {}).get("meta", {})
    _SOCIALS = site_meta.get("socials")
    if _SOCIALS:
        del config["SITE"]["meta"]["socials"]
    return


def before_render(var, template):
    """ socials json sample
    {
       "facebook":{
           "name":"Facebook",
           "url":"http://.....",
           "code":"..."
       },
       "twitter":{
           "name":"Twitter",
           "url":"http://.....",
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
                if social.get('type'):
                    social_list.append(social)

        # change to list if is dict
        if isinstance(socials, dict):
            for social in socials:
                tmp_social = socials[social]
                tmp_social.update({"type": social})
                social_list.append(tmp_social)
    else:
        social_list = None

    var["socials"] = social_list
    return