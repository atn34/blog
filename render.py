from jinja2 import Environment
import fnmatch
import sys
import os
import yaml
from collections import defaultdict

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

def limit(items, count):
    """
    >>> list(limit(xrange(5), 10))
    [0, 1, 2, 3, 4]
    """
    n = 0
    while n < count:
        try:
            if hasattr(items, 'next'):
                yield items.next()
            else:
                yield items[n]
        except StopIteration:
            break
        except IndexError:
            break
        n += 1

def include_file(file_name):
    with open(file_name, 'r') as f:
        return f.read()

env = Environment(trim_blocks=True, lstrip_blocks=True)

env.filters['invert_by'] = invert_by
env.filters['limit'] = limit
env.filters['include_file'] = include_file

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
    root, _ = os.path.splitext(file_name)
    if root.startswith('./'):
        root = root[len('./'):]
    d['link'] = root + '.html'
    return d

def get_content(glob, directory='.'):
    for root, dirnames, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, glob):
            metadata = parse_metadata(os.path.join(root, filename))
            if not metadata.get('draft', False):
                yield metadata

if __name__ == '__main__':
    os.chdir('content')
    print env.from_string(sys.stdin.read()).render(
        posts=get_content('*.md', directory='posts'),
        pages=get_content('*.md*'),
        production_url='www.atn34.com',
    )
