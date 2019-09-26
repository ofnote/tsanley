from collections import namedtuple

class DVal ():
    def __init__(self, shape=None, val=None):
        self._shape, self._val = shape, val
    @property
    def shape(self): return self._shape
    @property
    def val(self): return self._val

    def __repr__(self):
        s = f'(shape: {self._shape}, val: {self._val})'
        return s



class ArgList (list):
    def __init__(self, l):
        if isinstance (l, DVal): l = [l]
        else:
            #print (type(l))
            assert isinstance (l, list)
        list.__init__(self, l)
        
    
    def __getitem__(self, key):
        return list.__getitem__(self, key)

    def __add__(self, x):
        if isinstance (x, DVal): x = [x]
        assert isinstance(x, (list, ArgList))
        x = list.__add__(self,x)
        return ArgList(x)

    def __repr__(self):
        return list.__repr__(self)


RefArg = namedtuple('RefArg', ['ref', 'args'])

