import xmlrpc.client
import os.path


class Aria2():
    def __init__(self, uri, secret=None):
        self.conf = self._loadconfig()
        self.aria2 = xmlrpc.client.ServerProxy(uri).aria2
        self.tok = 'token:'
        if secret is not None:
            self.tok += secret
        elif 'rpc-secret' in self.conf:
            self.tok += self.conf['rpc-secret']

    def _loadconfig(self):
        fname = os.path.expanduser('~/.aria2/aria2.conf')
        conf = {}

        try:
            with open(fname) as f:
                lines = f.readlines()
        except FileNotFoundError:
            return conf

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            name, value = line.split('=')
            conf[name] = value

        return conf

    def add(self, uri, opts=None, pos=None):
        ''' add download to aria2.

        uri may be a torrent file, a metalink file or url'''
        args = [self.tok, uri]
        if isinstance(opts, dict):
            args.append(opts)
        if isinstance(pos, int):
            args.append(pos)

        if os.path.isfile(uri):
            ext = os.path.splitext(uri)[1]
            if ext in ('.metalink', '.meta4'):
                args[1] = xmlrpc.client.Binary(open(uri, 'rb').read())
                return self.aria2.addMetalink(*args)
            elif ext == '.torrent':
                args[1] = xmlrpc.client.Binary(open(uri, 'rb').read())
                args.insert(2, tuple())
                return self.aria2.addTorrent(*args)
            else:
                raise ValueError('uri not a recognized file type.')
        else:
            return self.aria2.addUri(*args)

    def list(self, ftype, keys=None, offset=0, num=5):
        '''return status of given fid

        fid may be one of 'all', 'active', 'waiting', 'paused', 'stopped'.'''
        knowntypes = ('all', 'active', 'waiting', 'paused', 'stopped')
        if ftype == 'all':
            ftypes = knowntypes[1:]
        else:
            ftypes = [ftype]

        queryBT = True
        args = [self.tok]
        if keys is not None:
            if 'bittorrent' not in keys:
                queryBT = False
                keys.append('bittorrent')
            args.append(keys)
        numargs = args[:1] + [offset, num] + args[1:]

        reslist = []
        for fid in ftypes:
            if fid == 'active':
                reslist.extend(self.aria2.tellActive(*args))
            elif fid == 'stopped':
                reslist.extend(self.aria2.tellStopped(*numargs))
            elif fid == 'paused' or fid == 'waiting':
                res = self.aria2.tellWaiting(*numargs)
                reslist.extend([d for d in res if d['status'] == fid])
            else:
                args.insert(1, fid)
                reslist.append(self.aria2.tellStatus(*args))

        if not queryBT:
            for d in reslist:
                try:
                    del d['bittorrent']
                except KeyError:
                    continue

        return reslist

    def eval(self, cmd, addSecret=True):
        ''' pass command to xml-rpc.
        
        if addSecret is true, cmd will add rpc secret at first argument'''
        if addSecret:
            part = cmd.split('(', 1)
            cmd = ''.join((part[0], '(', repr(self.tok), ', ', part[1]))
        return eval('self.aria2.' + cmd)
