#!/usr/bin/env python3

import os
from os.path import join as pjoin
import argparse

from lib import parse, process, render

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_THEME_DIR = pjoin(BASE_DIR, 'theme')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input_dir')
    parser.add_argument('intermediate_dir')
    parser.add_argument('output_dir')
    parser.add_argument('--theme', default=DEFAULT_THEME_DIR)
    args = parser.parse_args()

    print('Action: parse')
    parse.process_all(args.input_dir, args.intermediate_dir)
    print('Action: process')
    process.process_all(args.input_dir, args.intermediate_dir, args.output_dir)
    print('Action: render')
    render.render_all(args.theme, args.input_dir, args.intermediate_dir, args.output_dir)


if __name__ == '__main__':
    main()
