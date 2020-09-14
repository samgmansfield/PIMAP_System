"""PIMAP Visualize component for heat maps.

PIMAP Visualize component that uses Matplotlib's heat map features to display a 2d heat
map.

License:-
Authors: Eric Vin, Sam Mansfield
"""
import pickle
import numpy as np
from matplotlib import pyplot as plt

from pimap import pimaputilities as pu

class PimapVisualizeHeatmap:
  """ Visualizes a heatmap using matplotlib. """
  def __init__(self, min_value=0.0, max_value=1e6):
    self.figure, self.axes = plt.subplots()
    self.min_value = float(min_value)
    self.max_value = float(max_value)
    self.heat_map = [[self.min_value, self.max_value]]
    self.im = self.axes.imshow(self.heat_map, origin="lower")
    self.colorbar = self.figure.colorbar(self.im)
    plt.pause(0.01)

  def visualize(self, pimap_metrics):
    if len(pimap_metrics) == 0:
      # No PIMAP metrics to visualize
      return

    pimap_metric = pimap_metrics[-1]

    data = pickle.loads(pu.get_data(pimap_metric).encode())

    if np.shape(data) != np.shape(self.heat_map):
      self.im = self.axes.imshow(data, origin="lower")
    else:
      self.im.set_data(data)
    self.heat_map = data
    plt.pause(0.001)

  def close(self):
    plt.close(self.figure)
