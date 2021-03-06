#!/usr/bin/env python3

from os.path import join as pjoin
import shutil

from jinja2 import Environment, FileSystemLoader, select_autoescape
from .common import (
    read_json_obj, write_string_to_file, get_uci_fpath_list,
    get_relative_site_url_from_uci,
    )


def get_jinja_env(templates_dir):
    return Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape([]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def get_context(config, pages_dir=None, d=None, uci=None):
    context = config.copy()
    if config.get('SITEURL') is None:
        if uci is None:
            context['SITEURL'] = '.'
        else:
            context['SITEURL'] = get_relative_site_url_from_uci(uci)

    if d is not None:
        for k, v in d.items():
            context[k] = v
        if uci is not None and pages_dir is not None:
            doc_path = pjoin(pages_dir, uci[1:] + '.html')
            try:
                with open(doc_path) as fp:
                    context['document'] = fp.read()
            except FileNotFoundError:
                context['document'] = None
    context['uci'] = uci
    return context


def render_all(theme_dir, input_dir, intermediate_dir, output_dir, config,
        some_json_changed, modified_ucis):
    jinja_env = get_jinja_env(pjoin(theme_dir, 'templates'))

    # render nodes
    uci_fpath_list = get_uci_fpath_list(pjoin(intermediate_dir, 'json2'))
    pages_dir = pjoin(intermediate_dir, 'pages')
    template = jinja_env.get_template('node.html')
    for uci, fpath in uci_fpath_list:
        if some_json_changed or uci in modified_ucis:
            d = read_json_obj(fpath)
            context = get_context(config, pages_dir, d, uci)
            rendered = template.render(**context)
            output_fpath = pjoin(output_dir, 'nodes', uci[1:] + '.html')
            write_string_to_file(rendered, output_fpath)

    # render index and search
    context = get_context(config)
    index_tree_path = pjoin(intermediate_dir, 'index.json')
    context['index_tree'] = read_json_obj(index_tree_path)
    for fname in ('index.html', 'search.html', 'about.html'):
        template = jinja_env.get_template(fname)
        s = template.render(**context)
        output_fpath = pjoin(output_dir, fname)
        write_string_to_file(s, output_fpath)

    # copy static assets
    if 'dot' not in config['DISABLE']:
        shutil.copyfile(pjoin(intermediate_dir, 'graph.svg'), pjoin(output_dir, 'graph.svg'))

    # copy theme
    input_dirpath = pjoin(theme_dir, 'static')
    output_dirpath = pjoin(output_dir, 'theme')
    try:
        shutil.rmtree(output_dirpath)
    except FileNotFoundError:
        pass
    shutil.copytree(input_dirpath, output_dirpath)
