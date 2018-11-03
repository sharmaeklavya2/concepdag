#!/usr/bin/env python3

import argparse
import re

SPECIAL_CHARS = '\\`*_{}[]()#+-.!'
# These characters will be un-escaped by markdown.

INNER_PATTERN = '|'.join([re.escape(ch) for ch in SPECIAL_CHARS])

OUTER_PATTERNS = [
    r'\$[^\n\$]+\$',
    r'\$\$[\s\S]+?(?=\$\$)\$\$',
    r'\\\(.+?(?=\\\))\\\)',
    r'\\\[[\s\S]+?(?=\\\])\\\]',
    r'\\begin\{align\}[\s\S]+?(?=\\end\{align\})\\end\{align\}',
]

OUTER_PATTERN = '|'.join(OUTER_PATTERNS)


def area_escape(text):
    # escape text within tex groups
    return re.sub(INNER_PATTERN, (lambda match: '\\' + match.group(0)), text)


def tex_md_escape(text):
    # find tex groups
    matcher = (lambda match: area_escape(match.group(0)))
    return re.sub(OUTER_PATTERN, matcher, text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fpath')
    args = parser.parse_args()

    if args.fpath:
        with open(args.fpath) as fp:
            text = fp.read()
    else:
        text = input()
    text2 = tex_md_escape(text)
    print(text2)


if __name__ == '__main__':
    main()
