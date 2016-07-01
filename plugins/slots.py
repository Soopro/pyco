# coding=utf-8
from __future__ import absolute_import

from jinja2 import Template

_SLOTS = {}


def config_loaded(config):
    global _SLOTS
    _SLOTS = config.get("SITE", {}).get("slots", {})
    return


def before_render(var, template):
    """ slots json sample
    {
       "<slot_key>":"...scripts...",
    }
    """
    app_id = var.get("app_id")
    slots = {}
    for k, v in _SLOTS.iteritems():
        v = _render_ext_slots(v, app_id=app_id)
        slots[k] = v

    var["slot"] = slots
    return


# helpers
def _render_ext_slots(scripts, app_id):
    try:
        template = Template(scripts)
        scripts = template.render(app_id=app_id)
    except Exception as e:
        scripts = str(e)
    return scripts
