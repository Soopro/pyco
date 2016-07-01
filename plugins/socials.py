# coding=utf-8
from __future__ import absolute_import

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
            social_list = [social for social in socials
                           if social.get('key')]
        # change to list if is dict
        if isinstance(socials, dict):
            def _make_key(k, v):
                v.update({"key": k})
                return v
            social_list = [_make_key(k, v) for k, v in socials.iteritems()]

    var["socials"] = social_list
    return
