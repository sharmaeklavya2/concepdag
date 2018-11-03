#!/usr/bin/env python3

import argparse

from lib import process_json_0, process_json_1, render


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project_dir')
    parser.add_argument('actions', nargs='*', choices=('0', '1', 'render'))
    args = parser.parse_args()

    if '0' in args.actions:
        print('Action: 0')
        process_json_0.run_on_all(args.project_dir)
    if '1' in args.actions:
        print('Action: 1')
        process_json_1.run_on_all(args.project_dir)
    if 'render' in args.actions:
        print('Action: render')
        render.render_all(args.project_dir)


if __name__ == '__main__':
    main()
