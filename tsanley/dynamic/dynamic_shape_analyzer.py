import sys
import os
import inspect

from pathlib import Path
from collections import defaultdict
from easydict import EasyDict as ED

from .trace_utils import get_function_name_from_frame
from typed_ast import ast3 as ast
from ..common.ast_utils import expr2ann
from ..common.log_utils import log, debug_log
from .shape_cache import ShapeCache

from tsalib.ts import get_decls
from tsalib.tsn import tsn_to_tuple, resolve_to_int_tuple


PY_HOME = str(Path(sys.executable).parents[1])
EXCLUDE_FILES = [PY_HOME]
EXCLUDE_CLASSES = ['DimVar', 'DimExpr']
DEBUG_LEVEL = 0


# stores 
GLOBALS = ED({})

def should_filter_call(filename, func_name):
    ret = False
    if filename is not None: 
        ret = any([x in filename for x in EXCLUDE_FILES])
        if ret: return ret
    if func_name is not None:
        ret = any([x in func_name for x in EXCLUDE_CLASSES])

    return ret

def eval_attribute (a):
    if isinstance(a.value, ast.Name):
        receiver = a.value.id
        ret = receiver + '.' + a.attr
    elif isinstance(a.value, ast.Attribute):
        prefix = eval_attribute(a.value)
        ret = prefix + '.' + a.attr
    else:
        import astpretty
        astpretty.pprint(a)
        print (f'{type(a.value)}')
        raise NotImplementedError

    return ret

def eval_lhs(lhs):
    res = None
    if isinstance(lhs, ast.Name):
        res = lhs.id
    elif isinstance(lhs, ast.Tuple):
        res = [l.id for l in lhs.elts if l]
    elif isinstance(lhs, ast.Attribute):
        res = eval_attribute (lhs)
    else:
        #raise NotImplementedError(f'{type(lhs)}')
        print (f'Not implemented eval lhs for {type(lhs)}')
    return res


def get_var_ann_from_stmt (stmt, frame):
    var, ann = None, None
    tree = None
    #print (f'get_var_ann_from_stmt: {stmt}')

    try:
        tree = ast.parse(stmt.strip())
        #astpretty.pprint(tree)
    except:
        if GLOBALS.debug:
            log (f'parse failed: {stmt}', style='green')

    if tree is not None and len(tree.body) > 0:
        assign = tree.body[0]
        if isinstance(assign, (ast.AnnAssign, ast.Assign) ):

            if isinstance(assign, ast.AnnAssign):
                #assign.target, assign.annotation
                ann = expr2ann(assign.annotation)
                if ann is not None:
                    if isinstance(ann, str):
                        ann = tsn_to_tuple(ann)
                    else:
                        assert False, f'unknown annotation format {ann}'
                    var = eval_lhs(assign.target)

            elif isinstance(assign, ast.Assign):
                assert len(assign.targets) == 1
                trg = assign.targets[0]
                lvars = eval_lhs(trg)
                if isinstance(lvars, str):
                    var = lvars
                elif isinstance(lvars, (list, tuple)):
                    var = lvars[0]
                    if len(lvars) > 1:
                        log (f'lvars = {lvars}')
                        log ('WARN: only supporting single lhs tensor assignments')

    return var, ann

def get_var_shape (var, frame):
    if '.' not in var:
        var_shape = frame.f_locals[var]
    else:
        ap = var.split('.')
        #assert len(ap) == 2 #TODO: generalize
        #if len(ap) > 2: print (frame.f_locals)
        obj = frame.f_locals[ap[0]]
        for p in ap[1:]:
            obj = getattr(obj, p)
        var_shape = obj

        if len(ap) > 2: print (var_shape)

    return var_shape



def analyze_stmt (last_exec_stmt, line_no, func_name, filename, frame, trb):
    debug = GLOBALS.debug
    check_tsa = GLOBALS.check_tsa
    shape_cache = GLOBALS.shape_cache

    var, ann = get_var_ann_from_stmt(last_exec_stmt, frame)
    #the current shape of x (named var) corresponds to post-execution of prev statement
    # so we can check prev stmt's ann against x's shape
    if debug: log (f'>> var, ann : {var}, {ann}')

    if var is not None:
        debug_log (f'\n({func_name}:{line_no}), var={var}', trb.index, level=DEBUG_LEVEL)
        #print (frame.f_locals)

        var_shape = get_var_shape(var, frame)
        shape_cache.update_var_shape(var, var_shape, func_name, filename, line_no, 
                        show=GLOBALS.show_updates)
        
        if ann is not None and check_tsa:
            shape_cache.shape_check(var, ann, func_name, line_no)

