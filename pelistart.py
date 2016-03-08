#!/usr/bin/env python
print("Pelican starter v{0}, by s13d\n".format(0.1))

# stdlib
from datetime import datetime
import os
from pathlib import Path
import subprocess
import sys
# pelican
try:
    import pelicanconf as pc
except ImportError:
    print('WARN: are you sure you are in a Pelican directory?')
    print('WARN: some stuff may not work as excepted...')


# check content dir
CONTENT_DIR = 'content/'
try:
    CONTENT_DIR = pc.PATH
except AttributeError:
    print('WARN: Pelican configuration does not contain content dir...')
    print('WARN: Trying to use: {0}'.format(CONTENT_DIR))
finally:
    cdir = Path(CONTENT_DIR)
    if not cdir.exists():
        print('WARN: content directory {0} does not exist!'.format(cdir))
        print('Let me take the liberty to create it...', end='')
        try:
            Path.mkdir(cdir)
            print(' done!')
        except Exception:
            print('\nERROR: did not work...')
            sys.exit()


FILE_FORMATS = {
    '.md': {
        'ext': 'md',
        'name': 'Markdown',
        'md_content': lambda x: x.title(),
        'md_format': '{0}:',
    },
    '.rst': {
        'ext': 'rst',
        'name': 'reStructuredText',
        'md_content': lambda x: x,
        'md_format': ':{0}:'
    },
    '.txt': {
        'ext': 'txt',
        'name': 'AsciiDoc',
        'md_content': lambda x: x.title(),
        'md_format': ':{0}:'
    },
}


def get_articles():
    """ Get all articles already written. """
    for root, dirs, files in os.walk(CONTENT_DIR):
        for file in files:
            yield os.path.join(root, file)


def detect_format():
    """ Detect if you write in reStructuredText, Markdown, or AsciiDoc. """
    formats = dict.fromkeys(FILE_FORMATS, 0)
    for article in get_articles():
        name, extension = os.path.splitext(article)
        if extension in formats.keys():
            formats[extension] += 1

    index = max(formats, key=formats.get)
    if all(x == index for x in formats.values()):
        index = sorted(FILE_FORMATS)[pick_format() - 1]

    cur_form = FILE_FORMATS[index]
    print('You write in {0}, good!'.format(cur_form['name']))
    return cur_form


def pick_format():
    """ Let the user pick the article format of its choice. """
    print('No article written, pick your format:')
    for idx, val in enumerate(sorted(FILE_FORMATS)):
        print('  {0}: {1}'.format(idx+1, FILE_FORMATS[val]))
    pick = None
    while not isinstance(pick, int) or pick <= 0 or pick > len(FILE_FORMATS):
        try:
            pick = int(input('--> '))
        except ValueError:
            pick = None
        except KeyboardInterrupt:
            print('Quitting...')
            sys.exit()
    return pick


def build_header(cur_form):
    """ Populate the article header with as much data as possible """
    try:
        metadata = {
            'date': str(datetime.now())[0:16],
            'category': pick_category(),
            'tags': '',
            'title': input('\n- Title: '),
            'status': 'draft',
            'summary': input('\n- Summary: '),
        }
    except KeyboardInterrupt:
        print('Quitting...')
        sys.exit()
    # really (REALLY) basic slugify
    metadata['slug'] = metadata['title'].lower()
    for char in ['\\', '*', '"', '?', ' ', '!', '§', ',', ';', '.', '/', ':', '|', '=']:
        metadata['slug'] = metadata['slug'].replace(char, '-')
    metadata['slug'] = metadata['slug'].strip('-')
    metadata['slug'] = ''.join([j for i, j in enumerate(metadata['slug'])
                                if j != '-' or j != metadata['slug'][i-1] or i == 0])

    # finally, build it 
    header = ''
    for data in sorted(metadata):
        header += cur_form['md_format'].format(cur_form['md_content'](data))
        header += ' '
        try:
            header += metadata[data]
        except TypeError:
            header += str(metadata[data])
        header += '\n'
    return metadata, header


def pick_category():
    """ Find already used category in existing articles. """
    cats = set()
    for article in get_articles():
        cat = [l.split(':')[1].strip() for l in open(article) if 'category:' in l.lower()][0]
        cats.add(cat)

    cats = list(cats)
    print('\n- Pick a category for your article:')
    for idx, val in enumerate(sorted(cats)):
        print('  {0}: {1}'.format(idx+1, cats[idx]))
    print('  {0}: {1}'.format(len(cats)+1, '[Create a new one]'))
    pick = None
    while not isinstance(pick, int) or pick <= 0 or pick > len(cats)+1:
        try:
            pick = int(input('--> '))
        except ValueError:
            pick = None
        except KeyboardInterrupt:
            print('Quitting...')
            sys.exit()
    # ask for a new category and create associated directory
    if pick == len(cats)+1:
        cat = None
        try:
            cat = input('- New category: ')
        except KeyboardInterrupt:
            print('Quitting...')
            sys.exit()
        try:
            path = Path(os.path.join(CONTENT_DIR, cat))
            path.mkdir()
            print('  has been created!')
        except Exception:
            print('\nERROR: couldn\'t be created...')
            sys.exit()
        return cat

    return cats[pick - 1]


def create_file(metadata, header, cur_form):
    """ Create the article file. """
    path = os.path.join(CONTENT_DIR, metadata['category'],
                        metadata['slug'] + '.' + cur_form['ext'])

    # check if it exists already
    if Path(path).exists():
        try:
            yes = input('Article file already exists, ' +
                        'do you want to overwrite it? (yes/NO)')
        except KeyboardInterrupt:
            print('Quitting...')
            sys.exit()
        if yes != 'yes':
            return path

    with open(path, 'w') as file:
        file.write(header)
        file.write('\n')
        file.write("Start your article here, and don't forget to add tags!\n")
        file.write("Thanks for using Pelican starter :-)\n")

    return path


def open_in_editor(path):
    editor = os.environ.get('EDITOR', '/usr/bin/vi') # default to vi
    subprocess.call([editor, path])


def init():
    """ Do all the work. """
    cur_form = detect_format()
    metadata, header = build_header(cur_form)
    path = create_file(metadata, header, cur_form)
    open_in_editor(path)


if __name__ == '__main__':
    init()
