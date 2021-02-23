import os
from os.path import join as pjoin
import json
from collections import OrderedDict


DEFAULT_SITE_NAME = 'ConcepDAG'
debug = False


def get_uci_fpath_list(nodes_dir):
    uci_fpath_list = []
    for dirpath, dirnames, fnames in os.walk(nodes_dir):
        for fname in fnames:
            base, ext = os.path.splitext(fname)
            if ext == '.json':
                fpath = pjoin(dirpath, fname)
                uci = '/' + os.path.relpath(pjoin(dirpath, base), nodes_dir)
                if os.path.sep != '/':
                    uci = uci.replace(os.path.sep, '/')
                uci_fpath_list.append((uci, fpath))
    return uci_fpath_list


def read_json_obj(fpath):
    try:
        with open(fpath) as fobj:
            return json.load(fobj, object_pairs_hook=OrderedDict)
    except json.JSONDecodeError as e:
        raise Exception('could not read json file: ' + fpath) from e


def write_json_obj(obj, fpath, indent=None):
    dirpath = os.path.dirname(fpath)
    os.makedirs(dirpath, exist_ok=True)
    with open(fpath, 'w') as fobj:
        json.dump(obj, fobj, indent=indent)


def write_string_to_file(s, fpath):
    dirpath = os.path.dirname(fpath)
    os.makedirs(dirpath, exist_ok=True)
    with open(fpath, 'w') as fp:
        fp.write(s)


def get_config(input_dir):
    config_json = pjoin(input_dir, 'config.json')
    try:
        config = read_json_obj(config_json)
    except FileNotFoundError:
        config = OrderedDict()
    if config.get('TITLE') is None and config.get('NAME') is not None:
        config['TITLE'] = config.get('NAME')
    if config.get('NAME') is None:
        config['NAME'] = DEFAULT_SITE_NAME
    config['DEBUG'] = debug
    if debug:
        config['SITEURL'] = None
    return config


def get_relative_site_url_from_uci(uci):
    return ('../' * uci.count('/'))[:-1]
