#!/usr/bin/env python
import sqlite3
import os.path

from dbms import DBMS



def  getPatternList(*args, **kwargs):
    query = '''
        select pattern, dir_name
        from anime_file_patterns join anime_dirs using (anime_id)
        order by anime_dirs.anime_id;
    '''
    return db.execute(query, tuple()).fetchall()


def match(root, patterns):
    sortlist = []
    for pat in patterns:
        for fname in os.listdir(root):
            src = os.path.join(root, fname)
            dst = os.path.join(pat['dst'], fname)
            if pat['pattern'] in fname:
                sortlist.append({'dst': dst, 'src': src})
    return sortlist


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='''Sorting files in source directory to destination
        directorys by patterns ''')
    parser.add_argument('--src', help='source directory')
    parser.add_argument('--dst', help='destination directory')
    args = parser.parse_args()
    
    db = sqlite3.connect('../data/acgndb.sqlite', factory=DBMS)
    patterns = getPatternlist(db=db)

    pat = []
    for pattern in patterns:
        dst = os.path.join(args.dst, pattern['dir_name'])
        pat.append({'pattern': pattern['pattern'], 'dst': dst})

    sortlist = match(args.src, pat)
