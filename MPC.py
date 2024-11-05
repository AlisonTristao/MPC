import numpy as np
from solver_Axb import *

# Parâmetros do sistema
alpha       = 0.8           # constante de tempo
y0          = 2             # condição inicial
WINDOW      = 30            # janela de previsao
N           = 100           # tempo de simulação
LEN_STEP    = N + WINDOW    # número de passos

# arrays de dados
k_arr   = [i for i in range(LEN_STEP)]
u       = np.zeros(LEN_STEP)
noise   = np.random.normal(0, 0.1, N)

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
y_hat   = []

for k in range(N):
    # calcula a saída do sistema
    y = calculate_response(N, alpha, u, q) + y0 + noise

    # define o tempo passado com limite de janela de previsão
    past_time = 0 if k <= WINDOW else k - WINDOW

    # define o vetor de controle passado
    past_u = u[past_time:k].copy()

    # free response (ele completa os valores passado de u com zero)
    free_foward = calc_free_foward(y[k], alpha, past_u, WINDOW)

    # calcula a ação de controle com base na predicao
    delta_u = solver(alpha, free_foward, w[k:k+WINDOW])

    # atualiza ação de controle
    u[k] = delta_u[0]

    # salva a predição para plotar
    y_future = calculate_response(WINDOW, alpha, delta_u, [])
    u_hist.append(delta_u)
    y_hat.append(y_future + free_foward)
    
y = calculate_response(LEN_STEP, alpha, u, q) + y0
animate_system(k_arr, y, u, q, w, N, u_hist, y_hat)