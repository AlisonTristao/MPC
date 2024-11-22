import matplotlib.pyplot as plt
import random as ra
import numpy as np
import time

class Realtime_Plot:
    def __init__(self, data_config, data_colors, sample_time=0.1, window_size=50):
        self.data_config = data_config
        self.series_names = list(data_config.keys())
        self.sample_time = sample_time
        self.window_size = window_size

        # dicionário de cores para as séries
        self.colors = data_colors
        self.x_data = np.zeros(1)
        self.y_data = {name: np.zeros(1) for name in self.series_names}

        # divide a serie em 2 graficos
        num_series = len(self.series_names)
        half = num_series // 2 + num_series % 2
        self.series_ax1 = self.series_names[:half]
        self.series_ax2 = self.series_names[half:]

        # configura o grafico
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(12, 8))
        plt.subplots_adjust(hspace=0.4)
        plt.ion()

        # linhas no grafico 1
        self.lines_ax1 = {
            name: self.ax1.step([], [], lw=2, label=name, color=self.colors.get(name, "black"))[0]
            for name in self.series_ax1
        }
        # linhas do gráfico 2
        self.lines_ax2 = {
            name: self.ax2.step([], [], lw=2, label=name, color=self.colors.get(name, "black"))[0]
            for name in self.series_ax2
        }

        # linhas verticais indicando o tempo atual
        self.time_1 = self.ax1.axvline(x=self.x_data[-1], color='gray', linestyle='--')
        self.time_2 = self.ax2.axvline(x=self.x_data[-1], color='gray', linestyle='--')

        # configurações dos gráficos
        self.ax1.title.set_text('Planta')
        self.ax2.title.set_text('Controle')
        self.ax1.set_xlim(0, 2 * window_size * sample_time)
        self.ax1.set_ylim(-100, 100)
        self.ax1.grid(True, linestyle="--")

        self.ax2.set_xlim(0, 2 * window_size * sample_time)
        self.ax2.set_ylim(-100, 100)
        self.ax2.grid(True, linestyle="--")

        # adiciona legendas
        self.ax1.legend(loc="upper left")
        self.ax2.legend(loc="upper left")

    def update_data(self, new_data=None):
        # incrementa o tempo
        self.x_data = np.append(self.x_data, self.x_data[-1] + self.sample_time)

        for name in self.series_names:
            if new_data and name in new_data:
                self.y_data[name] = np.append(self.y_data[name], new_data[name])
            else:
                self.y_data[name] = np.append(self.y_data[name], ra.random() * 100)

        # manter apenas os últimos valores da janela
        if len(self.x_data) > self.window_size:
            self.x_data = self.x_data[-self.window_size:]
            for name in self.series_names:
                self.y_data[name] = self.y_data[name][-self.window_size:]

    def update_plot(self):
        # atualiza as linhas do primeiro gráfico
        for name, line in self.lines_ax1.items():
            line.set_xdata(self.x_data)
            line.set_ydata(self.y_data[name])

        # atualiza as linhas do segundo gráfico
        for name, line in self.lines_ax2.items():
            line.set_xdata(self.x_data)
            line.set_ydata(self.y_data[name])

        # atualiza as linhas verticais
        self.time_1.set_xdata([self.x_data[-1]])
        self.time_2.set_xdata([self.x_data[-1]])

        # ajusta os limites dos gráficos
        self.ax1.set_xlim(self.x_data[0], self.x_data[0] + 2 * self.window_size * self.sample_time)
        self.ax2.set_xlim(self.x_data[0], self.x_data[0] + 2 * self.window_size * self.sample_time)

        plt.pause(1e-6)

    def step(self, new_data=None):
        self.update_data(new_data)
        self.update_plot()

if __name__ == "__main__":
    # configuração dos dados iniciais
    data = {
        "Temperatura": [0],
        "Corrente": [0],
    }

    data_colors = {
        "Temperatura": "orange",
        "Corrente": "green"
    }

    plotter = Realtime_Plot(data_config=data, data_colors=data_colors, sample_time=0.1, window_size=50)

    for _ in range(100):  # número de passos
        # simulação de novos dados
        new_data = {
            "Temperatura": ra.uniform(-50, 50),
            "Corrente": ra.uniform(-30, 30),
        }
        plotter.step(new_data=new_data)
        time.sleep(0.1)  # controle externo do ritmo
