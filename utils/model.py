# coding=utf-8

from werkzeug.datastructures import ImmutableDict


def make_dotted_dict(obj):
    if isinstance(obj, dict):
        return DottedImmutableDict(obj)
    elif isinstance(obj, list):
        return [make_dotted_dict(o) for o in obj]
    else:
        return obj


class DottedDict(dict):
    def __init__(self, *args, **kwargs):
        super(DottedDict, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, item):
        try:
            return self.__getitem__(item)
        except KeyError as e:
            raise AttributeError(e.message)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(DottedDict, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(DottedDict, self).__delitem__(key)
        del self.__dict__[key]


class SilentlyStr(str):
    def return_new(*args, **kwargs):
        return SilentlyStr('')

    def silently(*args, **kwargs):
        return ''

    __getattr__ = return_new
    __call__ = return_new
    __str__ = silently


class DottedImmutableDict(ImmutableDict):

    def __getattr__(self, item):
        try:
            v = self.__getitem__(item)
        except KeyError:
            # do not use None, it could be use by a loop.
            # None is not iterable.
            return SilentlyStr()
        if isinstance(v, dict):
            v = DottedImmutableDict(v)
        return v

    def __repr__(self):
        # remove class name when repr.
        return dict(self).__repr__()
