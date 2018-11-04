#!/usr/bin/env python3

import os
import argparse
from os.path import join as pjoin
import json
from collections import OrderedDict
from urllib.parse import urljoin

from .common import get_uci_fpath_list, read_json_obj, write_json_obj, get_config


class JsonProcessor:

    class ConfigError(ValueError):
        pass

    def __init__(self, intermediate_dir, config):
        self.in_dir = pjoin(intermediate_dir, 'json1')
        self.out_dir = pjoin(intermediate_dir, 'json2')
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

    def get_url(self, uci):
        html_path = 'nodes{}.html'.format(uci)
        siteurl = self.config.get('SITEURL')
        if siteurl is not None:
            return urljoin(siteurl, html_path)
        else:
            return html_path

    def get_search_obj(self, d, uci):
        try:
            search_fields = self.config['SEARCH_FIELDS']
        except KeyError:
            search_fields = None

        obj = OrderedDict()
        obj['uci'] = uci
        obj['url'] = self.get_url(uci)

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


def section_id_to_name(s):
    return s.replace('-', ' ').replace('_', ' ').title()


def add_to_index_tree(tree, uci, url, metadata):
    uci_parts = uci[1:].split('/')
    for i, part in enumerate(uci_parts):
        if i < len(uci_parts) - 1:
            bpart = section_id_to_name(part)
            if bpart not in tree:
                tree2 = OrderedDict()
                tree[bpart] = tree2
            else:
                tree2 = tree[bpart]
            tree = tree2
        else:
            tree[part] = {'uci': uci, 'url': url, 'metadata': metadata}


def process_all(input_dir, intermediate_dir, output_dir):
    config = get_config(input_dir)
    search_objs = []
    index_tree = OrderedDict()
    uci_fpath_list_1 = get_uci_fpath_list(pjoin(intermediate_dir, 'json1'))

    processor = JsonProcessor(intermediate_dir, config)
    for uci, fpath1 in uci_fpath_list_1:
        fpath2 = pjoin(intermediate_dir, 'json2', uci[1:] + '.json')
        d = read_json_obj(fpath1)
        d2 = processor.process(d)
        search_objs.append(processor.get_search_obj(d, uci))
        add_to_index_tree(index_tree, uci, processor.get_url(uci), d['metadata'])
        write_json_obj(d2, fpath2, indent=4)

    write_json_obj(index_tree, pjoin(intermediate_dir, 'index.json'), indent=4)
    search_fields = config.get('SEARCH_FIELDS')
    search_fields = search_fields if search_fields is not None else ['search']
    search_fpath = pjoin(output_dir, 'searchinfo', 'raw.json')
    write_json_obj({'fields': search_fields, 'corpus': search_objs},
        search_fpath, indent=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('intermediate_dir')
    parser.add_argument('config_path', help='Path to JSON config file')
    parser.add_argument('fpath', help='Path to JSON file')
    args = parser.parse_args()

    with open(args.fpath) as fobj:
        d = json.load(fobj, object_pairs_hook=OrderedDict)

    config = read_json_obj(args.config_path)
    processor = JsonProcessor(args.intermediate_dir, config=config)
    d2 = processor.process(d)

    print(json.dumps(d2, indent=2))


if __name__ == '__main__':
    main()
