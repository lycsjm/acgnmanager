#!/usr/bin/env python
import sqlite3
import os.path
import shutil

from dbms import DBMS



def  getPatternList(*args, **kwargs):
    query = '''
        select pattern, dir_name
        from anime_file_patterns join anime_dirs using (anime_id)
        order by anime_dirs.anime_id;
    '''
    return db.execute(query, tuple()).fetchall()


def complish(path):
    '''Check file still downloading by aria2 or not.

    return True if file finish download.'''
    ariaext = ['aria2', 'aria2__temp']
    ariaf = ['.'.join([path, ext]) for ext in ariaext]

    for ariaf in ariaf:
        if os.path.exists(ariaf) or ariaext[0] in path:
            return False
    else:
        return True


def match(root, patterns):
    sortlist = []
    for fname in os.listdir(root):
        src = os.path.join(root, fname)
        if not complish(src):
            continue
        for pat in patterns:
            if pat['pattern'] in fname:
                dst = os.path.join(pat['dst'], fname)
                sortlist.append({'dst': dst, 'src': src})
    return sortlist


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='''Sorting files in source directory to destination
        directorys by patterns ''')
    parser.add_argument('--src', help='source directory')
    parser.add_argument('--dst', help='destination directory')
    parser.add_argument('-d', '--dry-run', help='dry run', action='store_true')
    args = parser.parse_args()
    
    db = sqlite3.connect('../data/acgndb.sqlite', factory=DBMS)
    patterns = getPatternlist(db=db)

    pat = []
    for pattern in patterns:
        dst = os.path.join(args.dst, pattern['dir_name'])
        pat.append({'pattern': pattern['pattern'], 'dst': dst})

    sortlist = match(args.src, pat)

    for path in sortlist:
        if args.dry_run:
            print('{} -> {}'.format(path['src'], path['dst']))
        else:
            try:
                shutil.move(path['src'], path['dst'])
            except FileExistsError as e:
                print(e)

