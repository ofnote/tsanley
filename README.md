# tsanley
![experimental](https://img.shields.io/badge/stability-experimental-orange.svg)

A shape analyzer for tensor programs, using popular tensor libraries: `tensorflow`, `pytorch`, `numpy`, ...

Builds upon a library [tsalib](https://github.com/ofnote/tsalib) for specifying, annotating and transforming tensor shapes using **named dimensions**.

### Quick Start

`tsanley` discovers shape errors at runtime by checking the runtime tensor shapes with the user-specified shape annotations. Tensor shape annotations are specified in the `tsalib` shape shorthand notation, e.g., `x: 'btd'`.

More details on the shorthand format [here](https://github.com/ofnote/tsalib/blob/master/notebooks/shorthand.md).

#### Example

Suppose we have the following functions `foo` and `test_foo` in our existing code. To setup `tsanley`, we add the following code *before* `test_foo` is called (`test` function):

- Declare the named dimension variables (using `dim_vars`) -- these help specify the expected shape of tensor variables used in the code. For example, here we declare 3 dimension variables, referred to via shorthand names `b`, `t`, `d`. We use these shorthand names to label variables and check their shapes in one or more functions, e.g., `foo` here.
- Initialize the `tsanley` analyzer by calling `init_analyzer`: parameter `trace_func_names` takes a list of function names as Unix shell-style wildcards (using the `fnmatch` library).

```python
def foo(x):
    x: 'b,t,d' #shape check: ok!              [line 36]
    y: 'b,d' = x.mean(dim=0) #error: dim should be 1  [line 37]
    #   ^ 
    #   | tsanley detects shape violation

    z: 'b,d' = x.mean(dim=1) #shape check: ok! [line 38]

def test_foo():
    import torch
    from tsalib import get_dim_vars

    # get the declared dimension sizes: 10, 100, 1024
    B, L, D = get_dim_vars('b t d') 
    x = torch.Tensor(B, L, D)
    foo(x)

def test():
    #declare the named dimension variables using the tsalib api
    from tsalib import dim_vars
    dim_vars('Batch(b):10 Length(t):100 Hidden(d):1024')

    # initialize tsanley's dynamic shape analyzer
    from tsanley.dynamic import init_analyzer
    init_analyzer(trace_func_names=['foo'], show_updates=True) #check_tsa=True, debug=False

    test_foo()

if __name__ == '__main__': test()
```

On executing the above program, `tsanley` tracks shapes of tensor variables (`x`, `y`, `z`) in function `foo` and reports shape check successes and failures.

#### Output

```bash
> Analyzing function foo 
  
Update at line 36: actual shape of x = b,t,d 
  >> shape check succeeded at line 36 
  
Update at line 37: actual shape of y = t,d 
  >> FAILED shape check at line 37 
  expected: (d:1024,), actual: (100, 1024) 
  
Update at line 38: actual shape of z = b,d 
  >> shape check succeeded at line 38 
saving shapes to /tmp/shape_log.json ..
```


See examples in [models](models/) directory.

### Installation

```
pip install tsanley
```

### Status: Experimental

`tsanley` performs a best-effort shape tracking when the program runs. Here are a few tricky scenarios:

- calling same function multiple times -- shape values from only the last call are cached.
- recursive calls -- not handled.

Tested with `pytorch` examples. `tensorflow` and `numpy` programs should also work (`tsalib` supported backends).