"""PIMAP Visualize Component using Matplotlib's Graphing.

PIMAP Visualize Plt Graph uses Matplotlib to graph time-series data. This is very
useful to visualize trends in data.

License:
Author: Sam Mansfield
"""
import ast
import datetime
import numpy as np
import pickle
import re
import sys
import time
from collections import defaultdict
from matplotlib import dates as mdates
from matplotlib import pyplot as plt
from pimap import pimaputilities as pu

class PimapVisualizePltGraph:
  def __init__(self, keys, system_samples=False, app=""):
    """Constructor for PIMAP Visualize Plt Graph

    Arguments:
      keys: A list of values used to key PIMAP data. For example given a PIMAP sample
        with sample field {"pressure":2, "temperature":3, "humidity":4} and the
        given keys argument ["pressure"], only the pressure values will be graphed.
      system_samples (optional): A boolean value that indicates whether system_samples
        are produced that report the throughput of this component. Defaults to False.
      app (optional): A name of the application running, which is used to append
        to the name of they sample_type of system_samples,
        e.g. sample_type:"system_samples_app". Defaults to "".

    Exceptions:
      TypeError:
        If keys is not a list.
    """
    if not isinstance(keys, list):
      raise TypeError("The argument keys must be a list")

    self.keys = keys
    self.system_samples = bool(system_samples)
    self.app = str(app)

    # System Samples Setup
    self.system_samples_updated = time.time()
    self.system_samples_period = 1.0
    self.latencies = []
    self.visualized_data = 0

    # A value of -1 indicates there is no limit
    self.display_limit = 100
    self.state = "aggregate"
    self.aggregation_buffer = []
    self.aggregation_limit = 100

    self.units = None
    self.title = None
    self.plot_dates = defaultdict(list)
    self.plot_data = defaultdict(list)
    self.lines = {}
    self.total_data = 0
    self.figure, self.axes = plt.subplots()

    for label in self.axes.get_xticklabels():
      label.set_ha("right")
      label.set_rotation(30)
    self.axes.grid()
    self.axes.set_xlabel("Time")
    self.axes.set_ylabel(str(self.keys))

    # These period are estimates and are not guaranteed
    self.refresh_period = 0.5
    self.aggregation_period = 0.2*self.refresh_period
    self.process_period = 0.4*self.refresh_period
    self.plot_period = 0.4*self.refresh_period
    self.time_plotted = time.time()

    # Display empty figure
    self.figure.canvas.draw_idle()
    plt.show(block=False)
    self.figure.canvas.start_event_loop(0.001)

  def visualize(self, pimap_data):
    """Core interaction of PIMAP Visualize Plt Graph.

    Graphs the given pimap_data using the keys from the constructor and the timestamp
    in the PIMAP datum. A new line is generated per patient_id, device_id pair.

    Arguments:
      pimap_data: A list of PIMAP data.

    Exceptions:
      TypeError:
        If pimap_data is not a list.
      ValueError:
        If pimap_data contains non-PIMAP data.
    """
    if not isinstance(pimap_data, list):
      raise TypeError("The argument pimap_data must be a list.")

    valid_pimap_data = list(map(pu.validate_datum, pimap_data))
    if not any(valid_pimap_data) and len(pimap_data) != 0:
      raise ValueError("Invalid data in pimap_data.")

    self.aggregation_buffer.extend(pimap_data)
    pimap_system_samples = [] 

    if self.state == "aggregate":
      if ((time.time() - self.time_plotted > self.aggregation_period) or
         (len(self.aggregation_buffer) > self.aggregation_limit)):
        self.state = "process_and_plot"
    if self.state == "process_and_plot":
      start_time_to_process = time.time()
      data_processed = 0
      for key in self.keys:
        filtered_pimap_data = list(filter(lambda x: key in ast.literal_eval(
                                                              pu.get_data(x)),
                                          self.aggregation_buffer))
        if len(filtered_pimap_data) == 0:
          continue

        self.total_data += len(filtered_pimap_data)
        data_processed += len(filtered_pimap_data)
        self.visualized_data += len(filtered_pimap_data)

        types = list(map(pu.get_type, filtered_pimap_data))
        patient_ids = list(map(pu.get_patient_id, filtered_pimap_data))
        device_ids = list(map(pu.get_device_id, filtered_pimap_data))
        timestamps = list(map(lambda x: round(float(pu.get_timestamp(x)), 3),
                              filtered_pimap_data))
        self.latencies.extend(time.time() - np.array(timestamps))
        dates = list(map(lambda x: datetime.datetime.fromtimestamp(x), timestamps))
        data_dicts = list(map(lambda x: ast.literal_eval(pu.get_data(x)),
                              filtered_pimap_data))
        data = list(map(lambda x: x[key], data_dicts))

        # Deprecated, but may be used in the future. This is on way to use units in
        # the graph, but is kind of hacky.
        #test_dict_for_units = data_dicts[0]
        #if (key + "_units") in test_dict_for_units and self.units == None:
        #    self.units = test_dict_for_units[key + "_units"]
        #    self.axes.set_ylabel(self.units)

        lines_updated = set()
        for pid, did, date, data, typ in zip(patient_ids, device_ids, dates, data,
                                                                                  types):
          line_id = ("pid:" + pid + ", did:" + did + ", data:" + key + ", type:" + typ)
          lines_updated.add(line_id)
          self.plot_dates[line_id].append(date)
          self.plot_data[line_id].append(data)

        down_sample = 1
        if (self.total_data >= self.display_limit and self.display_limit != -1):
          down_sample = int(self.total_data/self.display_limit)

        for line_id in lines_updated:
          if line_id in self.lines:
            self.lines[line_id].set_data(self.plot_dates[line_id][::down_sample],
                                         self.plot_data[line_id][::down_sample])
          else:
            self.lines[line_id], = self.axes.plot(
                                            self.plot_dates[line_id][::down_sample],
                                            self.plot_data[line_id][::down_sample],
                                            label=line_id)

      time_to_process = time.time() - start_time_to_process
      if time_to_process > self.process_period and data_processed > 0:
        self.aggregation_limit /= 2
      elif len(self.aggregation_buffer) >= self.aggregation_limit:
        self.aggregation_limit += len(self.aggregation_buffer)

      # Plot Time
      start_time_to_plot = time.time()
      self.axes.relim()
      self.axes.autoscale_view()
      # Based on the concept that a human can only keep track of 7 things in their
      # mind at once. But this is a bit arbitrary and is implemented for 
      # efficiency purposes.
      if len(self.lines) <= 7 and self.total_data > 0:
        self.axes.legend()

      # Refresh the figure 
      if self.figure.stale:
        self.figure.canvas.draw_idle()
        # Pushes graph to foreground. This may be desirable in some situations.
        #plt.show(block=False)
        self.figure.canvas.start_event_loop(0.001)
      else:
        time.sleep(0.001)

      actual_refresh_period = time.time() - self.time_plotted
      self.time_plotted = time.time()
      time_to_plot = time.time() - start_time_to_plot
      if self.display_limit != -1:
        if time_to_plot > self.plot_period:
          self.display_limit /= 2
        elif self.total_data > self.display_limit:
          self.display_limit += data_processed

      self.state = "aggregate"
      self.aggregation_buffer = []

    if (self.system_samples and
        (time.time() - self.system_samples_updated > self.system_samples_period)):
      sample_type = "system_samples"
      if self.app != "":
        sample_type += "_" + self.app
      patient_id = "visualize"
      device_id = self.keys
      visualized_data_per_s = self.visualized_data/(time.time() -
                                                    self.system_samples_updated)
      sample = {"throughput":visualized_data_per_s,
                "aggregation_limit":self.aggregation_limit,
                "aggregation":len(self.aggregation_buffer),
                "display_limit":self.display_limit,
                "total_data":self.total_data}
      if len(self.latencies) > 0:
        sample["latency"] = np.mean(self.latencies)
      pimap_system_samples.append(pu.create_pimap_sample(sample_type, patient_id,
                                                         device_id, sample))
      self.system_samples_updated = time.time()
      self.latencies = []
      self.visualized_data = 0

    return pimap_system_samples

  def save(self, location):
    """Save the current graph as a pickle.

    Arguments:
      location: The location to save the pickle. For example if location is
        "visualize.pickle" the graph will be saved in the current directory with the
        name "visualize.pickle". It can be reopened using:
        python pimapvisualizepltgraph.py location.
    """
    with open(location, "wb") as f:
      pickle.dump((self.title, self.axes.get_xlabel(), self.axes.get_ylabel(),
                   self.plot_dates, self.plot_data), f)

  def close(self):
    """Closes the Matplotlib figure."""
    plt.close(self.figure)

