#!/usr/bin/env python3

import os
from os.path import join as pjoin
import argparse

from lib import parse, process, render, common

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_THEME_DIR = pjoin(BASE_DIR, 'theme')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input_dir')
    parser.add_argument('intermediate_dir')
    parser.add_argument('output_dir')
    parser.add_argument('--theme', default=DEFAULT_THEME_DIR)
    parser.add_argument('--debug', action='store_true', default=False)
    args = parser.parse_args()

    common.debug = args.debug

    config = common.get_config(args.input_dir, args.intermediate_dir)
    print('Action: parse')
    parse.process_all(args.input_dir, args.intermediate_dir, config)
    print('Action: process')
    process.process_all(args.input_dir, args.intermediate_dir, args.output_dir, config)
    print('Action: render')
    render.render_all(args.theme, args.input_dir, args.intermediate_dir,
        args.output_dir, config)
    common.write_timestamp(args.intermediate_dir, config['THIS_RUN_TIME'])


if __name__ == '__main__':
    main()
