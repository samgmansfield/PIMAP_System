"""Example file: PIMAP Retrieve and Visualize

License:
Author: Sam Mansfield
"""
import ast
import configparser
import sys
import time
from pimap import pimapstorekafka as pstk
from pimap import pimapvisualizepltgraph as pvplt

# Default values
store_host = "localhost"
store_port = 9092
visualize_keys = ["xy_gradient"]
metric_type = "objective_mobility"
sleep_time = 1.0

# If a pimap_config.ini file is present in the current directory use the config values.
config = configparser.ConfigParser()
config.read("pimap_config.ini")
name = sys.argv[0]
if name in config:
  if "store_host" in config[name]: store_host = config[name]["store_host"]
  if "store_port" in config[name]: store_port = config[name]["store_port"]
  if "visualize_keys" in config[name]:
    visualize_keys = ast.literal_eval(config[name]["visualize_keys"])
  if "metric_type" in config[name]: metric_type = config[name]["metric_type"]
  if "sleep_time" in config[name]: sleep_time = float(config[name]["sleep_time"])

store = pstk.PimapStoreKafka(store_host, store_port)
visualize_keys = ["xy_gradient"]
visualize = pvplt.PimapVisualizePltGraph(visualize_keys)

while True:
  visualize.visualize(store.retrieve(metric_type))
  time.sleep(sleep_time)
