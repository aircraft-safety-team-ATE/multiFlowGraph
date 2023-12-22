import numpy as np
from scipy.sparse import coo_matrix

def _cal_failure(D_mat, p_test, eps=1e-20):
    return 1 - np.exp(D_mat.dot(np.log(1-p_test*(1-eps))[:,None]))

def _cal_fuzzy(D_mat, p_fault, eps=1e-20):
    ## ε-slack
    D_mat = D_mat.tocsr()
    logc_p_fault = np.log(1-p_fault*(1-eps))
    D_mat_bool = (D_mat > eps).tocsr()
    p_eff = np.exp(D_mat.T.dot(logc_p_fault)*(1-eps))
    D_eff = (D_mat_bool._sub_sparse(D_mat))\
            ._divide_sparse(
                D_mat_bool._add_sparse(D_mat.multiply(logc_p_fault).expm1())
                )
    D_eff -= D_mat_bool
    return 1 - np.exp(D_eff.dot(np.log(1-p_eff*(1-eps))) + np.log(1-p_eff*(1-eps)).sum())

def cal_failure_fuzzy(D_mat, p_test, eps=1e-20, n_round=5):
    p_fault = _cal_failure(D_mat, p_test, eps=eps)
    p_fuzzy = _cal_fuzzy(D_mat, p_fault, eps=eps)
    return np.round(p_fault.flatten(), n_round), np.round(p_fuzzy.flatten(), n_round)

if __name__ == "__main__":
    import time
    import matplotlib.pyplot as plt
    
    def gene_D_p(n_e, n_p=1.2):
        n_t = round(10**n_e)
        n_f = round(3*n_t**n_p)
        D_mat = coo_matrix(([1.0]*(n_f*5), (np.random.permutation(n_f*5)%n_f, np.random.permutation(n_f*5)%n_t)), shape=(n_f, n_t))
        return D_mat, np.random.uniform(0,1, [n_t])

    n_inner = 10
    time_reg = []
    # for n in np.arange(1,4,0.1)[:-1]:
    #     time_reg.append(0)
    #     for _ in range(n_inner):
    D_mat, p_test = gene_D_p(1)
    print("D_mat.shape:", D_mat.shape)
    print("D_mat",D_mat)
    print("p_test.shape:", p_test.shape)
    print("p_test", p_test)
    # t = time.time()
    res = cal_failure_fuzzy(D_mat, p_test)
    # print("res.shape:", res.shape)  
    print("res:", res)

            # time_reg[-1] += (time.time()-t)*1000/n_inner

    # plt.figure()
    # plt.plot(np.round(10**np.arange(1,4,0.1)[:-1]), time_reg)
    # plt.xlabel("N")
    # plt.ylabel("time_step[ms]")
    # plt.show()
