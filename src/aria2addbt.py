#!/usr/bin/env python
import xmlrpc.client


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
    args = parser.parse_args()

    aria2 = xmlrpc.client.ServerProxy(args.aria2uri).aria2
    # add bittorrent to aria2
    bt = xmlrpc.client.Binary(open(args.path, 'rb').read())
    aria2.addTorrent(bt, [])
    # read info of added file
    # process file(change dir, drop download ... etc)
    # ask if pattern not found
