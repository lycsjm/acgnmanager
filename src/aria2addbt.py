#!/usr/bin/env python
import xmlrpc.client
import os
import os.path


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
    args = parser.parse_args()

    aria2 = xmlrpc.client.ServerProxy(args.aria2uri).aria2
    tok = 'token:'
    if args.secret is not None:
        tok += args.secret
    flist = getFileList(args.path)
    opts = {}
    if args.dst is not None:
        opts['dir'] = os.path.abspath(args.dst)

    # add bittorrent to aria2
    for f in flist:
        bt = xmlrpc.client.Binary(open(f, 'rb').read())
        gid = aria2.addTorrent(tok, bt, [], opts)
    aria2.saveSession(tok)
    # read info of added file
    # process file(change dir, drop download ... etc)
    # ask if pattern not found
