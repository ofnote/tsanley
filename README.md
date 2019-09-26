# tsanley
A shape analyzer for tensor programs, using popular tensor libraries: `tensorflow`, `pytorch`, `numpy`, ...

Builds upon a library [tsalib](https://github.com/ofnote/tsalib) for specifying, annotating and transforming tensor shapes using **named dimensions**.

### Quick Start

`tsanley` discovers shape errors at runtime by checking the runtime tensor shapes with the user-specified shape annotations. Tensor shape annotations are specified in the `tsalib` shape shorthand notation, e.g., `x: 'btd'`.

More details on the shorthand format [here](https://github.com/ofnote/tsalib/blob/master/notebooks/shorthand.md).

```python
def func(x):
    x: 'b,t,d' #shape check: ok!
    y: 'b,d' = x.mean(dim=0) #error: dim should be 1
    #   ^ 
    #   | tsanley detects shape violation

    z: 'b,d' = x.mean(dim=1) #shape check: ok!

def test_func():
    import torch
    from tsalib import get_dim_vars

    # get the declared dimension sizes: 10, 100, 1024
    B, L, D = get_dim_vars('b t d') 
    x = torch.Tensor(B, L, D)
    func(x)

def test():
    #declare the named dimension variables using the tsalib api
    from tsalib import dim_vars
    dim_vars('Batch(b):10 Length(t):100 Hidden(d):1024')

    # initialize tsanley's dynamic shape analyzer
    from tsanley.dynamic import init_analyzer
    init_analyzer(trace_func_names=['func'], show_updates=True) #check_tsa=True, debug=False

    test_func()

if __name__ == '__main__': test()
```

On executing the above program, `tsanley` tracks shapes of tensor variables (`x`, `y`, `z`) in function `func` and reports shape check successes and failures.

See complete examples in [models](models/) directory.

### Installation

```
pip install tsanley
```

### Status: Experimental

`tsanley` performs a best-effort shape tracking during

Tested with `pytorch` examples. `tensorflow` and `numpy` programs should also work (`tsalib` supported backends).