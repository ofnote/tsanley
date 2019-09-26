import astpretty
from typed_ast import ast3 as ast
import sympy

def is_tsalib_annotation(e):
    return True

def aop(op, e1, e2):
    if isinstance(op, ast.FloorDiv): res = e1 // e2
    elif isinstance(op,ast.Div): res = e1 / e2
    elif isinstance(op, ast.Mult): res = e1 * e2
    elif isinstance(op, ast.Add): res = e1 + e2
    else: 
        print (f'op not handled {op}')
        assert False
    return res

def expr2ann(e):
    #print (f'expr2ann: {e}')
    #astpretty.pprint(e)

    #if not is_tsalib_annotation(e): return None

    ann = None
    if isinstance(e, ast.Tuple):
        ann = [expr2ann(el) for el in e.elts]
        ann = tuple(ann)
    elif isinstance(e, ast.Num):
        ann = e.n
    elif isinstance(e, ast.Name):
        #print 'eval_expr_val: ast.Name', e.id, type(e.id)
        if e.id.isdigit() or e.id in ['True', 'False', 'None']: 
            ann = e.id
        else: 
            ann = sympy.Symbol(e.id)
    elif isinstance(e, ast.BinOp):
        lhs = expr2ann(e.left)
        r = expr2ann(e.right)
        ann = aop(e.op, lhs, r)

    elif isinstance(e, ast.Str):
        ann = e.s
    else:
        print ('expr2ann: Not handled: ', type(e))
        #assert False
    return ann