def get_earlier_exec_stmts (last_exec_line, curr_line, frame):
    global GLOBALS
    debug = GLOBALS.debug

    co_src = inspect.getsourcelines(frame.f_code)
    stmt_list, first_line = co_src

    curr_idx = (curr_line - first_line) 
    if last_exec_line is None: 
        last_exec_line = curr_line - 1
    last_idx = (last_exec_line - first_line)
    earlier_stmts = [(first_line + i, stmt_list[i]) for i in range(last_idx, curr_idx)]

    if debug:
        log (last_exec_line, curr_line, last_idx, curr_idx, earlier_stmts, style='bold')
    return earlier_stmts

def trace_lines(frame, event, arg):
    global GLOBALS
    debug = GLOBALS.debug
    shape_cache = GLOBALS.shape_cache

    if debug:
        print (f'\n==> tracelines: event = {event}')
    
    if event == 'line': 
        context_pos = 0
    elif event == 'return': 
        context_pos = -1

    else:
        raise NotImplementedError(f'trace_lines: unknown event {event}')

    #co = frame.f_code
    #func_name = co.co_name
    #print ('varnames: ', co.co_varnames, co.co_freevars)
    co_src = inspect.getsourcelines(frame.f_code)

    filename = frame.f_code.co_filename
    #curr_line = curr_line - 1 - context_pos
    curr_line = frame.f_lineno
    func_name = get_function_name_from_frame(frame)

    if debug:
        log (f'trace_lines: function "{func_name}", executing line {curr_line}')
        log(f'code {co_src[0]}')

    trb = inspect.getframeinfo(frame, context=1)
    #print (trb)
    #code_context = trb.code_context
    #curr_line = code_context[trb.index]
    #print ('globals: ', frame.f_globals )

    if event == 'return': curr_line += 1 #allow tracking the last line before return

    stmts = get_earlier_exec_stmts (GLOBALS.last_exec_line, curr_line, frame)
    for stmt_line, stmt in stmts:
        analyze_stmt (stmt, stmt_line, func_name, filename, frame, trb)

    GLOBALS.last_exec_line = curr_line

    if event == 'return':
        shape_cache.save('/tmp/shape_log.json')
        GLOBALS.last_exec_line = None # function returns, so stop keeping track

    if event != 'line':
        #print (f'tracelines: event = {event}')
        return


    
    '''
    frame_mem = inspect.getmembers(frame)
    for name, v in frame_mem:
        #print (name)
        if name == 'f_locals':
            print (name, v)
    '''


import fnmatch

def trace_calls(frame, event, arg):
    global GLOBALS
    TRACE_INTO = GLOBALS.trace_into
    debug = GLOBALS.debug

    #print (frame, event, arg, frame.f_code.co_name)
    if event == 'call':
        co = frame.f_code
        func_name = co.co_name
        if func_name == 'write':
            # Ignore write() calls from print statements
            return
        func_name = get_function_name_from_frame(frame)
        #if func_name in TRACE_INTO:
        #    debug_log (f'> trying {func_name}, {co.co_filename}')

        curr_line = frame.f_lineno
        filename = co.co_filename
        #log (f'>> call to {func_name} on line {curr_line} of {filename}')

        if should_filter_call(filename, func_name): return 
        #log (f'>> call to {func_name} on line {curr_line} of {filename}: {TRACE_INTO}')


        matched = False
        if len(TRACE_INTO) == 0: matched = True
        else:
            matched = any([fnmatch.fnmatch(func_name, pat) for pat in TRACE_INTO])
        #if len(TRACE_INTO) == 0 or func_name in TRACE_INTO or 'forward' in func_name:
        if matched:
            # Trace into this function
            log(f'\n> Analyzing function {func_name}')
            GLOBALS.last_exec_line = None #TODO: push curr_line on stack
            return trace_lines
        #return trace_calls
    elif event == 'return':
        debug_log (f'return {frame.f_code.co_name}')

        assert False



def init_analyzer(trace_func_names=['main'], check_tsa=True, show_updates=True, debug=False, backend='pytorch'):
    global GLOBALS
    GLOBALS.debug = debug
    GLOBALS.shape_cache = ShapeCache(debug, backend)
    GLOBALS.trace_into = trace_func_names
    GLOBALS.check_tsa = check_tsa
    GLOBALS.show_updates = show_updates
    GLOBALS.last_exec_line = None

    #global SIZE2NAME
    #assert False

    sys.settrace(trace_calls)





#if __name__ == '__main__':
#    main()















