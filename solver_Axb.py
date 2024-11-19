import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

def animate_system(k, y, u, q, w, N, u_hist, y_hat):
    def update(frame):
        u_h = u_hist[frame] if frame < len(u_hist) else []
        y_h = y_hat[frame] if frame < len(y_hat) else []

        ax1.clear()
        ax2.clear()

        ax1.axvline(x=frame, color='gray', linestyle='--')
        ax2.axvline(x=frame, color='gray', linestyle='--')

        # Gráfico 1: (y) e (w) com previsão (f_hist) após o frame atual
        ax1.step(k[:frame], y[:frame], where="post", color="blue", label="y(k)")
        ax1.step(k, w, where="post", color="red", linestyle="--", label="w(k)")
        ax1.step(k[frame:frame+len(y_h)], y_h, where="post", color="green", linestyle="--", label="ŷ(k)")

        ax1.set_ylabel("ŷ e referência")
        ax1.set_xlim(0, N)
        ax1.set_ylim(min(min(y), min(w))-1, max(max(y), max(w))+1)
        ax1.grid(True)
        ax1.legend()
        ax1.set_title("y(k) e w(k)")

        # Gráfico 2: (q) e (u) com previsão (u_hist) após o frame atual
        ax2.step(k[:frame], q[:frame], where="post", color="orange", label="Δq(k)")
        ax2.step(k[:frame], u[:frame], where="post", color="purple", label="Δu(k)")
        ax2.step(k[frame:frame+len(u_h)], u_h, where="post", color="green", linestyle="--", label="Δû(k)")    
    
        ax2.set_ylabel("entradas")
        ax2.set_xlim(0, N)
        ax2.set_ylim(min(min(q), min(u))-1, max(max(q), max(u))+1)
        ax2.grid(True)
        ax2.legend()
        ax2.set_title("Δq(k) e Δu(k)")
        
        return ax1, ax2

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
    fig.tight_layout(pad=3.0)
    ani = FuncAnimation(fig, update, frames=N+1, repeat=False, interval=0)  # Ajuste feito em frames para N+1
    plt.show()

def step_generator(future, time, heigh):
    ref = np.zeros(future)

    if len(heigh) != len(time):
        return None

    for i in range(future):
        for j in range(len(time)):
            if time[j] <= i:
                ref[i] = heigh[j]

    return ref

def arr_complete(arr, N):
    # se nao for um array numpy transforma em um
    if type(arr) != np.ndarray:
        arr = np.array(arr)

    for _ in range(N - arr.shape[0]):
        arr = np.insert(arr, 0, 0)
    return arr

def resp_degrau(alpha, k):
    return (1 - alpha**k)

def matrix_G(N, alpha=0.8):
    # --- matriz de convolução ---
    G = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            if j <= i:
                G[i][j] = resp_degrau(alpha, i-j + 1)

    return G

def calculate_response(N, alpha=0.8, u=[], q=[]):
    # se não houver valores de u
    u = arr_complete(u, N)
    q = arr_complete(q, N)

    # --- matriz de convolução ---
    G = matrix_G(N, alpha)

    # --- resposta ao degrau + perturbacao ---
    y = np.dot(G, u[:N]) + np.dot(G, q[:N])

    return y

def solver(alpha, free_foward, w, LAMBDA=0.1):
    # --- solver ---
    G   = matrix_G(len(free_foward), alpha)
    Gt  = np.transpose(G)
    I   = np.identity(G.shape[0])
    
    # --- monta o sistema ---
    A   = np.dot(Gt, G) + LAMBDA*I
    b   = np.dot(Gt, w - free_foward)
    
    # --- resolve o sistema ---
    delta_u = np.linalg.solve(A, b)
    
    return delta_u

def calc_free_foward(y_t, alpha, u_past, window):
    free_foward = np.zeros(window)

    # valores em q gi tende a zero
    N_ss = int(np.log(1e-3) / np.log(alpha)) + 1

    # valores de g
    g = [resp_degrau(alpha, i) for i in range(N_ss + window)]

    # completa os valores de u passados com zero
    u_past = arr_complete(u_past, N_ss)

    # faz a predicao para toda a janela
    for j in range(window):
        # diferença entre os valores de g
        diff = np.zeros(N_ss) 
        for i in range(N_ss):
            diff[i] = g[j+i] - g[i]

        # soma de todas as diferenças multiplicadas pelos valores passados
        sum = 0
        for i in range(N_ss):
            sum += diff[i] * u_past[N_ss -i -1]
        
        # calcula o valor predito
        free_foward[j] = sum

    # soma a parcela inicial
    free_foward += y_t

    return free_foward