from jinja2 import Environment
import fnmatch
import sys
import os
import yaml
from collections import defaultdict

def invert_by(ds, key):
    result = defaultdict(list)
    for d in ds:
        vs = d[key] if isinstance(d[key], list) else [d[key]]
        for v in vs:
            result[v].append(d)
    return result.iteritems()

env = Environment(trim_blocks=True)

env.filters['invert_by'] = invert_by

def parse_md_file(file_name):
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
    d['link'] = file_name[:-3] + '.html'
    return d

def get_md_files():
    os.chdir('content')
    for root, dirnames, filenames in os.walk('.'):
        for filename in fnmatch.filter(filenames, '*.md'):
            yield parse_md_file(os.path.join(root, filename))

if __name__ == '__main__':
    print env.from_string(sys.stdin.read()).render(md_files=get_md_files())
