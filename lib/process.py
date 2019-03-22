#!/usr/bin/env python3

"""
Read low-level intermediate files and process them to create high-level intermediate files.
These high-level files include some final output and context for the renderer.
"""

import sys
import os
import argparse
from os.path import join as pjoin
import json
from collections import OrderedDict
from urllib.parse import urljoin
import subprocess

from .common import get_uci_fpath_list, read_json_obj, write_json_obj, get_config
from .graph import Graph


class JsonProcessor:

    class ConfigError(ValueError):
        pass

    def __init__(self, intermediate_dir, config, data, graph):
        self.in_dir = pjoin(intermediate_dir, 'json1')
        self.out_dir = pjoin(intermediate_dir, 'json2')
        self.config = config
        self.data = data
        self.graph = graph

    def get_fpath_for_uci(self, uci2):
        relpath = uci2[1:] + '.json'
        if os.path.sep != '/':
            relpath = relpath.replace('/', os.path.sep)
        return pjoin(self.in_dir, relpath)

    def get_url(self, uci):
        html_path = 'nodes{}.html'.format(uci)
        siteurl = self.config.get('SITEURL')
        if siteurl is not None:
            return urljoin(siteurl + '/', html_path)
        else:
            return html_path

    def get_deps_context(self, d):
        d2 = []
        for i, deps in enumerate(d):
            d3 = []
            for uci2, reason in deps.items():
                try:
                    obj2 = self.data[uci2]
                    # deps2 = obj2['deps']
                    metadata2 = obj2['metadata']
                    try:
                        depth2 = self.graph.get_depth(uci2)
                        topo_order2 = self.graph.get_topo_order(uci2)
                        n_deps, n_rdeps, n_tdeps, n_trdeps = self.graph.get_degrees(uci2)
                    except self.graph.VertexNotFound:
                        depth2 = None
                        topo_order2 = None
                        n_deps, n_rdeps, n_tdeps, n_trdeps = None, None, None, None
                except KeyError:
                    metadata2 = None
                    depth2 = None
                    topo_order2 = None
                    n_deps, n_rdeps, n_tdeps, n_trdeps = None, None, None, None
                d4 = OrderedDict([
                    ('uci', uci2),
                    ('exists', uci2 in self.data),
                    ('reason', reason),
                    ('depth', depth2),
                    ('topo_order', topo_order2),
                    ('n_deps', n_deps),
                    ('n_rdeps', n_rdeps),
                    ('n_tdeps', n_tdeps),
                    ('n_trdeps', n_trdeps),
                    ('metadata', metadata2),
                ])
                d3.append(d4)
            d2.append(d3)
        return d2

    def get_search_obj(self, d, uci, search_sep=' $ '):
        obj = OrderedDict(d['metadata'])
        obj['uci'] = uci
        obj['url'] = self.get_url(uci)
        if self.config.get('SEARCH_FIELDS') is None:
            obj['search'] = search_sep.join(d['metadata'].values())
        return obj

    def get_context(self, d, uci):
        d2 = OrderedDict()
        d2['depth'] = self.graph.get_depth(uci)
        d2['topo_order'] = self.graph.get_topo_order(uci)
        d2['n_deps'], d2['n_rdeps'], d2['n_tdeps'], d2['n_trdeps'] = self.graph.get_degrees(uci)
        d2['metadata'] = d['metadata']
        d2['deps'] = self.get_deps_context(d['deps'])
        d2['rdeps'] = self.get_deps_context([self.graph.get_adj(uci)])[0]
        return d2


def section_id_to_name(s):
    return s.replace('-', ' ').replace('_', ' ').title()


def add_to_index_tree(tree, uci, url, metadata, graph):
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
            n_deps, n_rdeps, n_tdeps, n_trdeps = graph.get_degrees(uci)
            tree[part] = {
                'uci': uci,
                'url': url,
                'depth': graph.get_depth(uci),
                'topo_order': graph.get_topo_order(uci),
                'n_deps': n_deps,
                'n_rdeps': n_rdeps,
                'n_tdeps': n_tdeps,
                'n_trdeps': n_trdeps,
                'metadata': metadata,
            }


def process_all(input_dir, intermediate_dir, output_dir):
    # read data from file
    uci_fpath_list_1 = get_uci_fpath_list(pjoin(intermediate_dir, 'json1'))
    data = OrderedDict()
    graph = Graph()
    for uci, fpath1 in uci_fpath_list_1:
        graph.add_vertex(uci)
        d = read_json_obj(fpath1)
        data[uci] = d

    # add edges to graph and detect broken dependencies
    broken_deps = OrderedDict()
    for uci, d in data.items():
        for deps in d['deps']:
            for uci2, reason in deps.items():
                graph.add_edge(uci2, uci, reason)
                if uci2 not in data:
                    if uci2 not in broken_deps:
                        broken_deps[uci2] = [uci]
                    else:
                        broken_deps[uci2].append(uci)

    with open(pjoin(intermediate_dir, 'graph.dot'), 'w') as fp:
        print('digraph concepdag {', file=fp)
        for uci, d in data.items():
            label = d['metadata'].get('title')
            if label is not None:
                print('"{}" [label="{}"]'.format(uci, label), file=fp)
        for uci, d in data.items():
            for deps in d['deps']:
                for uci2, reason in deps.items():
                    if reason is None:
                        print('"{}" -> "{}"'.format(uci2, uci), file=fp)
                    else:
                        print('"{}" -> "{}" [label="{}"]'.format(uci2, uci, reason), file=fp)
        print('}', file=fp)

    try:
        subprocess.check_call(['dot', '-Tsvg', pjoin(intermediate_dir, 'graph.dot'), '-o',
            pjoin(intermediate_dir, 'graph.svg')])
    except FileNotFoundError:
        print('dot is not installed, not generating graph', file=sys.stderr)

    with open(pjoin(intermediate_dir, 'broken_deps.json'), 'w') as fp:
        json.dump(broken_deps, fp, indent=4)

    # SCCs, toposort and transitive dependencies
    scc_list = graph.scc()
    graph.transitive_closure()
    multi_node_sccs = OrderedDict()
    flat_list = []
    for cci, vlist in enumerate(scc_list):
        if len(vlist) > 1:
            multi_node_sccs[cci] = vlist
        flat_list += vlist
    with open(pjoin(intermediate_dir, 'multi_node_sccs.json'), 'w') as fp:
        json.dump(multi_node_sccs, fp, indent=4)
    with open(pjoin(intermediate_dir, 'toposort.txt'), 'w') as fp:
        for uci in flat_list:
            if uci in data:
                print(uci, file=fp)

    # Make JsonProcessor as per config and data
    config = get_config(input_dir)
    processor = JsonProcessor(intermediate_dir, config, data, graph)

    # create search index, hierarchical index and render context
    search_objs = []
    index_tree = OrderedDict()
    for uci, d in data.items():
        search_objs.append(processor.get_search_obj(d, uci))
        add_to_index_tree(index_tree, uci, processor.get_url(uci), d['metadata'], graph)
        # Write render-context
        fpath2 = pjoin(intermediate_dir, 'json2', uci[1:] + '.json')
        context = processor.get_context(d, uci)
        write_json_obj(context, fpath2, indent=4)

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
