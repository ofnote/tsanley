

def f1(x):
    dim = 0
    x: 'b,t,d'
    y: 'b,d' = x.mean(dim=dim) #error: dim should be 1
    #   ^ 
    #   | tsanley detects shape violation

def f2(x):
    dim = 1
    x: 'b,t,d'
    y: 'b,d' = x.mean(dim=dim) #all shape checks passed

def test_func():
    import torch
    from tsalib import get_dim_vars

    B, L, D = get_dim_vars('b t d')
    x = torch.Tensor(B, L, D)
    f1(x) #error
    f2(x) #success

def test():
    #declare the main named dimension variables using tsalib api
    #recall these values anywhere in the program using `get_dim_vars`
    from tsalib import dim_vars
    dim_vars('Batch(b):10 Length(t):100 Hidden(d):1024')

    from tsanley.dynamic import init_analyzer
    init_analyzer(trace_func_names=['f*'], show_updates=True)

    test_func()

def foo(x):
    x: 'b,t,d' #shape check: ok!
    y: 'b,d' = x.mean(dim=0) #error: dim should be 1
    z: 'b,d' = x.mean(dim=1) #shape check: ok!

def test_foo():
    import torch
    from tsalib import get_dim_vars

    # get the declared dimension sizes: 10, 100, 1024
    B, L, D = get_dim_vars('b t d') 
    x = torch.Tensor(B, L, D)
    foo(x)

def test2():
    #declare the named dimension variables using the tsalib api
    from tsalib import dim_vars
    dim_vars('Batch(b):10 Length(t):100 Hidden(d):1024')

    # initialize tsanley's dynamic shape analyzer
    from tsanley.dynamic import init_analyzer
    init_analyzer(trace_func_names=['foo'], show_updates=True, debug=False) #check_tsa=True, debug=False

    test_foo()



if __name__ == '__main__':
    test2()