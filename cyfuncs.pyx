# This file holds several cython functions for use in the citation monte carlo exercise 

def cmean(list array):
    cdef int i, N=len(array)
    cdef float x, s=0.0
    for i in range(N):
        x = array[i]
        s += x
    return s/N

def cmake_haz(float x, float alpha, float beta):
    return alpha + beta * x

def cmake_field_haz(int field, int latent, float x, float alpha_0, float alpha_1, float alpha_2, float beta_d_0, float beta_d_1, float beta_d_2):
    if field == 0:
        return alpha_0 + beta_d_0 * x
    if field == 1 and latent == 0:
        return alpha_2 + beta_d_2 * x
    if field == 1 and latent == 1:
        return alpha_1 + beta_d_1 * x 

def cmult(float x):
    return x * 3.16888e-17

def cminex(float w1, float v1, float w0, float v0, float p):
    den = v0 + w0 - v1
    if den <= 0:
        return 1
    else:
        return min(pow(w1 / den, p), 1)

def cmaxex(float w1, float v1, float w0, float v0):
    return max(w1, v0 + w0 - v1)
