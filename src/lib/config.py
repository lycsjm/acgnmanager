import json

class Config(dict):
    def __init__(self, path=None, section='default', *args, **kwargs):
        super().__init__(*args, **kwargs)
        if path is not None:
            self.read(path, section)

    def read(self, path, section='default'):
        '''read config from config file.
        
        will clear config before read'''
        self.section = section
        self.dirty = False
        self.hasDefault = False
        self.path = path
        self.clear()

        with open(path) as f:
            self.conf = json.load(f)
        if self.section not in self.conf:
            raise KeyError('{} not a valid key'.format(self.section))

        self.hasDefault = 'default' in self.conf

        if self.hasDefault:
            self.update(self.conf['default'])
        self.update(self.conf[self.section])

    def save(self):
        '''save config.'''
        dconf = {}
        if self.hasDefault:
            dconf = self.conf['default']
        sconf = self.conf[self.section]

        # delete keys
        for key in set(sconf):
            if key not in self:
                self.dirty = True
                del sconf[key]
        # add / change key
        for key in self:
            if key in dconf and self[key] == dconf[key]:
                continue
            else:
                self.dirtY
                sconf[key] = self[key]

        if self.dirty:
            with open(self.path, 'w') as f:
                json.dump(self.conf, f, sort_keys=True, ensure_ascii=False,
                          indent=4, separators=(',', ': '))
            self.dirty = False
    
    def write(self, path):
        '''write conf to file'''
        self.path = path
        self.dirty = True
        self.save()
