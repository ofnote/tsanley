from tsalib.ts import get_decls
from tsalib.ts import get_dim_vars_by_long_name

def get_dimvar_subst_map ():
    from sympy import Symbol
    decls = get_decls()
    subst_map = {}
    for k, dv in decls.items():
        subst_map[Symbol(dv._name)] = dv._val
    return subst_map

def resolve_ann_in_frame(ann, frame):
    '''def eval(a, ):
        if isinstance(a, int): return a
        if astr in frame.f_globals: return frame.f_globals[astr]
        elif astr in frame.f_locals: return frame.f_locals[astr]
        else:
            assert False, f'not found ann symbol: {a}'
    '''
    sub_map = get_dimvar_subst_map() # Batch: 10, 
    print (sub_map)
    ret = [e.subs(sub_map) if not isinstance(e, int) else e for e in ann]
    print (f'resolved from {ann} to {ret}')
    return ret



dname2expr = {}


def lookup_long_name (name):
    assert isinstance(name, str)
    if name not in dname2expr: 
        e = get_dim_vars_by_long_name(name)
    return dname2expr[e]