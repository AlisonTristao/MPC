import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

def animate_system(k, y, u, q, w, N, t):
    def update(frame):
        ax1.clear()
        ax2.clear()
        ax3.clear()

        ax1.axvline(x=t, color='yellow', linestyle='--')
        ax2.axvline(x=t, color='yellow', linestyle='--')
        ax3.axvline(x=t, color='yellow', linestyle='--')

        # (y) e (w) no mesmo gráfico
        ax1.step(k[:frame], y[:frame], where="post", color="blue", label="y(k)")
        ax1.step(k[:frame], w[:frame], where="post", color="red", linestyle="--", label="w(k)")
        ax1.set_ylabel("ŷ e referência")
        ax1.set_xlim(0, N)
        ax1.set_ylim(min(min(y), min(w))-1, max(max(y), max(w))+1)
        ax1.grid(True)
        ax1.legend()
        ax1.set_title("y(k) e w(k)")
        
        # (q) e (u) no mesmo gráfico
        ax2.step(k[:frame], q[:frame], where="post", color="green", label="Δq(k)")
        ax2.step(k[:frame], u[:frame], where="post", color="purple", label="Δu(k)")
        ax2.set_ylabel("entradas")
        ax2.set_xlim(0, N)
        ax2.set_ylim(min(min(q), min(u))-1, max(max(q), max(u))+1)
        ax2.grid(True)
        ax2.legend()
        ax2.set_title("Δq(k) e Δu(k)")

        # erro (y - w)
        ax3.step(k[:frame], y[:frame] - w[:frame], where="post", color="black", label="erro")
        ax3.set_ylabel("erro")
        ax3.set_xlim(0, N)
        ax3.set_ylim(min(y-w)-1, max(y-w)+1)
        ax3.grid(True)
        ax3.legend()
        ax3.set_title("erro")
        
        return ax1, ax2, ax3

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10))
    fig.tight_layout(pad=3.0)
    ani = FuncAnimation(fig, update, frames=N+1, repeat=False, interval=0)  # Ajuste feito em frames para N+1
    plt.show()

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
    # --- se não houver valores de u
    for _ in range(N - u.shape[0]):
        u = np.insert(u, 0, 0)

    for _ in range(N - q.shape[0]):
        q = np.insert(q, 0, 0)

    # --- matriz de convolução ---
    G = matrix_G(N, alpha)

    # --- resposta ao degrau + perturbacao ---
    y = np.dot(G, u) + np.dot(G, q)

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
    g = [resp_degrau(alpha, i) for i in range(N_ss + 1)]

    # completa os valores de u passados com zero
    len = u_past.shape[0]
    for _ in range(N_ss - len):
        u_past = np.insert(u_past, 0, 0)

    # faz a predicao para toda a janela
    for j in range(window):
        # diferença entre os valores de g
        diff = np.zeros(N_ss) 
        for i in range(N_ss):
            if j+i < N_ss:
                diff[i] = g[j+i] - g[i]

        # soma de todas as diferenças multiplicadas pelos valores passados
        sum = 0
        for i in range(N_ss):
            sum += diff[i] * u_past[N_ss -i -1]
        
        # calcula o valor predito
        free_foward[j] = sum + y_t

    return free_foward