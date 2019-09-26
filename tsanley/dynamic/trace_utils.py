

import opcode

def tracer(frame, event, arg):
    if event == 'return':
        if arg is not None or (opcode.opname[frame.f_code.co_code[frame.f_lasti]]
                               in ('RETURN_VALUE', 'YIELD_VALUE')):
            print('exit via return', arg)
        else:
            print('exit via exception')

# copied from https://github.com/dropbox/pyannotate/blob/master/pyannotate_runtime/collect_types.py

# TODO: Make this faster
def get_function_name_from_frame(frame):
    # type: (Any) -> str
    """
    Heuristic to find the class-specified name by @guido
    For instance methods we return "ClassName.method_name"
    For functions we return "function_name"
    """

    def bases_to_mro(cls, bases):
        # type: (type, List[type]) -> List[type]
        """
        Convert __bases__ to __mro__
        """
        mro = [cls]
        for base in bases:
            if base not in mro:
                mro.append(base)
            sub_bases = getattr(base, '__bases__', None)
            if sub_bases:
                sub_bases = [sb for sb in sub_bases if sb not in mro and sb not in bases]
                if sub_bases:
                    mro.extend(bases_to_mro(base, sub_bases))
        return mro

    code = frame.f_code
    # This ought to be aggressively cached with the code object as key.
    funcname = code.co_name
    if code.co_varnames:
        varname = code.co_varnames[0]
        if varname == 'self':
            inst = frame.f_locals.get(varname)
            if inst is not None:
                try:
                    mro = inst.__class__.__mro__
                except AttributeError:
                    mro = None
                else:
                    try:
                        bases = inst.__class__.__bases__
                    except AttributeError:
                        bases = None
                    else:
                        mro = bases_to_mro(inst.__class__, bases)
                if mro:
                    for cls in mro:
                        bare_method = cls.__dict__.get(funcname)
                        if bare_method and getattr(bare_method, '__code__', None) is code:
                            return '%s.%s' % (cls.__name__, funcname)
    return funcname



def _trace_dispatch(frame, event, arg):


    if not tracking:
        return

    #print ('event - ', event, arg)

    code = frame.f_code
    key = id(code)
    n = sampling_counters.get(key, 0)
    if n is None:
        return

    if event == 'call':
        # Bump counter and bail depending on sampling sequence.
        sampling_counters[key] = n + 1

    elif event == 'return':
        if key not in call_pending:
            return
        call_pending.discard(key) 
    else:
        return 


    filename = _filter_filename(code.co_filename)
    if filename:
        func_name = get_function_name_from_frame(frame)
        print (filename, func_name, code.co_firstlineno)
        print (code)




'''
from decorator import decorator
from line_profiler import LineProfiler

@decorator
def profile_each_line(func, *args, **kwargs):
    profiler = LineProfiler()
    profiled_func = profiler(func)
    try:
        profiled_func(*args, **kwargs)
    finally:
        profiler.print_stats()
'''

'''
# Array of counters indexed by ID of code object.
sampling_counters = {}  # type: Dict[int, Optional[int]]
# IDs of code objects for which the previous event was a call (awaiting return).
call_pending = set()  # type: Set[int]

def _filter_types(types_dict):
    # type: (Dict[FunctionKey, T]) -> Dict[FunctionKey, T]
    """Filter type info before dumping it to the file."""

    def exclude(k):
        # type: (FunctionKey) -> bool
        """Exclude filter"""
        return k.path.startswith('<') or k.func_name == '<module>'

    return {k: v for k, v in types_dict.items() if not exclude(k)}
'''
