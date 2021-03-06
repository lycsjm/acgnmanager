#!/usr/bin/env python
import os
import os.path
import sqlite3
import textwrap
import sys
import datetime

from lib.dbms import DBMS
from lib.config import Config
from lib.aria2 import Aria2


def getArgs():
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''Add bitfile to aria2 and automatical change dir.''',
        epilog=textwrap.dedent('''
        Example:
            aria2addbt.py --aria2uri "http://localhost:6800/rpc" --path\\
            ~/bittorrent --dst ~/anime

            aria2addbt.py --config config.json anime music
        '''))
    parser.add_argument('--aria2uri', help='aria2 uri')
    parser.add_argument('--path',
                        help='''Path of bittorrent file, may be a bittorrent
                        file or directory. If path is directory, it scan all
                        file in that directory''')
    parser.add_argument('--dst', help='''default store directory of that
                        bittorrent file.''')
    parser.add_argument('--secret', help='''given rpc secret token''')
    parser.add_argument('--pat-root', help='''specified root of pattern''')
    parser.add_argument('-c', '--config', nargs='+',
                        metavar=('FILE', 'SECTION'), help='''Read config from
                        file. FILE is file name of that config and SECTION is
                        section.''')
    args = parser.parse_args()

    if args.config is not None:
        if len(args.config) == 1:
            args.config.append('default')
        for section in args.config[1:]:
            conf = Config(args.config[0], section)
            for key in vars(args):
                if key in conf:
                    exec('args.{key} = conf["{key}"]'.format(key=key))
            yield args
            parser.parse_args(namespace=args)
    else:
        yield args


def getFileList(path):
    '''get list of bittorrent files.'''
    path = os.path.abspath(path)
    isbt = lambda f: os.path.isfile(f) and os.path.splitext(f)[1] == '.torrent'
    flist = []
    if isbt(path):
        flist.append(path)
    elif os.path.isdir(path):
        for f in os.listdir(path):
            f = os.path.join(path, f)
            if isbt(f):
                flist.append(f)
    else:
        msg = '{} not a directory or valide bittorrent file.'.format(path)
        raise ValueError(msg)
    return flist


def getPatterns(dbpath):
    db = sqlite3.connect(dbpath, factory=DBMS)
    query = '''
        select anime_id as id, pattern, dir_name
        from anime_file_patterns join anime_dirs using (anime_id)
        order by id;
    '''
    return db.execute(query, tuple()).fetchall()


def mkOptions(args):
    opts = {}
    if args.dst is not None:
        if not os.path.isdir(args.dst):
            raise ValueError('dst must be a directory.')
        opts['dir'] = os.path.abspath(args.dst)
    return opts


def getPatRoot(args):
    if args.pat_root is None:
        if args.dst is not None:
            return os.path.abspath(args.dst)
        else:
            return
    elif not os.path.isdir(args.pat_root):
        raise ValueError('pat-root must be a direcory')
    else:
        return os.path.abspath(args.pat_root)


def main():
    today = datetime.date.today()
    scriptpath = os.path.dirname(sys.argv[0])
    dbpath = os.path.join(scriptpath, '../data/filelog.sqlite')
    logger = sqlite3.connect(dbpath)
    logquery = '''
        insert or ignore into torrent_log(adddate, fname, tname)
        values (?, ?, ?);
    '''
    pats = getPatterns(os.path.join(scriptpath, '../data/acgndb.sqlite'))

    for args in getArgs():
        aria2 = Aria2(args.aria2uri, args.secret)

        opts = mkOptions(args)
        dstroot = getPatRoot(args)

        flist = getFileList(args.path)
        # add bittorrent to aria2
        for f in flist:
            gid = aria2.add(f, opts)

            # process file(change dir, drop download ... etc)
            info = aria2.list(gid, ['bittorrent', 'dir'])
            try:
                name = info['bittorrent']['info']['name']
            except KeyError:
                # already added
                pass
            for pat in pats:
                if pat['pattern'] in name:
                    opts['dir'] = os.path.join(dstroot, pat['dir_name'])
                    aria2.changeOption(gid, opts)
                    break
            else:
                # not find any pattern
                # ask for add pattern
                pass

            # log and remove source bt
            qargs = (today, name, f)
            logger.execute(logquery, qargs)
            os.remove(f)
        aria2.saveSession(tok)
        # ask if pattern not found
    logger.commit()


if __name__ == '__main__':
    main()
