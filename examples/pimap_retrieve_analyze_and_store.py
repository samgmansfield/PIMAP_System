"""Example file: PIMAP Retrieve Analyze and Store

License:
Author: Sam Mansfield
"""
import configparser
import sys
import time
from pimap import pimapanalyzeobjectivemobility as paom
from pimap import pimapstorekafka as pstk

# Default values
store_host = "localhost"
store_port = 9092
max_pressure = 100.0
sample_type = "pressure_bandage"
sleep_time = 1.0

# If a pimap_config.ini file is present in the current directory use the config values.
config = configparser.ConfigParser()
config.read("pimap_config.ini")
name = sys.argv[0]
if name in config:
  if "store_host" in config[name]: store_host = config[name]["store_host"]
  if "store_port" in config[name]: store_port = config[name]["store_port"]
  if "max_pressure" in config[name]: max_pressure = float(config[name]["max_pressure"])
  if "sample_type" in config[name]: sample_type = config[name]["sample_type"]
  if "sleep_time" in config[name]: sleep_time = float(config[name]["sleep_time"])

analyze = paom.PimapAnalyzeObjectiveMobility(max_pressure)
store = pstk.PimapStoreKafka(store_host, store_port)

while True:
  pimap_metrics = analyze.analyze(store.retrieve(sample_type))
  store.store(pimap_metrics)
  time.sleep(sleep_time)
