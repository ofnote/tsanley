import tensorflow as tf

def foo(x):
    x: 'b,t,d' #shape check: ok!
    y: 'b,d' = tf.reduce_mean(x, axis=0) #error: dim should be 1
    z: 'b,d' = tf.reduce_mean(x, axis=1) #shape check: ok!

    print (y)
    print (z)

def test_foo():
    from tsalib import get_dim_vars

    # get the declared dimension sizes: 10, 100, 1024
    B, L, D = get_dim_vars('b t d') 
    #x = tf.get_variable("x", [B, L, D])
    x = tf.Variable(tf.zeros([B, L, D]))
    foo(x)

def test2():
    #declare the named dimension variables using the tsalib api
    from tsalib import dim_vars
    dim_vars('Batch(b):10 Length(t):100 Hidden(d):1024')

    # initialize tsanley's dynamic shape analyzer
    from tsanley.dynamic import init_analyzer
    init_analyzer(trace_func_names=['foo'], show_updates=True, debug=False, backend='tensorflow') #check_tsa=True, debug=False

    test_foo()



if __name__ == '__main__':
    test2()