import numpy as np
import tensorflow as tf

def _cal_failure(D_mat, p_test, eps=1e-20):
    return tf.reduce_prod(1-D_mat*(1-p_test), axis=1)

def _cal_fuzzy(D_mat, p_fault, eps=1e-20):
##    ## ideal formula
##    E_mat = tf.eye(D_mat.shape[0])
##    return np.around(tf.reduce_prod(1- \
##                                    tf.reduce_prod(1-(D_mat[:,None,:]*D_mat[None,:,:]-E_mat[:,:,None])*p_fault[None,:,None],axis=1),
##                                    axis=1).numpy(), n_round=5)

    ## ε-slack
    Dp = 1 - D_mat*p_fault[:,None]*(1-eps)
    return tf.reduce_prod(
        1 - D_mat/Dp*tf.reduce_prod(Dp,axis=0),
        axis=1)

def cal_failure_fuzzy(D_mat, p_test, eps=1e-20, n_round=5):
    p_fault = _cal_failure(D_mat, p_test, eps=eps)
    p_fuzzy = _cal_fuzzy(D_mat, p_fault, eps=eps)
    return tf.round(p_fault, n_round).numpy(), tf.round(p_fuzzy, n_round).numpy()

if __name__ == "__main__":
    import time
    import matplotlib.pyplot as plt
    
    def gene_D_p(n_e, n_p=1.2):
        n_t = round(10**n_e)
        n_f = round(3*n_t**n_p)
        indices = [list(itm) for itm in zip(np.random.permutation(n_f*5)%n_f, np.random.permutation(n_f*5)%n_t)]
        D_mat = tf.tensor_scatter_nd_update(
            tf.zeros((n_f, n_t)),
            indices,
            [1]*len(indices))
        return D_mat, tf.random.uniform([n_t])

    n_inner = 10
    time_reg = []
    for n in np.arange(1,4,0.1)[:-1]:
        time_reg.append(0)
        for _ in range(n_inner):
            D_mat, p_test = gene_D_p(n)
            t = time.time()
            cal_failure_fuzzy(D_mat, p_test)
            time_reg[-1] += (time.time()-t)*1000/n_inner

    plt.figure()
    plt.plot(np.round(10**np.arange(1,4,0.1)[:-1]), time_reg)
    plt.xlabel("N")
    plt.ylabel("time_step[ms]")
    plt.show()
