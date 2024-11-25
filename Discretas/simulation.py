import matplotlib.pyplot as plt
from plant import Plant
import numpy as np

class Simulation:
    def __init__(self, config, sample_time=0.1, window_size=50):
        if not isinstance(config, dict):
            raise TypeError("The `config` argument must be a JSON dictionary.")

        self.sample_time = sample_time
        self.data_config = config["data_config"]
        self.colors = config["data_colors"]
        self.style = config["data_style"]
        self.window_size = config["data_win"]

        self.series_names = list(self.data_config.keys())

        self.x_data = {name: np.array([i * self.sample_time for i in range(self.window_size[name])]) for name in self.series_names}
        self.y_data = {name: np.zeros(self.window_size[name]) for name in self.series_names}

        num_series = len(self.series_names)
        half = num_series // 2 + num_series % 2
        self.series_ax1 = self.series_names[:half]
        self.series_ax2 = self.series_names[half:]

        # Initialize plot elements
        self.fig, self.ax1, self.ax2 = self.initialize_figure()
        self.lines_ax1, self.lines_ax2 = self.initialize_lines()
        self.initialize_axes_limits()

    def plant_configurations(self, alpha=[0.9], beta=[1], gama=[1], saturation=100):
        self.__plant = Plant(alpha=alpha, beta=beta, gama=gama, saturation=saturation)
        self.__plant.init_connection()

    def change_topics(self, topic_receive="control_simulation", topic_send="plant_simulation", client_id="plant"):
        self.__plant.change_topics(topic_receive=topic_receive, topic_send=topic_send, client_id=client_id)

    def initialize_figure(self):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        plt.subplots_adjust(hspace=0.4)
        plt.ion()
        
        ax1.title.set_text('Plant')
        ax2.title.set_text('Control')
        ax1.set_xlabel('Time')
        ax2.set_xlabel('Time')
        
        return fig, ax1, ax2

    def initialize_lines(self):
        lines_ax1 = {
            name: self.ax1.step([], [], lw=1,
                                label=name,
                                color=self.colors.get(name, "black"),
                                linestyle=self.style.get(name, "-"))[0]
            for name in self.series_ax1
        }

        lines_ax2 = {
            name: self.ax2.step([], [], lw=1,
                                label=name,
                                color=self.colors.get(name, "black"),
                                linestyle=self.style.get(name, "-"))[0]
            for name in self.series_ax2
        }

        return lines_ax1, lines_ax2

    def initialize_axes_limits(self):
        time_range = 2 * (self.window_size[list(self.window_size.keys())[0]] - 1) * self.sample_time
        for ax in [self.ax1, self.ax2]:
            ax.set_xlim(0, time_range)
            ax.set_ylim(-100, 100)
            ax.grid(True, linestyle="--")
            ax.tick_params(axis='x', which='both', labelbottom=False)
            ax.set_xticks(np.arange(0, time_range, self.sample_time * 3))

        self.ax1.legend(loc="upper left")
        self.ax2.legend(loc="upper left")
        
        self.time_1 = self.ax1.axvline(x=time_range / 2, color='gray', linestyle='--')
        self.time_2 = self.ax2.axvline(x=time_range / 2, color='gray', linestyle='--')

    def update_data(self, new_data=None):
        for name in self.series_names:
            if new_data and name in new_data:
                self.y_data[name] = np.append(self.y_data[name], new_data[name])[-self.window_size[name]:]

    def update_plot(self):
        for name, line in self.lines_ax1.items():
            line.set_xdata(self.x_data[name])
            line.set_ydata(self.y_data[name])

        for name, line in self.lines_ax2.items():
            line.set_xdata(self.x_data[name])
            line.set_ydata(self.y_data[name])

        plt.pause(1e-6)

    def step(self, w, q, horizon=1):
        # recebe o sinal de controle
        self.__plant.receive_signal()

        # atualiza a simulação do sistema
        self.__plant.step_simulation(q=q)

        # atualiza a referência futura
        self.__plant.set_w([w])

        # atualiza os dados 
        self.update_data(self.__plant.get_data())

        # envia o sinal de referência
        w_send = [self.y_data["w"][self.window_size["y"] +i -1] for i in range(horizon)]
        self.__plant.send_signal(w=w_send)

        # atualiza o gráfico (enquanto o outro cara calcula o controle)
        self.update_plot()
