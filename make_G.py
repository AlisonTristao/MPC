from solver_Axb import *

alpha = 0.4
N = 15

G = matrix_G(N, alpha)

free_foward = calc_free_foward(0, alpha, [3, 0, 2], N)

print(free_foward)