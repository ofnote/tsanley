from collections import defaultdict
import json
from ..common.log_utils import log

from tsalib.ts import get_decls
from tsalib.backend import get_backend_by_name, get_str_type


tensor_classes = {
    'torch': ['torch.Tensor', 'torch.nn.parameter.Parameter', 'torch.nn.modules.sparse.Embedding']
}

def is_tensor(x):
    t = get_str_type(x)

    if 'numpy.' in t: ret = ('numpy.ndarray' in t)
    elif 'torch.' in t: 
        ret = any([x in t for x in tensor_classes['torch']])
    elif 'tensorflow.' in t: ret = ('ops.Tensor' in t)
    else: ret = False

    if not ret: 
        log (f'shape_cache: Not is_tensor: {t}', style='red')

    return ret

class ShapeCache:
    def __init__ (self, backend):
        self.var2shape = defaultdict(dict)
        self.func2ann = defaultdict(dict) # forward -> {lineno: shape}
        self.sz2name = None

        self.BE = get_backend_by_name(backend)

    def make_decl_map (self):
        if self.sz2name is None:
            decl_dvs = get_decls().values()
            self.sz2name = {dv.size: dv.shortname for dv in decl_dvs}

    def get_shape(self, val):
        self.make_decl_map()
        shape = self.BE.shape(val)
        shape_ann = [self.sz2name[s] if s in self.sz2name else str(s) for s in shape]
        return shape, ','.join(shape_ann)

    def update_var_shape(self, v, val, func_name, filename, lineno, show=False):
        if not is_tensor(val): return None

        #print ('update_var_shape', type(val))
        if not isinstance(val, (list, tuple) ):
            shape, shape_ann = self.get_shape(val)
        else:
            lenv = len(val)
            shape, shape_ann = self.get_shape(val[0])
            shape = (lenv, shape)
            shape_ann = (lenv, shape_ann)

        self.var2shape[func_name][v] = shape
        self.func2ann[func_name+','+filename][lineno] = (shape_ann, v)
        if show:
            log(f'update at line {lineno}: shape of {v} = {shape_ann}')
        return shape

    def shape_check (self, v, shape_ann, func_name, lineno, verbose=True):
        cache = self.var2shape[func_name]
        assert v in cache
        store_shape = tuple(cache[v])
        #shape = resolve_to_int_tuple(shape)
        #print (type(shape[0]))
        if store_shape == shape_ann:
            log (f'>> shape check succeeded at line {lineno}', style='green')
        else:
            log (f'>> FAILED shape check at line {lineno}', style='red')
            log (f'expected: {shape_ann}, actual: {store_shape}', style='red')
            #assert False

    def save(self, fname):
        print (f'saving shapes to {fname} ..')
        json_obj = (dict(self.func2ann))
        with open(fname, "w", encoding='utf-8') as of:
            json.dump(json_obj, of, indent=2)

