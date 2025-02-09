import matplotlib.pyplot as plt
from plant import Plant
import numpy as np

class Simulation:
    def __init__(self, config, sample_time=0.1, window_size=50):
        if not isinstance(config, dict):
            raise TypeError("The `config` argument must be a JSON dictionary.")

        self.__sample_time = sample_time
        self.__data_config = config["data_config"]
        self.__colors = config["data_colors"]
        self.__style = config["data_style"]
        self.__window_size = config["data_win"]

        self.__series_names = list(self.__data_config.keys())

        self.__x_data = {name: np.array([i * self.__sample_time for i in range(self.__window_size[name])]) for name in self.__series_names}
        self.__y_data = {name: np.zeros(self.__window_size[name]) for name in self.__series_names}

        num_series = len(self.__series_names)
        half = num_series // 2 + num_series % 2
        self.__series_ax1 = self.__series_names[:half]
        self.__series_ax2 = self.__series_names[half:]

        # Initialize plot elements
        self.__fig, self.__ax1, self.__ax2 = self.initialize_figure()
        self.__lines_ax1, self.__lines_ax2 = self.initialize_lines()
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
            name: self.__ax1.step([], [], lw=1,
                                label=name,
                                color=self.__colors.get(name, "black"),
                                linestyle=self.__style.get(name, "-"))[0]
            for name in self.__series_ax1
        }

        lines_ax2 = {
            name: self.__ax2.step([], [], lw=1,
                                label=name,
                                color=self.__colors.get(name, "black"),
                                linestyle=self.__style.get(name, "-"))[0]
            for name in self.__series_ax2
        }

        return lines_ax1, lines_ax2

    def initialize_axes_limits(self):
        time_range = 2 * (self.__window_size[list(self.__window_size.keys())[0]] - 1) * self.__sample_time
        for ax in [self.__ax1, self.__ax2]:
            ax.set_xlim(0, time_range)
            ax.set_ylim(-100, 100)
            ax.grid(True, linestyle="--")
            ax.tick_params(axis='x', which='both', labelbottom=False)
            ax.set_xticks(np.arange(0, time_range, self.__sample_time * 3))

        self.__ax1.legend(loc="upper left")
        self.__ax2.legend(loc="upper left")

    def update_data(self, new_data=None):
        for name in self.__series_names:
            if new_data and name in new_data:
                self.__y_data[name] = np.append(self.__y_data[name], new_data[name])[-self.__window_size[name]:]

    def update_plot(self):
        for name, line in self.__lines_ax1.items():
            line.set_xdata(self.__x_data[name])
            line.set_ydata(self.__y_data[name])

        for name, line in self.__lines_ax2.items():
            line.set_xdata(self.__x_data[name])
            line.set_ydata(self.__y_data[name])

        # adiciona uma linha vertical para indicar o tempo atual
        self.__ax1.axvline(x=self.__x_data["y"][-1], color="gray", linestyle="--")
        self.__ax2.axvline(x=self.__x_data["y"][-1], color="gray", linestyle="--")

        plt.pause(1e-6)

    def step(self, w=0, q=0, noise=0.0, w_horizon=1, q_horizon=0):
        # recebe o sinal de controle
        self.__plant.receive_signal()

        # atualiza a simulação do sistema
        self.__plant.step_simulation(q=self.__y_data["q"][self.__window_size["y"] - 1], noise=noise)

        # atualiza a ref e a perturbacao
        self.update_data({"q": q})
        self.update_data({"w": w})

        # atualiza os dados 
        self.update_data(self.__plant.get_data())

        # envia o sinal de referência e y
        w_future_win = [self.__y_data["w"][self.__window_size["y"] +i -1] for i in range(w_horizon)]
        q_future_win = [self.__y_data["q"][self.__window_size["y"] +i -1] for i in range(q_horizon)]
        self.__plant.send_signal(w=w_future_win, q=q_future_win)

        # atualiza o gráfico (enquanto o outro cara calcula o controle)
        self.update_plot()
