import json5

def traverse_convert(cfg):
    if isinstance(cfg, dict):
        return Config(cfg)
    if isinstance(cfg, list) or isinstance(cfg, tuple):
        return type(cfg)([traverse_convert(value) for value in cfg])
    return cfg

def consume_dots(config, key, create_default):
    holden_keys = key.split('.', 1)
    holden_key = holden_keys[0]

    if not dict.__contains__(config, holden_key):
        if create_default:
            dict.__setitem__(config, holden_key, Config())
        else:
            raise KeyError('%s not exists' % str(key))

    if len(holden_keys) == 1:
        return config, holden_key
    else:
        sub_config = dict.__getitem__(config, holden_key)
        return consume_dots(sub_config, holden_keys[1], create_default)
class Config(dict):

    def __init__(self, *args, **kwargs):
        super(Config, self).__init__()
        self.__assign__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return Config(self, *args, **kwargs)

    def __assign__(self, *args, **kwargs):
        for arg in args:
            if isinstance(arg, str):
                jd = json5.load(open(arg))
                self.__assign_from_dict__(jd, traverse = True)
            elif isinstance(arg, dict):
                self.__assign_from_dict__(arg, traverse = True)
            else:
                raise TypeError('arg should be an instance of <str> or <dict>')
        if kwargs:
            self.__assign_from_dict__(kwargs, traverse = False)
        return self

    def __assign_from_dict__(self, d, traverse):
        for key, value in d.items():
            assert key != '', 'empty key is not allowed'
            holder_cfg, holden_key = consume_dots(self, key, create_default = True)
            if traverse: value = traverse_convert(value)
            holder_cfg[holden_key] = value

    def parse_args(self, args = None):
        if args is None:
            import sys
            args = sys.argv[1:]
        index = 0
        while index < len(args):
            arg = args[index]
            assert arg.startswith('--'), 'arg should starts with "--"'
            assert len(arg) > 2, 'requires len(arg) > 2'
            assert arg[2] != '-', 'requires arg[2] != "-"'
            arg = arg[2:]
            if '=' in arg:
                key, value = arg.split('=')
                index += 1
            else:
                assert len(args) > index + 1, 'incomplete command line arguments'
                key = arg
                value = args[index + 1]
                index += 2
            assert key in self, '%s not exists in config' % key
            value_type = type(self[key])
            self[key] = value_type(value)

    # access by '.' -> access by '[]'

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        del self[key]

    # access by '[]'

    def __getitem__(self, key):
        holder_cfg, holden_key = consume_dots(self, key, create_default = False)
        return dict.__getitem__(holder_cfg, holden_key)

    def __setitem__(self, key, value):
        holder_cfg, holden_key = consume_dots(self, key, create_default = True)
        dict.__setitem__(holder_cfg, holden_key, value)

    def __delitem__(self, key):
        holder_cfg, holden_key = consume_dots(self, key, create_default = False)
        dict.__delitem__(holder_cfg, holden_key)
        #del self.__dict__[key]

    # access by 'in'

    def __contains__(self, key):
        try:
            holder_cfg, holden_key = consume_dots(self, key, create_default = False)
        except KeyError:
            return False
        return True

    # traverse

    def traverse(self, mode, prefix = []):
        for key, value in self.items():
            full_key = '.'.join(prefix + [key])
            yield { 'key': full_key, 'value': value, 'item': (full_key, value) }[mode]
            if type(value) == Config:
                for kv in value.traverse(mode, prefix + [key]):
                    yield kv

    def traverse_keys(self):
        for key in self.traverse('key'):
            yield key

    def traverse_values(self):
        for value in self.traverse('value'):
            yield value

    def traverse_items(self):
        for key, value in self.traverse('item'):
            yield key, value
