#coding=utf-8
from __future__ import absolute_import

from flask import current_app
from jinja2 import Template

_SLOTS = {}


def config_loaded(config):
    global _SLOTS
    _SLOTS = config.get("SITE", {}).get("slots", {})
    return


def before_render(var, template):
    """ slots json sample
    {
       "slot_key":"...scripts...",
    }
    """

    slots = {}
    for k, v in _SLOTS.iteritems():
        v = _render_ext_slots(v, app_id=var["app_id"],
                                 meta=var["meta"])
        slots[k] = v

    var["slots"] = slots
    return


# helpers
def _render_ext_slots(scripts, **context):
    try:
        template = Template(scripts)
        scripts = template.render(**context)
    except Exception as e:
        scripts = str(e)
    return scripts
