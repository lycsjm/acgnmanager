import datetime
import sqlite3
import os.path
import os

from dbms import DBMS


def getSeason(date=datetime.date.today()):
    '''
    return 2-tuple of datetime.date as anime start date range.
    consider some anime will start some days before season of given days,
    return will not exectally as same as season.

    example:
    >>> getSeason(datetime.date(2014, 1, 13))
    (datetime.date(2014, 12, 01), datetime.date(2014, 03, 01))
    >>> getseason(datetime.date(2014, 06, 12))
    (datetime.date(2014, 06, 01), datetime.date(2014, 09, 01))
    '''
    years = [date.year] * 5
    years[0] -= 1
    months = [12, 3, 6, 9, 12]
    season = (date.month - 1) // 3
    startdate = datetime.date(years[season], months[season], 1)
    enddate = datetime.date(years[season + 1], months[season + 1], 1)

    return (startdate, enddate)


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


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='automatically make formatted dirs to given root')
    parser.add_argument('--dst', help='path to create dirs')
    args = parser.parse_args()

    limits = {}
    limits['date'] = getSeason(datetime.date.today())

    db = sqlite3.connect('../data/acgndb.sqlite', factory=DBMS)
    dirlist = getDirList(db, args.dst, db.getaids(limits))
    
    for name in dirlist:
        try:
            os.mkdir(name)
        except FileExistsError as e:
            print(e)
