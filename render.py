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
from subprocess import Popen, PIPE, check_output
import hashlib
import base64
import tempfile

SITE = {
    'production_url': 'www.atn34.com',
    'title': 'Stuff Andrew Likes',
}

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

def get_unique_resource(content, ext='.svg'):
    outdirectory = os.path.dirname(args['<file>']).replace('content/', 'site/')
    outname = base64.urlsafe_b64encode(hashlib.sha1(content).digest()) + ext
    outpath = os.path.join(outdirectory, outname)
    return outpath, outpath.replace('site/', '/')

def inline_img(link, alt_text=''):
    return '![%s](%s)' % (alt_text, link)

def dot(source, alt_text=''):
    outpath, outlink = get_unique_resource(source)
    with open(outpath, 'w') as f:
        p = Popen(['dot','-Tsvg'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        f.write(p.communicate(input=source)[0])
    return inline_img(outlink, alt_text)

def plot(source, alt_text=''):
    outpath, outlink = get_unique_resource(source)
    _, tempf = tempfile.mkstemp()
    with open(tempf, 'w') as f:
        f.write("""
import matplotlib.pyplot as plt
%(source)s
plt.gcf().set_size_inches(6,6)
plt.savefig("%(outpath)s")
""" % vars())
    check_output(['python', tempf])
    os.unlink(tempf)
    return inline_img(outlink, alt_text)

env = Environment(
    loader=FileSystemLoader('templates'),
)

env.filters['invert_by'] = invert_by
env.filters['limit'] = itertools.islice
env.filters['include_file'] = include_file
env.filters['dot'] = dot
env.filters['plot'] = plot

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
            **SITE
        )
    if args['--firstpass']:
        print body
        sys.exit(0)
    elif args['--deps']:
        result = 'site/' + metadata['link']
        result += ' .deps/' + result + ': '
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
            **SITE
        ).encode('utf-8')
    else:
        print body
