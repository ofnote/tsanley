

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
    init_analyzer(trace_func_names=['f1', 'f2'], show_updates=True)

    test_func()




if __name__ == '__main__':
    test()