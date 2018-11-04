#!/usr/bin/env python3

import argparse
import json
import os
from os.path import join as pjoin
from collections import OrderedDict
from collections.abc import Mapping, Sequence
from urllib.parse import urljoin

from markdown import Markdown
from .common import (
    read_json_obj, write_json_obj, write_string_to_file, get_uci_fpath_list,
    get_relative_site_url_from_uci
    )
from .tex_md_escape import tex_md_escape


def jsonpath_to_string(jsonpath):
    return ''.join(['[{}]'.format(repr(x)) for x in jsonpath])


global_markdown = None
KNOWN_FORMATS = ('html', 'txt', 'raw', 'tex', 'md', 'mdonly')


def get_markdown_instance():
    global global_markdown
    if global_markdown is None:
        global_markdown = Markdown()
    return global_markdown


def convert_to_html(text, format):
    if format in ('html', 'txt', 'raw'):
        return text
    elif format is None or format in ('tex', 'md'):
        text2 = tex_md_escape(text)
        return get_markdown_instance().convert(text2)
    elif format == 'mdonly':
        return get_markdown_instance().convert(text)


def headingify(text, level):
    return '<h{level}>{text}</h{level}>'.format(text=text, level=level)


def linkify(text, url):
    return '<a href="{url}">{text}</a>'.format(url=url, text=text)


