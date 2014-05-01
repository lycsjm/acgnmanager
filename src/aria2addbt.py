#!/usr/bin/env python
import xmlrpc.client
import os
import os.path
import sqlite3

from dbms import DBMS


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
        raise ValueError('Not a valid bittorrent file or path.')
    return flist


def getPatterns():
    db = sqlite3.connect('../data/acgndb.sqlite', factory=DBMS)
    query = '''
        select anime_id as id, pattern, dir_name
        from anime_file_patterns join anime_dirs using (anime_id)
        order by id;
    '''
    return db.execute(query, tuple()).fetchall()

def autoChangeDir(aria2, pats, dstroot):
    ''' change directory based on patterns'''
    # read info of added file
    info = aria2.tellStatus(tok, gid, ['bittorrent', 'dir'])
    try:
        name = info['bittorrent']['info']['name']
    except KeyError:
        # already added
        return
    for pat in pats:
        if pat['pattern'] in name:
            opts['dir'] = os.path.join(dstroot, pat['dir_name'])
            aria2.pause(tok, gid)
            aria2.changeOption(tok, gid, opts)
            aria2.unpause(tok, gid)
            break
    else:
        # not find any pattern
        # ask for add pattern
        pass
    

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='''Add bitfile to aria2 and automatical change dir.
        ''')
    parser.add_argument('aria2uri', help='aria2 uri')
    parser.add_argument('path', help='''Path of bittorrent file, may be a
                        bittorrent file or directory. If path is directory,
                        it scan all file in that directory''')
    parser.add_argument('--dst', help='''default store directory of that
                        bittorrent file.''')
    parser.add_argument('--secret', help='''given rpc secret token''')
    parser.add_argument('--pat-root', help='''specified root of pattern''')
    args = parser.parse_args()

    aria2 = xmlrpc.client.ServerProxy(args.aria2uri).aria2
    tok = 'token:'
    if args.secret is not None:
        tok += args.secret
    flist = getFileList(args.path)
    opts = {}
    if args.dst is not None:
        opts['dir'] = os.path.abspath(args.dst)

    opts = {}
    if args.dst is not None:
        if not os.path.isdir(args.dst):
            raise ValueError('dst must be a directory.')
        opts['dir'] = os.path.abspath(args.dst)
        if args.pat_root is None:
            dstroot = opts['dir']
        elif not os.path.isdir(args.pat_root):
            raise ValueError('pat-root must be a direcory')
        else:
            dstroot = os.path.abspath(args.pat_root)

    # add bittorrent to aria2
    for f in flist:
        bt = xmlrpc.client.Binary(open(f, 'rb').read())
        gid = aria2.addTorrent(tok, bt, [], opts)

        # process file(change dir, drop download ... etc)
        pats = getPatterns()
        autoChangeDir(aria2, pats, dstroot)
    aria2.saveSession(tok)
    # ask if pattern not found
