#coding=utf-8
from __future__ import absolute_import

_argments = None
_url = None
    
def request_url(request, redirect_to):
    global _argments, _url
    _argments = {}
    
    for (k,v) in request.args.items():
        _argments.update({k:v})
    _url = request.path
    return

def before_render(var,template):
    var["args"] = _argments
    var["add_args"] = add_args
    return

#custom functions
def add_args(args):
    if args and isinstance(args, dict):
        _argments.update(args)
        url=_url+"?"+"&".join(['%s=%s' % (key, value) for (key, value) in _argments.items()]) 
    return url
