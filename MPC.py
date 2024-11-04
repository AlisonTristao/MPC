import numpy as np
import math as m
from solver_Axb import *

def gerar_referencias_degrau(N, amplitudes, inicios):
    referencia = np.zeros(N)

    if len(amplitudes) != len(inicios):
        raise Exception("amplitudes e inicios devem ter o mesmo tamanho")

    for i in range(N):
        for j in range(len(inicios)):
            if inicios[j] <= i:
                referencia[i] = amplitudes[j]

    return referencia

# constantes
alpha   = 0.8
y0      = 5
WINDOW  = (int(m.log(1e-3) / m.log(alpha)))
N       = 100

# arrays de dados
k       = [i for i in range(N)]
q       = np.zeros(N)
u       = q.copy()
w       = np.concatenate((np.ones(int(N/2)), np.ones(int(N/2))*4))

# Arrays de dados
k = [i for i in range(N)]
q = np.zeros(N)
u = q.copy()
N = 100
w = gerar_referencias_degrau(N, [1, 2, -3, 4], [10.0, 30, 40, 60])

# Resposta ao degrau
for t in range(N-WINDOW):
    # controles passados e atuais
    current_u = u[:t+WINDOW].copy()
    current_q =  q[:t+WINDOW].copy()

    # calcula a resposta futura de acordo com controles passados
    free_foward = calculate_response(WINDOW+t, alpha, y0, current_u, current_q)

    # corta do segundo item em diante
    free_foward = free_foward[t:t+WINDOW]

    # resove o sistema
    delta_u = solver(alpha, free_foward, w[t:t+len(free_foward)], LAMBDA=0.7)

    y = calculate_response(len(free_foward), alpha, free_foward[0], delta_u, q[t:t+len(free_foward)])

    # atualiza os controles
    u[t] = delta_u[0]

print("pronto")
y = calculate_response(N-WINDOW, alpha, y0, u[:N-WINDOW], current_q[:N-WINDOW])
animate_system(k[:N-WINDOW], y, q[:N-WINDOW], u[:N-WINDOW], w[:N-WINDOW], N-WINDOW, t)