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
        '''load user's config.'''
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

    def pause(self, ftype, force=False):
        if ftype == 'all':
            if force:
                return self.aria2.forcePauseAll(self.tok)
            else:
                return self.aria2.pauseAll(self.tok)
        else:
            if force:
                return self.aria2.forcePause(self.tok, ftype)
            else:
                return self.aria2.pause(self.tok, ftype)

    def remove(self, gid, force=False):
        if force:
            return self.aria2.forceRemove(self.tok, gid)
        else:
            return self.aria2.remove(self.tok, gid)

    def clear(self, ftype):
        '''Remove stopped result'''
        if ftype == 'all':
            return self.aria2.purgeDownloadResult(self.tok)
        else:
            return self.removeDownoadResult(self.tok, ftype)

    def list(self, ftype, keys=None, offset=0, num=5):
        '''return status of given fid

        fid may be gid, or one of 'all', 'active' 'queueing', 'waiting',
        'paused', 'stopped', 'error', 'removed', and 'completed'.
        
        Key 'all' will return all status of file get by tellActive(),
        tellWaiting(), tellStopped().
        'queueing' accept all files staus get by tellWaiting(), note that
        Key 'waiting' only get files that status is 'waititng'.
        Key 'stopped' accept all files status get by tellStopped().
        Others key will only return file that status equals to key.
        If fid is gid, use tellStatus() instead. '''
        alltypes = ('active', 'queueing', 'stopped')
        queueingtypes = ('waiting', 'paused')
        stoppedtypes = ('error', 'removed', 'completed')
        if ftype == 'all':
            ftypes = alltypes
        else:
            ftypes = [ftype]

        queryBT = True
        queryStat = True
        maxnum = 1000
        args = [self.tok]
        if keys is not None:
            if 'bittorrent' not in keys:
                queryBT = False
                keys.append('bittorrent')
            if 'status' not in keys:
                queryStat = False
                keys.append('status')
            args.append(keys)
        numargs = args[:1] + [offset, num] + args[1:]

        reslist = []
        for fid in ftypes:
            if fid == 'active':
                reslist.extend(self.aria2.tellActive(*args))
            elif fid == 'stopped':
                numargs[2] = num
                reslist.extend(self.aria2.tellStopped(*numargs))
            elif fid == 'queueing':
                numargs[2] = num
                reslist.extend(self.aria2.tellWaiting(*numargs))
            elif fid in queueingtypes:
                numargs[2] = maxnum
                res = self.aria2.tellWaiting(*numargs)
                reslist.extend([d for d in res if d['status'] == fid][:num])
            elif fid in stoppedtypes:
                numargs[2] = maxnum
                res = self.aria2.tellStopped(*numargs)
                reslist.extend([d for d in res if d['status'] == fid][:num])
            else:
                args.insert(1, fid)
                reslist.append(self.aria2.tellStatus(*args))

        if not queryBT:
            for d in reslist:
                try:
                    del d['bittorrent']
                except KeyError:
                    continue
        if not queryStat:
            for d in reslist:
                del d['status']


        return reslist

    def getOption(self, gid):
        '''Get option of specified download'''
        return self.aria2.getOption(self.tok, gid)
    
    def changeOption(self, gid, opts):
        noPauseOpts = ('bt-max-peers', 'force-save', 'max-download-limit',
                       'max-upload-limit', 'bt-remove-unselected-file',
                       'bt-request-peer-speed-limit',)

        if all(key in noPauseOpts for key in opts):
            self.aria2.changeOption(self.tok, gid, opts)
        else:
            self.aria2.pause(self.tok, gid)
            self.aria2.changeOption(self.tok, gid, opts)
            self.aria2.unpause(self.tok, gid)

    def save(self):
        '''save setting'''
        return self.aria2.saveSession(self.tok)

    def eval(self, cmd, addSecret=True):
        ''' pass command to xml-rpc.
        
        if addSecret is true, cmd will add rpc secret at first argument'''
        if addSecret:
            part = cmd.split('(', 1)
            cmd = ''.join((part[0], '(', repr(self.tok), ', ', part[1]))
        return eval('self.aria2.' + cmd)

    def execute(self, fname, *args, **kwargs):
        return eval('self.aria2.' + fname)(self.tok, *args, **kwargs)