def print_usage_and_exit():
  print("Usage:")
  print("   pimapvisualizepltgraph.py 'pickle_file_path'")
  exit()

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print_usage_and_exit()

  # Change the font size.
  #plt.rcParams.update({'font.size': 20})
  figure, axes = plt.subplots()
  axes.grid()
  (title, xlabel, ylabel, plot_dates, plot_data) = pickle.load(open(sys.argv[1], "rb"))
  # Markers for multiple plots on the same graph
  markers = ["o", "v", "s", "+", "*", "1", "8", "p", "x"]
  i = 0
  for line_id in sorted(plot_dates):
    # Plot raw data
    plt.plot(plot_dates[line_id], plot_data[line_id], label=line_id)
    # Plot filtered data by line_id
    #if line_id.find("store") != -1:
    #  plt.plot(plot_dates[line_id], plot_data[line_id], label=line_id,
    #           linestyle = ":", linewidth=0.5,
    #           marker=markers[i], markersize=8, markevery=1, fillstyle="none")
    i += 1
  axes.set_title(title)
  axes.set_xlabel(xlabel)
  # Change x-axis label.
  #axes.set_xlabel("Time (hour:minute)")
  # Change the x-axis limit.
  #axes.set_xlim(datetime.datetime(2020, 7, 7, hour=17, minute=13),
  #              datetime.datetime(2020, 7, 8, hour=17, minute=14))
  # Change the x-axis date formatter
  #datefmt = mdates.DateFormatter("%H:%M")
  #axes.xaxis.set_major_formatter(datefmt)
  # Change the y-axis label
  #axes.set_ylabel("Throughput (PIMAP samples/metrics a second)")
  # Change the y-axis limit.
  #axes.set_ylim(-500, 12000)
  # Invert y-axis
  #axes.invert_yaxis()
  for label in axes.get_xticklabels():
    label.set_ha("right")
    label.set_rotation(30)
  axes.legend()
  plt.show()
