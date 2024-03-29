#!/usr/bin/env python3
"""
usage:
    render.py (build|serve) [--dev --source=<dir> --dest=<dir>]
    render.py test <file>

options:
    --dev           Include draft posts.
    --source=<dir>  Directory of source content [default: content].
    --dest=<dir>    Directory to generate site [default: site].
"""

from collections import defaultdict
from docopt import docopt
from identify import identify
from subprocess import Popen, PIPE, check_output

import bottle
import base64
import glob2
import hashlib
import itertools
import jinja2
import os
import shutil
import sys
import tempfile
import threading
import yaml

def pandoc(source):
    metadata = parse_metadata(source.splitlines())
    flags = ['--standalone', '--template=templates/pandoc.txt', '--mathjax']
    if metadata.get('tableofcontents', True):
        flags.append('--toc')
    p = Popen(['pandoc'] + flags, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    return p.communicate(input=source.encode('utf-8'))[0].decode('utf-8')

SITE = {
    'production_url': 'www.atn34.com',
    'title': 'Ignorance is Bliss',
    'description': 'Ramblings about Computer Science',
}

APPLY_JINJA = {
    '.md': '.html',
    '.jinja': '',
    '.html': '.html',
}

FILTER_BODY = {
    '.md': pandoc,
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
        return sorted(result.items())
    else:
        return result.iteritems()

included_files = []

def include_file(file_name):
    included_files.append(os.path.join(args['--dest'], file_name))
    with open(os.path.join(args['--source'], file_name), 'r') as f:
        return f.read()

def inline_img(link, alt_text=''):
    return '![%s](%s)' % (alt_text, link)

def codeblock(source, css_class=''):
    return """
```%s%s
```
""" % (css_class, source)

class FileRender(object):

    def __init__(self, file_name):
        self.file_name = file_name
        self.plots = []
        self.python_codes = []
        self.python_repls = []
        self.bash_prompts = []
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader('templates'),
        )
        env.filters['invert_by'] = invert_by
        env.filters['limit'] = itertools.islice
        env.filters['include_file'] = include_file
        env.filters['dot'] = self.dot
        env.filters['plot'] = self.plot
        env.filters['python_code'] = self.python_code
        env.filters['python_repl'] = self.python_repl
        env.filters['bash_prompt'] = self.bash_prompt
        self.env = env
        self.metadata = parse_metadata_from_file(self.file_name)

    def get_unique_resource(self, content, ext='.svg'):
        outdirectory = os.path.dirname(self.file_name).replace(args['--source'], args['--dest'], 1)
        outname = base64.urlsafe_b64encode(hashlib.sha1(content.encode('utf-8')).digest()).decode('utf-8') + ext
        outpath = os.path.join(outdirectory, outname)
        return outpath, outpath.replace(args['--dest'], '/', 1)

    def dot(self, source, alt_text=''):
        outpath, outlink = self.get_unique_resource(source)
        if not args['test'] and not os.path.isfile(outpath):
            if not os.path.exists(os.path.dirname(outpath)):
                os.makedirs(os.path.dirname(outpath))
            with open(outpath, 'wb') as f:
                p = Popen(['dot','-Tsvg'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
                f.write(p.communicate(input=source.encode('utf-8'))[0])
        return inline_img(outlink, alt_text)

    def plot(self, source, alt_text=''):
        outpath, outlink = self.get_unique_resource(source)
        self.plots.append((source, outpath))
        return inline_img(outlink, alt_text)

    def python_code(self, source):
        self.python_codes.append(source)
        return codeblock(source, 'python')

    def python_repl(self, source):
        self.python_repls.append(source)
        return codeblock(source, 'python')

    def format_test(self):
        deps = self.metadata.get('deps', '')
        with open(self.file_name, 'r') as f:
            self.env.from_string(f.read()).render(
                deps=get_content(deps),
                metadata=self.metadata,
                **SITE
            )
        return '''#!/usr/bin/env python3
class Py(object):
    """%s
"""
    pass

%s

import doctest
import sys
failures = doctest.testmod()[0] or 0
sys.exit(failures)
''' % ('\n'.join(self.python_repls), '\n'.join(self.python_codes))

    def bash_prompt(self, source):
        self.bash_prompts.append(source)
        return codeblock(source, 'terminal')

    def format_plot(self):
        _, tempf = tempfile.mkstemp()
        with open(tempf, 'w') as f:
            f.write('import os\n')
            f.write('\n'.join(self.python_codes) + '\n')
            for source, path in self.plots:
                f.write('if not os.path.isfile("%s"):\n' % path)
                f.write('    import matplotlib.pyplot as plt\n')
                f.write('\n'.join('    ' + s for s in source.splitlines()))
                f.write('\n')
                f.write('    plt.gcf().set_size_inches(6,6)\n')
                f.write('    plt.savefig("%s")\n' % path)
                f.write('    plt.clf()\n')
        check_output(['python', tempf])
        os.unlink(tempf)

    def render(self):
        deps = self.metadata.get('deps', '')
        base_template_name = self.metadata.get('base', default_template_name(self.file_name))
        with open(self.file_name, 'r') as f:
            body = self.env.from_string(f.read()).render(
                deps=get_content(deps),
                metadata=self.metadata,
                **SITE
            )
        body = filter_body(self.file_name)(body)
        if self.plots:
            self.format_plot()
        if base_template_name:
            return self.env.get_template(base_template_name).render(
                body=body,
                deps=get_content(deps),
                metadata=self.metadata,
                **SITE
            )
        return body

    def render_to_file(self):
        outpath = os.path.join(args['--dest'], self.metadata['link'])
        if not os.path.exists(os.path.dirname(outpath)):
            os.makedirs(os.path.dirname(outpath))
        with open(outpath, 'w') as f:
            f.write(self.render())

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

def parse_metadata(lines):
    """
    >>> sorted(parse_metadata(['---', 'x: 1', 'y: 2', '---']).items())
    [('x', 1), ('y', 2)]
    >>> sorted(parse_metadata(['---', 'x: 1\\n', 'y: 2\\n', '---']).items())
    [('x', 1), ('y', 2)]
    >>> sorted(parse_metadata(['---', 'x: 1', 'y: 2', '---', 'slkjd']).items())
    [('x', 1), ('y', 2)]
    """
    dddash_count = 0
    yaml_lines = []
    for line in lines:
        if line.endswith('\n'):
            line = line[:-1]
        if line == '---':
            dddash_count += 1
        if dddash_count == 1:
            yaml_lines.append(line)
        elif dddash_count == 2:
            break
    return yaml.safe_load('\n'.join(yaml_lines)) or {}

def parse_metadata_from_file(file_name):
    d = {}
    if 'text' in identify.tags_from_path(file_name):
        with open(file_name, 'r') as f:
            d = parse_metadata(f)
    root, ext = os.path.splitext(file_name)
    if root.startswith('./'):
        root = root[len('./'):]
    d['link'] = root.replace(args['--source'], '', 1) + APPLY_JINJA.get(ext, ext)
    d['file_name'] = file_name
    d['post'] = file_name.startswith(os.path.join(args['--source'], 'posts'))
    if 'date' in d:
        d['yyyy-mm'] = '-'.join(str(d['date']).split('-')[:2])
    return d

def get_content(glob):
    if not glob:
        return
    for filename in glob2.glob(args['--source'] + glob):
        if not os.path.isfile(filename):
            continue
        metadata = parse_metadata_from_file(filename)
        if args['test'] or args['--dev'] or not metadata.get('draft', False):
            yield metadata

def default_template_name(file_name):
    _, ext = os.path.splitext(file_name)
    return {
        '.md': 'default.html',
        '.html': 'default.html',
    }.get(ext)

def filter_body(file_name):
    _, ext = os.path.splitext(file_name)
    return FILTER_BODY.get(ext, strip_metadata)

def build(modified_file=None):
    for metadata in get_content('**'):
        deps = metadata.get('deps', '')
        if modified_file is not None and not (glob2.fnmatch.fnmatch(modified_file, deps) or metadata['file_name'] == os.path.join(args['--source'], modified_file)):
            continue
        f = metadata['file_name']
        if not os.path.isfile(f):
            continue
        if not any(f.endswith(ext) for ext in APPLY_JINJA):
            print('copying ' + f)
            outpath = f.replace(args['--source'], args['--dest'], 1)
            if not os.path.exists(os.path.dirname(outpath)):
                os.makedirs(os.path.dirname(outpath))
            shutil.copy(f, outpath)
            continue
        print('rendering ' + f)
        file_render = FileRender(f)
        file_render.render_to_file()
    print('done.')
@bottle.route('<path:path>')
def serve_path(path):
    return bottle.static_file(path, args['--dest'])

@bottle.route('/')
def serve_root():
    return serve_path('/index.html')

def serve():
    bottle.run(host='localhost', port=8000)


if __name__ == "__main__":
    args = docopt(__doc__)
    if args['test']:
        file_render = FileRender(args['<file>'])
        print(file_render.format_test())
    elif args['build'] or args['serve']:
        if not os.path.isdir(args['--source']):
            print(args['--source'] + ' is not a dir')
            sys.exit(1)
        if not os.path.isdir(args['--dest']):
            print(args['--dest'] + ' is not a dir')
            sys.exit(1)
        if not args['--source'].endswith('/'):
            args['--source'] += '/'
        if not args['--dest'].endswith('/'):
            args['--dest'] += '/'
        build()
    if args['serve']:
        t = threading.Thread(target=serve)
        t.daemon = True
        t.start()
        t.join()
