"""Example file: PIMAP Sense and Store

License:
Author: Sam Mansfield
"""
import configparser
import sys
import time
from pimap import pimapsenseudp as pseu
from pimap import pimapstorekafka as pstk

# Default values
sense_host = "localhost"
sense_port = 31415
store_host = "localhost"
store_port = 9092
sleep_time = 1.0

# If a pimap_config.ini file is present in the current directory use the config values.
config = configparser.ConfigParser()
config.read("pimap_config.ini")
name = sys.argv[0]
if name in config:
  if "sense_host" in config[name]: sense_host = config[name]["sense_host"]
  if "sense_port" in config[name]: sense_port = int(config[name]["sense_port"])
  if "store_host" in config[name]: store_host = config[name]["store_host"]
  if "store_port" in config[name]: store_port = int(config[name]["store_port"])
  if "sleep_time" in config[name]: sleep_time = float(config[name]["sleep_time"])

sense = pseu.PimapSenseUdp(sense_host, sense_port)
store = pstk.PimapStoreKafka(store_host, store_port)

while True:
  store.store(sense.sense())
  time.sleep(sleep_time)
