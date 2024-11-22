import matplotlib.pyplot as plt
import random as ra
import numpy as np

class Realtime_Plot:
    def __init__(self, config=None, sample_time=0.1, window_size=50):
        if config == None:
            config = {
                    "data_config":{"y": [],"w": [],"u": [],"q": []},
                    "data_colors":{"y": "orange","w": "purple","u": "green","q": "black"},   
                    "data_style":{"y": "-","w": "--","u": "-","q": "--"}
                }

        if isinstance(config, dict):
            self.data_config = config["data_config"]
            self.colors = config["data_colors"]
            self.style = config["data_style"]
        else:
            raise TypeError("The `config` argument must be a JSON dictionary.")

        self.series_names = list(self.data_config.keys())
        self.sample_time = sample_time
        self.window_size = window_size

        self.x_data = np.zeros(1)
        self.y_data = {name: np.zeros(1) for name in self.series_names}

        num_series = len(self.series_names)
        half = num_series // 2 + num_series % 2
        self.series_ax1 = self.series_names[:half]
        self.series_ax2 = self.series_names[half:]

        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(12, 8))
        plt.subplots_adjust(hspace=0.4)
        plt.ion()

        self.lines_ax1 = {
            name: self.ax1.step([], [], lw=1,
                                label=name,
                                color=self.colors.get(name, "black"),
                                linestyle=self.style.get(name, "-"))[0]
            for name in self.series_ax1
        }

        self.lines_ax2 = {
            name: self.ax2.step([], [], lw=1,
                                label=name,
                                color=self.colors.get(name, "black"),
                                linestyle=self.style.get(name, "-"))[0]
            for name in self.series_ax2
        }

        self.time_1 = self.ax1.axvline(x=self.x_data[-1], color='gray', linestyle='--')
        self.time_2 = self.ax2.axvline(x=self.x_data[-1], color='gray', linestyle='--')

        self.ax1.title.set_text('Plant')
        self.ax2.title.set_text('Control')
        self.ax1.set_xlim(0, 2 * window_size * sample_time)
        self.ax1.set_ylim(-100, 100)
        self.ax1.grid(True, linestyle="--")

        self.ax2.set_xlim(0, 2 * window_size * sample_time)
        self.ax2.set_ylim(-100, 100)
        self.ax2.grid(True, linestyle="--")

        self.ax1.legend(loc="upper left")
        self.ax2.legend(loc="upper left")

    def update_data(self, new_data=None):
        self.x_data = np.append(self.x_data, self.x_data[-1] + self.sample_time)

        for name in self.series_names:
            if new_data and name in new_data:
                self.y_data[name] = np.append(self.y_data[name], new_data[name])
            else:
                self.y_data[name] = np.append(self.y_data[name], ra.random() * 100)

        if len(self.x_data) > self.window_size:
            self.x_data = self.x_data[-self.window_size:]
            for name in self.series_names:
                self.y_data[name] = self.y_data[name][-self.window_size:]

    def update_plot(self):
        for name, line in self.lines_ax1.items():
            line.set_xdata(self.x_data)
            line.set_ydata(self.y_data[name])

        for name, line in self.lines_ax2.items():
            line.set_xdata(self.x_data)
            line.set_ydata(self.y_data[name])

        self.time_1.set_xdata([self.x_data[-1]])
        self.time_2.set_xdata([self.x_data[-1]])

        self.ax1.set_xlim(self.x_data[0], self.x_data[0] + 2 * self.window_size * self.sample_time)
        self.ax2.set_xlim(self.x_data[0], self.x_data[0] + 2 * self.window_size * self.sample_time)

        plt.pause(1e-6)

    def step(self, new_data=None):
        self.update_data(new_data)
        self.update_plot()