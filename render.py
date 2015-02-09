#!/usr/bin/env python
"""
usage:
    render.py <file> [--deps|--test]
    render.py --site
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
    'title': 'Ignorance is Bliss',
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
        if key in d:
            vs = d[key] if isinstance(d[key], list) else [d[key]]
        else:
            vs = []
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
    outdirectory = os.path.dirname(args['<file>']).replace('content/', 'site/', 1)
    outname = base64.urlsafe_b64encode(hashlib.sha1(content).digest()) + ext
    outpath = os.path.join(outdirectory, outname)
    return outpath, outpath.replace('site/', '/', 1)

def inline_img(link, alt_text=''):
    return '![%s](%s)' % (alt_text, link)

def dot(source, alt_text=''):
    outpath, outlink = get_unique_resource(source)
    if not args['--test']:
        with open(outpath, 'w') as f:
            p = Popen(['dot','-Tsvg'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
            f.write(p.communicate(input=source)[0])
    return inline_img(outlink, alt_text)

plots = []
def plot(source, alt_text=''):
    outpath, outlink = get_unique_resource(source)
    plots.append((source, outpath))
    return inline_img(outlink, alt_text)

python_codes = []
def python_code(source):
    global python_codes
    python_codes.append(source)
    return """
```python%s
```
""" % source

python_repls = []
def python_repl(source):
    global python_repls
    python_repls.append(source)
    return """
```python%s
```
""" % source

bash_prompts = []
def bash_prompt(source):
    global bash_prompts
    bash_prompts.append(source)
    return """
```terminal%s
```
""" % source

env = Environment(
    loader=FileSystemLoader('templates'),
)

env.filters['invert_by'] = invert_by
env.filters['limit'] = itertools.islice
env.filters['include_file'] = include_file
env.filters['dot'] = dot
env.filters['plot'] = plot
env.filters['python_code'] = python_code
env.filters['python_repl'] = python_repl
env.filters['bash_prompt'] = bash_prompt

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

def parse_metadata(source):
    dddash_count = 0
    yaml_lines = []
    for line in source.splitlines():
        if line == '---':
            dddash_count += 1
        if dddash_count == 1:
            yaml_lines.append(line)
        elif dddash_count == 2:
            break
    return yaml.load('\n'.join(yaml_lines)) or {}

def parse_metadata_from_file(file_name):
    with open(file_name, 'r') as f:
        d = parse_metadata(f.read())
    root, ext = os.path.splitext(file_name)
    if root.startswith('./'):
        root = root[len('./'):]
    ext_map = {
        '.md': '.html',
        '.jinja': '',
    }
    d['link'] = root.replace('content/', '', 1) + ext_map.get(ext, ext)
    d['file_name'] = file_name
    d['post'] = file_name.startswith('content/posts/')
    if 'date' in d:
        d['yyyy-mm'] = '%s-%s' % (d['date'].year, d['date'].month)
    return d

def get_content(glob):
    if not glob:
        return
    for filename in glob2.glob('content/' + glob):
        if not os.path.isfile(filename):
            continue
        metadata = parse_metadata_from_file(filename)
        if not metadata.get('draft', False):
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

def pandoc(source):
    metadata = parse_metadata(source)
    flags = ['--standalone', '--template=templates/pandoc.txt']
    if metadata.get('tableofcontents', True):
        flags.append('--toc')
    p = Popen(['pandoc'] + flags, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    return p.communicate(input=source)[0].decode('utf-8')

def format_test():
    return '''#!/usr/bin/env python
class Py(object):
    """%s
"""
    pass

class Bash(object):
    """%s
"""
    pass
%s

import doctest
import shelldoctest
import sys
failures = doctest.testmod()[0] or 0
failures += shelldoctest.testmod()[0] or 0
sys.exit(failures)
''' % ('\n'.join(python_repls), '\n'.join(bash_prompts), '\n'.join(python_codes))

def format_plot():
    if args['--test']:
        return
    _, tempf = tempfile.mkstemp()
    with open(tempf, 'w') as f:
        f.write('import matplotlib.pyplot as plt\n')
        f.write('\n'.join(python_codes) + '\n')
        for source, path in plots:
            f.write(source + '\n')
            f.write('plt.gcf().set_size_inches(6,6)\n')
            f.write('plt.savefig("%s")\n' % path)
            f.write('plt.clf()\n')
    check_output(['python', tempf])
    os.unlink(tempf)

if __name__ == '__main__':
    args = docopt(__doc__)
    if args['--site']:
        print ' '.join('site/' + m['link'] for m in get_content('**/*'))
        sys.exit(0)
    metadata = parse_metadata_from_file(args['<file>'])
    deps = metadata.get('deps', '')
    base_template_name = metadata.get('base', default_template_name(args['<file>']))
    with open(args['<file>'], 'r') as f:
        body = env.from_string(f.read()).render(
            deps=get_content(deps),
            metadata=metadata,
            **SITE
        )
    if args['--test']:
        print format_test()
        sys.exit(0)
    elif args['--deps']:
        result = []
        result.append('site/' + metadata['link'])
        result.append('.deps/' + 'site/' + metadata['link'])
        result.append(':')
        result.append(__file__)
        result.extend(dep['file_name'] for dep in get_content(deps))
        result.extend(included_files)
        if base_template_name:
            result.append('templates/' + base_template_name)
        if args['<file>'].endswith('.md'):
            result.append('templates/pandoc.txt')
        print ' '.join(result)
        sys.exit(0)
    if plots:
        format_plot()
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