class InputJsonParser:
    def __init__(self, project_dir, uci, siteurl=None):
        # siteurl should end with a slash if it contains a subdirectory
        self.project_dir = project_dir
        self.uci = uci
        self.includes_dir = pjoin(project_dir, 'input', 'includes')
        self.siteurl = siteurl
        if siteurl is None:
            self.siteurl2 = get_relative_site_url_from_uci(self.uci)
            self.url = ''
        else:
            self.url = urljoin(siteurl, 'nodes' + uci)

    def convert_absolute_url(self, url):
        if self.siteurl is not None:
            return urljoin(self.siteurl, url[1:])
        else:
            return self.siteurl2 + url

    class ParseError(ValueError):
        def __init__(self, *args, uci, jsonpath):
            self.args = args
            self.uci = uci
            self.jsonpath = jsonpath

        def __str__(self):
            parts = []
            s = jsonpath_to_string(self.jsonpath)
            if self.uci is not None:
                parts.append(self.uci + s)
            elif self.jsonpath:
                parts.append(s)
            parts.extend(self.args)
            return ': '.join(parts)

    class ParseTypeError(ParseError):
        pass

    def parse_path(self, s, jsonpath):
        if not isinstance(s, str):
            raise self.ParseError('parse_path', 'path should be a string',
                uci=self.uci, jsonpath=jsonpath)
        if not s.startswith('/'):
            raise self.ParseError('parse_path', 'relative paths are not supported', s,
                uci=self.uci, jsonpath=jsonpath)
        elif '//' in s:
            raise self.ParseError('parse_path', 'found // in path', s,
                uci=self.uci, jsonpath=jsonpath)
        else:
            return s

    def parse_deps_mapping(self, d, jsonpath):
        if not isinstance(d, Mapping):
            raise self.ParseError('parse_deps_mapping', 'not a mapping',
                uci=self.uci, jsonpath=jsonpath)
        d2 = OrderedDict()
        for k, v in d.items():
            if not(v is None or isinstance(v, str)):
                raise self.ParseError('parse_deps_mapping', 'not a string or null',
                    uci=self.uci, jsonpath=jsonpath + (k,))
            else:
                d2[self.parse_path(k, jsonpath=jsonpath)] = v
        return d2

    def parse_deps(self, d, jsonpath):
        if not d:
            return []
        if isinstance(d, Mapping):
            d3 = self.parse_deps_mapping(d, jsonpath=jsonpath)
            return [d3] if d3 else []
        elif isinstance(d, Sequence):
            num_strings = sum([isinstance(x, str) for x in d if x])
            num_mappings = sum([isinstance(x, Mapping) for x in d if x])
            num_nonempty = sum([bool(x) for x in d])
            d2 = []
            if num_strings == num_nonempty:
                d3 = OrderedDict([(x, None) for x in d if x])
                d2.append(d3)
            elif num_mappings == num_nonempty:
                for i, x in enumerate(d):
                    if x:
                        d3 = self.parse_deps_mapping(x, jsonpath=jsonpath + (i,))
                        if d3:
                            d2.append(d3)
            else:
                raise self.ParseError('parse_deps', 'list has items of invalid type',
                    uci=self.uci, jsonpath=jsonpath)
            return d2
        else:
            self.ParseError('parse_deps', 'not a list, mapping or null',
                uci=self.uci, jsonpath=jsonpath)

    def parse_document_section(self, d, metadata, jsonpath):
        if not isinstance(d, Mapping):
            raise self.ParseError('parse_document_section', 'not a mapping',
                uci=self.uci, jsonpath=jsonpath)

        format = d.get('format')
        title = d.get('title')
        lines = []
        if title:
            lines.append(headingify(title, 2))
        if 'type' not in d:
            raise self.ParseError('parse_document_section', 'document must have a type',
                uci=self.uci, jsonpath=jsonpath)

        if d['type'] == 'inline':
            try:
                text = d['text']
            except KeyError:
                raise self.ParseError('parse_document_section', 'inline document must have text',
                    uci=self.uci, jsonpath=jsonpath)
            lines.append(convert_to_html(text, format))

        elif d['type'] == 'include':
            try:
                relpath = d['path']
            except KeyError:
                raise self.ParseError('parse_document_section', 'include document must have a path',  # noqa
                    uci=self.uci, jsonpath=jsonpath)
            if format is None:
                base, ext = os.path.splitext(relpath)
                if ext[1:] not in KNOWN_FORMATS:
                    raise self.ParseError('parse_document_section', 'cannot guess file format',
                        uci=self.uci, jsonpath=jsonpath)
                else:
                    format = ext[1:]
            abspath = pjoin(self.includes_dir, relpath[1:])
            with open(abspath) as fobj:
                text = fobj.read()
            lines.append(convert_to_html(text, format))

        elif d['type'] == 'meta':
            try:
                key = d['key']
            except KeyError:
                raise self.ParseError('parse_document_section', 'meta document must have a key',
                    uci=self.uci, jsonpath=jsonpath)
            try:
                text = metadata[key]
            except KeyError:
                raise self.ParseError('parse_document_section',
                    'key {} not found in metadata'.format(repr(key)),
                    uci=self.uci, jsonpath=jsonpath)
            lines.append(convert_to_html(text, format))

        elif d['type'] == 'link':
            try:
                path = d['path']
            except KeyError:
                raise self.ParseError('parse_document_section', 'link must have a path',
                    uci=self.uci, jsonpath=jsonpath)
            if not path.startswith('/'):
                raise self.ParseError('parse_document_section',
                    'link must be relative to site root, and should start with a slash',
                    uci=self.uci, jsonpath=jsonpath)
            path2 = self.convert_absolute_url(path)
            lines.append(linkify(text=path, url=path2))

        return '\n'.join(lines)

    def parse_document(self, d, metadata, jsonpath):
        if d is None:
            return None
        elif isinstance(d, Mapping):
            return self.parse_document_section(d, metadata, jsonpath=jsonpath)
        elif isinstance(d, Sequence):
            d2 = []
            for i, x in enumerate(d):
                d2.append(self.parse_document_section(x, metadata, jsonpath=jsonpath + (i,)))
            return '\n'.join(d2) if d2 else None
        else:
            raise self.ParseError('parse_document', 'not a list, mapping or null',
                uci=self.uci, jsonpath=jsonpath)

    def parse_input(self, d, jsonpath=()):
        if not isinstance(d, Mapping):
            raise self.ParseError('parse_input', 'not a mapping', uci=self.uci, jsonpath=jsonpath)

        d2 = OrderedDict()

        d2['deps'] = self.parse_deps(d.get('deps'), jsonpath=jsonpath + ('deps',))
        d2['metadata'] = d.get('metadata', OrderedDict())
        document = self.parse_document(d.get('document'), d2['metadata'],
            jsonpath=jsonpath + ('document',))

        return (d2, document)


def run_on_all(project_dir, indent=4):
    input_nodes_dir = pjoin(project_dir, 'input', 'nodes')
    int_nodes_dir = pjoin(project_dir, 'intermediate', 'json1')
    pages_dir = pjoin(project_dir, 'intermediate', 'pages')
    uci_input_fpath_list = get_uci_fpath_list(input_nodes_dir)
    for uci, input_fpath in uci_input_fpath_list:
        output_fpath = pjoin(int_nodes_dir, uci[1:] + '.json')
        parser = InputJsonParser(project_dir, uci=uci)
        d = read_json_obj(input_fpath)
        d2, document = parser.parse_input(d)
        write_json_obj(d2, output_fpath, indent=indent)
        output_fpath2 = pjoin(pages_dir, uci[1:] + '.html')
        if document is not None:
            write_string_to_file(document, output_fpath2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('fpath', help='Path to JSON file')
    args = parser.parse_args()

    with open(args.fpath) as fobj:
        d = json.load(fobj, object_pairs_hook=OrderedDict)

    parser = InputJsonParser(None, uci=args.fpath)
    d2, document = parser.parse_input(d)

    print(json.dumps(d2, indent=2))
    print()
    print(document)


if __name__ == '__main__':
    main()