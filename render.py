#!/usr/bin/env python
"""
usage:
    render.py <file> [--deps|--firstpass]
"""
from jinja2 import Environment, FileSystemLoader
import sys
import os
import yaml
from collections import defaultdict
from docopt import docopt
import itertools
import glob2
from subprocess import Popen, PIPE

production_url = 'www.atn34.com'

def _test():
    import doctest
    return doctest.testmod()

def invert_by(ds, key, sort=True):
    """
    >>> invert_by([{'a': ['b','c']}], 'a')
    [('b', [{'a': ['b', 'c']}]), ('c', [{'a': ['b', 'c']}])]
    """
    result = defaultdict(list)
    for d in ds:
        vs = d[key] if isinstance(d[key], list) else [d[key]]
        for v in vs:
            result[v].append(d)
    if sort:
        return sorted(result.iteritems())
    else:
        return result.iteritems()

included_files = []

def include_file(file_name):
    included_files.append(os.path.join('site', file_name))
    with open(os.path.join('content', file_name), 'r') as f:
        return f.read()

env = Environment(
    loader=FileSystemLoader('templates'),
    trim_blocks=True,
    lstrip_blocks=True
)

env.filters['invert_by'] = invert_by
env.filters['limit'] = itertools.islice
env.filters['include_file'] = include_file

def strip_metadata(body):
    dddash_count = 0
    result = []
    for line in body.splitlines():
        if line == '---':
            dddash_count += 1
            continue
        if dddash_count != 1:
            result.append(line)
    return '\n'.join(result)

def parse_metadata(file_name):
    with open(file_name, 'r') as f:
        dddash_count = 0
        yaml_lines = []
        for line in f:
            if line == '---\n':
                dddash_count += 1
            if dddash_count == 1:
                yaml_lines.append(line)
            elif dddash_count == 2:
                break
    d = yaml.load(''.join(yaml_lines)) or {}
    root, ext = os.path.splitext(file_name)
    if root.startswith('./'):
        root = root[len('./'):]
    ext_map = {
        '.md': '.html',
        '.jinja': '',
    }
    d['link'] = root.replace('content/', '', 1) + ext_map.get(ext, ext)
    d['file_name'] = file_name
    return d

def get_content(glob):
    if glob:
        for filename in glob2.glob('content/' + glob):
            metadata = parse_metadata(filename)
            yield metadata

def default_template_name(file_name):
    _, ext = os.path.splitext(file_name)
    return {
        '.md': 'default.html',
        '.html': 'default.html',
    }.get(ext)

def filter_body(file_name):
    _, ext = os.path.splitext(file_name)
    return {
        '.md': pandoc,
    }.get(ext, strip_metadata)

def pandoc(input):
    p = Popen(['pandoc'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
    return p.communicate(input=input)[0].decode('utf-8')

if __name__ == '__main__':
    args = docopt(__doc__)
    metadata = parse_metadata(args['<file>'])
    deps = metadata.get('deps', '')
    base_template_name = metadata.get('base', default_template_name(args['<file>']))
    with open(args['<file>'], 'r') as f:
        body = env.from_string(f.read()).render(
            deps=get_content(deps),
            metadata=metadata,
            production_url=production_url,
        )
    if args['--deps']:
        print body
        sys.exit(0)
    elif args['--deps']:
        result = 'site/' + metadata['link']
        result += ' deps/' + result + ': '
        result += ' '.join(dep['file_name'] for dep in get_content(deps))
        result += ' '.join(included_files)
        if base_template_name:
            result += ' templates/' + base_template_name
        print result
        sys.exit(0)
    body = filter_body(args['<file>'])(body)
    if base_template_name:
        print env.get_template(base_template_name).render(
            body=body,
            deps=get_content(deps),
            metadata=metadata,
            production_url=production_url,
        ).encode('utf-8')
    else:
        print body
