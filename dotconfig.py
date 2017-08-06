import re
import json

class Config(dict):
    def __init__(self, stuff = None, **kwargs):
        super(Config, self).__init__()
        if type(stuff) is str:
            content = ''
            for line in open(stuff):
                content += re.sub('#.*', '', line.strip()) + '\n'
            for key, value in json.loads(content).items():
                if type(value) == dict:
                    value = Config(value)
                self[key] = value
        elif type(stuff) in [Config, dict]:
            for key, value in stuff.items():
                if type(value) in [Config, dict]:
                    value = Config(value)
                self[key] = value
        elif stuff is not None:
            raise TypeError('stuff should be a <str>, <dict>, <Config> or None')
        if kwargs:
            for key, value in kwargs.items():
                if type(value) in [Config, dict]:
                    value = Config(value)
                self[key] = value

    def __setitem__(self, key, value):
        if not key.startswith('!') and self.__contains__('!' + key):
            key = '!' + key
        super(Config, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __getitem__(self, key):
        if self.__contains__('!' + key):
            return super(Config, self).__getitem__('!' + key)
        else:
            return super(Config, self).__getitem__(key)

    def __delitem__(self, key):
        if self.__contains__('!' + key):
            super(Config, self).__delitem__('!' + key)
            del self.__dict__['!' + key]
        else:
            super(Config, self).__delitem__(key)
            del self.__dict__[key]

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        del self[key]

    def items(self):
        for key, value in super(Config, self).items():
            if key.startswith('!'):
                key = key[1:]
            yield key, value

    def __call__(self, __copy__or__inplace__ = True, __overwrite__or__fillup__ = True, **kwargs):
        if __copy__or__inplace__: new_config = Config(self)
        else: new_config = self
        for k, v in kwargs.items():
            if __overwrite__or__fillup__ or k not in new_config:
                new_config[k] = v
            else:
                raise Exception('In fillup mode, key <%s> already exists in config.')
        return new_config

    def copy_overwrite(self, **kwargs):
        return self.__call__(True, True, **kwargs)

    def copy_fillup(self, **kwargs):
        return self.__call__(True, False, **kwargs)

    def inplace_overwrite(self, **kwargs):
        return self.__call__(False, True, **kwargs)

    def inplace_fillup(self, **kwargs):
        return self.__call__(False, False, **kwargs)

    def maybe_get_kwargs(self, *keys):
        kwargs = dict()
        for key in keys:
            if key in self:
                kwargs[key] = self[key]
        return kwargs

    def collect_marked_config(self):
        d = dict()
        for path, value in traverse([], self):
            d[path] = value
        return d

def traverse(prefix, node):
    if type(node) not in [dict, Config]:
        return
    else:
        for key in node.keys():
            if key.startswith('!'):
                path = '.'.join(prefix + [key[1:]])
                value = node[key]
                if type(value) not in [str, int, float, bool]:
                    value = json.dumps(value)
                yield path, value
            else:
                for path, value in traverse(prefix + [key], node[key]):
                    yield path, value
