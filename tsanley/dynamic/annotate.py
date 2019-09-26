from typed_ast import ast3 as ast

import astpretty
#import rope
import astunparse
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
            ann = ast.Str(s=f'{shape}', kind='')
            res = ast.AnnAssign(target, ann, value, 1)

        return res

def annotate(fname, outfname, line2shape):
    tree = ast.parse(open(fname).read())

    ann = Annotator(line2shape)
    tree = ann.visit(tree)

    treestr = astpretty.pformat(tree)
    #print (treestr)
    code = typed_astunparse.unparse(tree)
    #print (code)
    with open(outfname, 'w') as f:
        f.write(code)

import json
def parse_shape_file (shape_file):
    line2shape = {}
    with open(shape_file, 'r') as fp:
        shape_log = json.load(fp)

        for func, vals in shape_log.items():
            for lineno, rhs in vals.items(): #rhs = ['b,t', 'varname']
                line2shape[int(lineno)] = rhs[0]
    return line2shape


from dataclasses import dataclass
from pathlib import Path

@dataclass
class Config:
    fname: str
    outfname: str = None
    shape_file: str = '/tmp/shape_log.json'


    def __post_init__(self):
        self.fname = Path(self.fname).resolve()     
        if self.outfname is None:   
            parent, name = self.fname.parent, self.fname.parts[-1]
            self.outfname = parent / f'tsa_{name}'
        else:
            self.outfname = Path(self.outfname).resolve()

    def annotate(self):
        line2shape = parse_shape_file(self.shape_file)
        annotate(self.fname, self.outfname, line2shape)


if __name__ == '__main__':
    #fname = '../models/effnet.py'
    C1 = Config(fname='~/Projects/tsa-models/pytorch-pretrained-BERT/pytorch_pretrained_bert/modeling.py')

    C1.annotate()






