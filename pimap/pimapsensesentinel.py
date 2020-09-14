"""PIMAP Sense component that interacts with the Sentinel bandage.

PIMAP Sense Sentinel interacts with the Sentinel bandage using serial. This component
depends on the sentineltoolkit.

License:
Author: Eric Vin
"""
import time
import pickle

from pimap import pimaputilities as pu
from sentineltoolkit.sentinel_interface import SentinelInterfaceToolkit

class PimapSenseSentinel:
  """ Performs a scan on the Sentinel Bandage """
  def __init__(self, device_location, frequency_list, calibration_profile,
               patient_id = 0, device_id = 0):
    # Creates an instance of the Sentinel Interface Toolkit
    self.sentinel_toolkit = SentinelInterfaceToolkit(device_location)

    # Stores list of frequencies to scan.
    self.frequency_list = frequency_list

    # Stores calibration profile to calibrate raw scans
    self.calibration_profile = calibration_profile

    self.patient_id = str(patient_id)
    self.device_id = str(device_id)

    def sense(self):
      raw_scan_results = self.sentinel_toolkit.send_scan_all(self.frequency_list)
      calibrated_scan_results = self.calibration_profile.calibrate_raw_sample(
        raw_scan_results)

      string_scan_results = pickle.dumps(calibrated_scan_results, 0).decode()

      pimap_sample = pu.create_pimap_sample("SentinelBandage", self.patient_id,
                                            self.device_id, string_scan_results,
                                            time.time())

      return [pimap_sample]
