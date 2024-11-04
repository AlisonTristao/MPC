import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

def animate_system(k, y, q, u, w, N, t):
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
        
        return ax1, ax2

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10))
    fig.tight_layout(pad=3.0)
    ani = FuncAnimation(fig, update, frames=N+1, repeat=False, interval=0)  # Ajuste feito em frames para N+1
    plt.show()

def matrix_A(N, alpha=0.8):
    # --- matriz de convolução ---
    A = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            if j <= i:
                A[i][j] = 1 - alpha**(i-j + 1)

    return A

def calculate_response(N, alpha=0.8, y0=0, u=[], q=[]):
    y = np.zeros(N)
    u = np.zeros(N) if len(u) == 0 else u
    q = np.zeros(N) if len(q) == 0 else q

    # --- matriz de convolução ---
    A = matrix_A(N)

    # --- resposta ao degrau (perturbacao) ---
    y = np.dot(A, u) + np.dot(A, q)

    # --- condição inicial ---
    for i in range(N):
        y[i] += y0 * alpha**i

    return y

def solver(alpha, free_foward, w, LAMBDA=0.1):
    G = matrix_A(len(free_foward), alpha)
    Gt  = np.transpose(G)
    I = np.identity(G.shape[0])
    
    A = np.dot(Gt, G) + LAMBDA*I
    b = np.dot(Gt, w - free_foward)
    
    delta_u = np.linalg.solve(A, b)
    
    return delta_u

'''def free_foward(y_t, alpha, delta_u, f_arr, k, N_ss):
    g = [1 - alpha**i for i in range(1000)]    
    diff = [g[i + k] - g[i] for i in range(N_ss)]

    sum = 0
    for M in range(N_ss):
        sum += diff[M] * delta_u[M]
        
    f_arr[k] = sum + y_t

    return f_arr'''