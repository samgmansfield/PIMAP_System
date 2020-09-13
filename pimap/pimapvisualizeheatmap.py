import pickle
import numpy as np
from matplotlib import pyplot as plt

class PimapVisualizeHeatmap:
    """
    Visualizes a heatmap using matplotlib.
    """
    def __init__(self, min_value=0.0, max_value=1e6):
        self.figure, self.axes = plt.subplots()
        self.min_value = min_value
        self.max_value = max_value
        self.heat_map = [[self.min_value, self.max_value]]
        self.im = self.axes.imshow(self.heat_map, origin="lower")
        self.colorbar = self.figure.colorbar(self.im)
        plt.pause(0.01)

    def visualize(self, pimap_metrics):
        if len(pimap_metrics) == 0:
            return

        pimap_metric = pimap_metrics[-1]

        split_pimap_metric = pimap_metric.split(";")

        pickled_scan = split_pimap_metric[3][7:]

        data = [pickle.loads(pickled_scan.encode())]

        if len(data) == 0:
            return

        new_heat_map = data[-1]
        if np.shape(new_heat_map) != np.shape(self.heat_map):
            self.im = self.axes.imshow(new_heat_map, origin="lower")
        else:
            self.im.set_data(new_heat_map)
        self.heat_map = new_heat_map
        plt.pause(0.001)

    def close(self):
        plt.close(self.figure)
