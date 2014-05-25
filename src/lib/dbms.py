import sqlite3
import itertools

class DBMS(sqlite3.Connection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.row_factory = sqlite3.Row

    def getaids(self, limits):
        '''
            get list of anime's id that satisfied limits

            limits is a dict-like object may contain following keys:
            
                * date: 2-tuple contain range of start date
                * name: string of anime name
        '''
        def toset(res):
            try:
                return set(r[0] for r in res)
            except IndexError:
                return set()
        
        aidslist = []
        if 'date' in limits:
            res = self.execute('''
                select id from anime where startdate >= ? and startdate < ?;
            ''', limits['date'])
            aidslist.append(toset(res))
        if 'name' in limits:
            res = self.execute('''
                select id from anime where name = ?;
            ''', (limits['name'], ))
            aidslist.append(toset(res))
        
        it = iter(aidslist)
        try:
            aids = next(it)
        except StopIteration:
            return []
        for ids in it:
            aids &= ids
        return list(aids)
