import numpy as np
import math as m
from solver_Axb import *


def step_generator(future, time, heigh):
    ref = np.zeros(future)

    if len(heigh) != len(time):
        return None

    for i in range(future):
        for j in range(len(time)):
            if time[j] <= i:
                ref[i] = heigh[j]

    return ref

# Parâmetros do sistema
alpha       = 0.8           # constante de tempo
y0          = 2             # condição inicial
WINDOW      = 20            # janela de previsao
N           = 100           # tempo de simulação
LEN_STEP    = N + WINDOW    # número de passos

# arrays de dados
k_arr   = [i for i in range(LEN_STEP)]
u       = np.zeros(LEN_STEP)
q       = u.copy()
#w       = u.copy()

# perturbação
STEPS_Q = [1, 0, 1, 0, 1, 0, -1, 0, -1, 0, 2, 0]
STEPS_T = [10, 11, 20, 21, 30, 31, 40, 41, 50, 51, 60, 61]
q = step_generator(LEN_STEP, STEPS_T, STEPS_Q)

# referência
STEPS_W = [3, -2, 1, -4, 5]
STEPS_T = [15, 30, 45, 60, 75]
w = step_generator(LEN_STEP, STEPS_T, STEPS_W)

# varivais para animar o sistema
u_hist  = []
f_hist  = []
y_hat   = []

last_y0 = y0
for k in range(1, N):
    # calcula a saída do sistema
    y = calculate_response(N+1, alpha, u, q) + y0

    # atualiza a saída do sistema
    last_y0 = y[k]

    # define o tempo passado com limite de janela de previsão
    past_time = 0 if k <= WINDOW else k - WINDOW

    # define o vetor de controle passado
    past_u = u[past_time:k].copy()

    # free response (ele completa os valores passado de u com zero)
    free_foward = calc_free_foward(last_y0, alpha, past_u, WINDOW)

    # calcula a ação de controle com base na predicao
    delta_u = solver(alpha, free_foward, w[k:k+WINDOW])

    # salva a predição para plotar
    y_future = calculate_response(WINDOW, alpha, delta_u, q[k:k+WINDOW]) + last_y0
    u_hist.append(delta_u.copy())
    y_hat.append(y_future)
    f_hist.append(free_foward.copy())
    
    # atualiza ação de controle
    u[k] = delta_u[0] # if abs(delta_u[0]) <= 1 else delta_u[0]/abs(delta_u[0])

y = calculate_response(LEN_STEP, alpha, u, q) + y0
animate_system(k_arr, y, u, q, w, N, u_hist, f_hist, y_hat)