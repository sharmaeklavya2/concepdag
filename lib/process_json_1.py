#!/usr/bin/env python3

import os
import argparse
from os.path import join as pjoin
import json
from collections import OrderedDict
from urllib.parse import urljoin

from .common import get_uci_fpath_list, read_json_obj, write_json_obj


class JsonProcessor:

    class ConfigError(ValueError):
        pass

    def __init__(self, project_dir, uci, config=None):
        self.uci = uci
        self.project_dir = project_dir
        self.in_dir = pjoin(project_dir, 'intermediate', 'json1')
        self.out_dir = pjoin(project_dir, 'intermediate', 'json2')
        self.files_dir = pjoin(project_dir, 'input', 'files')
        self.includes_dir = pjoin(project_dir, 'input', 'includes')
        if config is None:
            self.config_path = pjoin(project_dir, 'input', 'config.json')
            self.config = read_json_obj(self.config_path)
        else:
            self.config = config

    def get_fpath_for_uci(self, uci2):
        return pjoin(self.in_dir, uci2[1:] + '.json')

    def process_deps(self, d):
        d2 = []
        for i, deps in enumerate(d):
            d3 = []
            for uci2, reason in deps.items():
                fpath2 = self.get_fpath_for_uci(uci2)
                try:
                    obj2 = read_json_obj(fpath2)
                    deps2 = obj2['deps']
                    metadata2 = obj2['metadata']
                except FileNotFoundError:
                    deps2, metadata2 = None, None
                d4 = OrderedDict([
                    ('uci', uci2),
                    ('exists', os.path.exists(fpath2)),
                    ('reason', reason),
                    ('deps', deps2),
                    ('metadata', metadata2),
                ])
                d3.append(d4)
            d2.append(d3)
        return d2

    def get_search_obj(self, d, uci):
        try:
            search_fields = self.config['SEARCH_FIELDS']
        except KeyError:
            search_fields = None

        obj = OrderedDict()
        obj['uci'] = uci
        if self.config.get('SITEURL') is not None:
            obj['url'] = urljoin(self.config['SITEURL'], 'nodes{}.html'.format(uci))
        else:
            obj['url'] = './nodes{}.html'.format(uci)

        if search_fields is not None:
            for search_field in search_fields:
                v = d['metadata'].get(search_field)
                if v is not None:
                    obj[search_field] = v
        else:
            obj['search'] = list(d['metadata'].values())
        return obj

    def process(self, d):
        d2 = OrderedDict()
        d2['deps'] = self.process_deps(d['deps'])
        d2['metadata'] = d['metadata']
        return d2


def run_on_all(project_dir):
    json_dir_1 = pjoin(project_dir, 'intermediate', 'json1')
    json_dir_2 = pjoin(project_dir, 'intermediate', 'json2')
    config_path = pjoin(project_dir, 'input', 'config.json')
    config = read_json_obj(config_path)
    search_objs = []
    uci_fpath_list_1 = get_uci_fpath_list(json_dir_1)

    for uci, fpath1 in uci_fpath_list_1:
        fpath2 = pjoin(json_dir_2, uci[1:] + '.json')
        d = read_json_obj(fpath1)
        processor = JsonProcessor(project_dir, uci, config)
        d2 = processor.process(d)
        search_objs.append(processor.get_search_obj(d, uci))
        write_json_obj(d2, fpath2, indent=4)

    search_fields = config.get('SEARCH_FIELDS')
    search_fields = search_fields if search_fields is not None else ['search']
    search_fpath = pjoin(project_dir, 'output', 'searchinfo', 'raw.json')
    write_json_obj({'fields': search_fields, 'corpus': search_objs},
        search_fpath, indent=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project_dir')
    parser.add_argument('fpath', help='Path to JSON file')
    args = parser.parse_args()

    with open(args.fpath) as fobj:
        d = json.load(fobj, object_pairs_hook=OrderedDict)

    processor = JsonProcessor(args.project_dir, uci=args.fpath)
    d2 = processor.process(d)

    print(json.dumps(d2, indent=2))


if __name__ == '__main__':
    main()
