#!/usr/bin/env python

from typed_ast import ast3 as ast
import astpretty
#import astunparse
import typed_astunparse
#https://pypi.org/project/typed-astunparse/


class Annotator(ast.NodeTransformer):
    def __init__ (self, line2shape):
        self.line2shape = line2shape

    def visit_Assign(self, node):
        #astpretty.pprint(node)
        #Assign(expr* targets, expr value)
        #AnnAssign(expr target, expr annotation, expr? value, int simple)

        res = node
        targets, value = node.targets, node.value
        lineno = node.lineno
        if lineno in self.line2shape:
            assert len(targets) == 1
            target = targets[0]
            shape = self.line2shape[lineno]
            ann = ast.Str(s=f'{shape}', kind='', lineno=lineno, col_offset=node.col_offset)
            #print("\n===>", astpretty.pprint(node, indent=' '))
            res = ast.AnnAssign(target=target, annotation=ann, value=value, simple=1, 
                        lineno=lineno, col_offset=node.col_offset)

        return res

def annotate(fname, outfname, line2shape, debug=False):
    tree = ast.parse(open(fname).read())
    #astpretty.pprint (tree)

    ann = Annotator(line2shape)
    tree = ann.visit(tree)

    if debug:
        print (line2shape)

    #treestr = astpretty.pformat(tree)
    #astpretty.pprint (tree)
    code = typed_astunparse.unparse(tree)
    #print (code)
    print (f'Writing to annotated file {outfname}')
    with open(outfname, 'w') as f:
        f.write(code)

import json
def parse_shape_file (shape_log_file):
    line2shape = {}
    with open(shape_log_file, 'r') as fp:
        shape_log = json.load(fp)

        for func, vals in shape_log.items():
            for lineno, rhs in vals.items(): #rhs = ['b,t', 'varname']
                line2shape[int(lineno)] = rhs[0]
    return line2shape


from dataclasses import dataclass
from pathlib import Path

@dataclass
class AnnotatorConfig:
    fname: str
    outfname: str = None
    shape_log_file: str = None #'/tmp/shape_log.json'


    def __post_init__(self):
        if self.shape_log_file is None:
            self.shape_log_file = '/tmp/shape_log.json'
        
        self.fname = Path(self.fname).resolve()     
        if self.outfname is None:   
            parent, name = self.fname.parent, self.fname.parts[-1]
            self.outfname = parent / f'tsa_{name}'
        else:
            self.outfname = Path(self.outfname).resolve()

    def annotate(self, debug=False):
        line2shape = parse_shape_file(self.shape_log_file)
        annotate(self.fname, self.outfname, line2shape, debug=debug)






