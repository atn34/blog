#!/usr/bin/env python
"""
usage:
    render.py [--dev] <file>...
    render.py --test <file>
"""
import os
from collections import defaultdict
from docopt import docopt
import itertools
import glob2
from subprocess import Popen, PIPE, check_output
import hashlib
import base64
import tempfile
import jinja2
import yaml
import shutil

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
        outdirectory = os.path.dirname(self.file_name).replace('content/', 'site/', 1)
        outname = base64.urlsafe_b64encode(hashlib.sha1(content).digest()) + ext
        outpath = os.path.join(outdirectory, outname)
        return outpath, outpath.replace('site/', '/', 1)

    def dot(self, source, alt_text=''):
        outpath, outlink = self.get_unique_resource(source)
        if not args['--test'] and not os.path.isfile(outpath):
            if not os.path.exists(os.path.dirname(outpath)):
                os.makedirs(os.path.dirname(outpath))
            with open(outpath, 'w') as f:
                p = Popen(['dot','-Tsvg'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
                f.write(p.communicate(input=source)[0])
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
''' % ('\n'.join(self.python_repls), '\n'.join(self.bash_prompts), '\n'.join(self.python_codes))

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
            ).encode('utf-8')
        return body

    def render_to_file(self):
        outpath = os.path.join('site', self.metadata['link'])
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
    >>> parse_metadata(['---', 'x: 1', 'y: 2', '---'])
    {'y': 2, 'x': 1}
    >>> parse_metadata(['---', 'x: 1\\n', 'y: 2\\n', '---'])
    {'y': 2, 'x': 1}
    >>> parse_metadata(['---', 'x: 1', 'y: 2', '---', 'slkjd'])
    {'y': 2, 'x': 1}
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
    return yaml.load('\n'.join(yaml_lines)) or {}

def parse_metadata_from_file(file_name):
    with open(file_name, 'r') as f:
        d = parse_metadata(f)
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
        d['yyyy-mm'] = '-'.join(str(d['date']).split('-')[:2])
    return d

def get_content(glob):
    if not glob:
        return
    for filename in glob2.glob('content/' + glob):
        if not os.path.isfile(filename):
            continue
        metadata = parse_metadata_from_file(filename)
        if args['--test'] or args['--dev'] or not metadata.get('draft', False):
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
    metadata = parse_metadata(source.splitlines())
    flags = ['--standalone', '--template=templates/pandoc.txt']
    if metadata.get('tableofcontents', True):
        flags.append('--toc')
    p = Popen(['pandoc'] + flags, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    return p.communicate(input=source)[0].decode('utf-8')


if __name__ == "__main__":
    args = docopt(__doc__)
    if args['--test']:
        file_render = FileRender(args['<file>'][0])
        print file_render.format_test()
    else:
        for f in args['<file>']:
            if not os.path.isfile(f):
                continue
            if not any(f.endswith(ext) for ext in ('.md', '.html', '.jinja')):
                outpath = f.replace('content/', 'site/', 1)
                if not os.path.exists(os.path.dirname(outpath)):
                    os.makedirs(os.path.dirname(outpath))
                shutil.copy(f, outpath)
                continue
            file_render = FileRender(f)
            file_render.render_to_file()
