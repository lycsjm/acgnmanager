#!/usr/bin/env python
import datetime
import sqlite3
import os.path
import os

from lib.dbms import DBMS
from lib.util import getSeason


def getDirList(db, root, ids):
    '''get list of dir name'''

    query = '''
        select dir_name
        from anime_dirs
        where anime_id in ({});
    '''.format(', '.join(map(str, ids)))
    names = db.execute(query, tuple())
    dirlist = []
    for name in names:
        dirlist.append(os.path.join(os.path.abspath(root), name['dir_name']))

    return dirlist


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='automatically make formatted dirs to given root')
    parser.add_argument('--dst', help='path to create dirs')
    parser.add_argument('--date', nargs=2, help='date option of mhaf')
    args = parser.parse_args()

    limits = {}
    if args.date is None:
        limits['date'] = getSeason()
    else:
        limits['date'] = []
        for date in args.date:
            ts = datetime.datetime.strptime(date, '%Y-%m-%d').timestamp()
            limits['date'].append(datetime.date.fromtimestamp(ts))

    db = sqlite3.connect('../data/acgndb.sqlite', factory=DBMS)
    dirlist = getDirList(db, args.dst, db.getaids(limits))
    
    for name in dirlist:
        try:
            os.mkdir(name)
        except FileExistsError as e:
            print(e)


if __name__ == '__main__':
    main()
