# tsanley 

Tsanley is a shape analyzer for tensor programs, using popular tensor libraries: `tensorflow`, `pytorch`, `numpy`. Plugs into your existing code seamlessly, with minimal changes.

Builds upon the library [tsalib](https://github.com/ofnote/tsalib) for specifying, annotating and transforming tensor shapes using **named dimensions**. 

### Quick Start

`tsanley` discovers shape errors at runtime by checking the runtime tensor shapes against the user-specified shape annotations. Tensor shape annotations are specified in the `tsalib` shape shorthand notation, e.g., `x: 'btd'`.

More details on the shorthand format [here](https://github.com/ofnote/tsalib/blob/master/notebooks/shorthand.md).

#### Example

Suppose we have the following functions `foo` and `test_foo` in our existing code. To setup `tsanley` analyzer for shape checking in `foo`, we add a function `setup_named_dims` *before* calling `test_foo`, label tensor variables by their expected shorthand shapes (e.g., `b,d`) and then execute the code normally.


```python
def foo(x):
    x: 'b,t,d' #shape check: ok!               [line 36]
    y: 'b,d' = x.mean(dim=0)  # error!         [line 37]
    z: 'b,d' = x.mean(dim=1) #shape check: ok! [line 38]

def test_foo():
    import torch
    x = torch.Tensor(10, 100, 1024)
    foo(x)

def setup_named_dims():
    from tsalib import dim_vars
    #declare the named dimension variables using the tsalib api
    #e.g., 'b' stands for 'Batch' dimension with size 10
    dim_vars('Batch(b):10 Length(t):100 Hidden(d):1024')

    # initialize tsanley's dynamic shape analyzer
    from tsanley.dynamic import init_analyzer
    init_analyzer(trace_func_names=['foo'], show_updates=True) #check_tsa=True, debug=False


if __name__ == '__main__': 
    setup_named_dims()
    test_foo()
```

On executing the above program, `tsanley` tracks shapes of tensor variables (`x`, `y`, `z`) in function `foo` and reports following shape check results.

#### Output

```bash
> Analyzing function foo 
  
Update at line 36: actual shape of x = b,t,d 
  >> shape check succeeded at line 36 
  
Update at line 37: actual shape of y = t,d 
  >> FAILED shape check at line 37 
  expected: (b:10, d:1024), actual: (100, 1024) 
  
Update at line 38: actual shape of z = b,d 
  >> shape check succeeded at line 38 
saving shapes to /tmp/shape_log.json ..
```

#### What does setup_named_dims do?

- Declare the named dimension variables (using `dim_vars`) -- using them we can specify the expected shape of tensor variables in the code. For example, here we declare 3 dimension variables, `Batch`, `Length` and `Hidden`, and refer to them via shorthand names `b`,`t`, `d`. 
- We use shorthand names to label tensor variables and check their shapes in one or more functions, e.g., `foo` here.
- Initialize the `tsanley` analyzer by calling `init_analyzer`: parameter `trace_func_names` takes a list of function names as Unix shell-style wildcards (using the `fnmatch` library). We can specify names with wildcards, e.g., `Resnet.*` to track all functions in the `Resnet` class.

See examples in [models](models/) directory.

### Installation

```
pip install tsanley
```

### Annotation

`tsanley` can also annotate tensor variables in existing *executable* code with shape labels. This is useful when trying to understand external open-source code or labeling one's own code.

Suppose, we have some un-annotated code residing in file `model.py`.

1. First, generate *shape logs* by adding `setup_named_dims` to the `model.py`.
2. Execute `model.py`. The logs are stored in `/tmp/shape_log.json`.
2. Use the logs to annotate `model.py`.

#### Example
Let's revisit the earlier example, without our manual annotations. Suppose it resides in `model.py`.

```python
def foo(x):
    y = x.mean(dim=0) 
    z = x.mean(dim=1) 

def test_foo():
    import torch
    x = torch.Tensor(10, 100, 1024)
    foo(x)
```

We add `setup_named_dims` to the code, and execute it.

```python
def setup_named_dims():
    from tsalib import dim_vars
    #declare the named dimension variables using the tsalib api
    #e.g., 'b' stands for 'Batch' dimension with size 10
    dim_vars('Batch(b):10 Length(t):100 Hidden(d):1024')

    # initialize tsanley's dynamic shape analyzer
    from tsanley.dynamic import init_analyzer
    init_analyzer(trace_func_names=['foo'], show_updates=True, check_tsa=False) # debug=False

if __name__ == '__main__': 
    setup_named_dims()
    test_foo()
```

This generates the shape logs in `/tmp/shape_log.json`. Flag `check_tsa=False` ensures no shape checks are performed by `tsanley`.

Now, annotate `foo` with the command:

> tsa annotate -f model.py

The output is a file `tsa_model.py` with `foo` updated as follows:

```python
def foo(x):
    y: 't,d' = x.mean(dim=0) 
    z: 'b,d' = x.mean(dim=1) 
```

`tsanley` makes smart guesses to map runtime shape values (`100`) to the shorthand names (`t`). If we do not declare the dimension names using `dim_vars` in `setup_named_dims`, we get the following annotation:

```python
def foo(x):
    y: '100,1024' = x.mean(dim=0) 
    z: '10,1024' = x.mean(dim=1) 
```


### Status: Work-In-Progress

`tsanley` is a work in progress. It performs a best-effort shape tracking during program execution. Here are a few tricky scenarios:

- calling same function multiple times -- shape values from only the last call are cached.
- recursive calls -- not handled.

Tested with `pytorch` examples. `tensorflow` and `numpy` programs should also work (`tsalib` supported backends), but remain to be tested.

Try it out and open an issue if you spot a missing feature or run into problems.


