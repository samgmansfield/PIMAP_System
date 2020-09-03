"""Unittest file for pimapvisualizepltgraph.py

To run the tests in the top level directory type the command:
PYTHONPATH=. python tests/testpimapvisualizepltgraph.py

License:
Author: Sam Mansfield
"""
import ast
import numpy as np
import time
import unittest
from pimap import pimapvisualizepltgraph as pvpg
from pimap import pimaputilities as pu

class PimapVisualizePltGraphTestCase(unittest.TestCase):
  def test_creating_incorrect_usage(self):
    # Test passing a non-list keys argument.
    invalid_visualize_keys = "keys"
    self.assertRaises(TypeError, pvpg.PimapVisualizePltGraph, invalid_visualize_keys)

  def test_visualize_correct_usage(self):
    # Test using system samples with an empty list.
    visualize_keys = []
    visualize = pvpg. PimapVisualizePltGraph(visualize_keys, system_samples=True)
    system_samples = visualize.visualize([])
    while len(system_samples) == 0:
      system_samples = visualize.visualize([])

    sample = ast.literal_eval(pu.get_data(system_samples[0]))
    throughput = sample["throughput"]
    correct_throughput = 0.0
    self.assertEqual(throughput, correct_throughput)
    visualize.close()

    # Test simple graph.
    visualize_keys = ["linear"]
    visualize = pvpg.PimapVisualizePltGraph(visualize_keys)
    sample_type = "visualize_test"
    patient_ids = ["1", "2", "3"]
    device_ids = ["1", "2"]
    for i in range(10):
      pimap_samples = []
      for pid in patient_ids:
        for did in device_ids:
          sample = {}
          sample["linear"] = i*int(pid) + int(did)
          sample["linear_units"] = "Units"
          pimap_sample = pu.create_pimap_sample(sample_type, pid, did, sample)
          pimap_samples.append(pimap_sample)
      visualize.visualize(pimap_samples)
      time.sleep(1.0)
    looks_good = input("Type 'yes' if the following are true:\n"
                       "  The y-axis is labelled '" + str(visualize_keys) + "'.\n"
                       "  There are six linear plots labelled pid:1-3, did:1-2.\n"
                       "Response: ")
    assert looks_good == "yes"
    visualize.close()

  def test_visualize_incorrect_usage(self):
    # Test passing PIMAP datum instead of a list of PIMAP data.
    visualize_keys = ["key1", "key2"]
    visualize = pvpg.PimapVisualizePltGraph(visualize_keys)
    sample_type = "visualize_test"
    patient_id = "1"
    device_id = "2"
    sample = {"visualize":1}
    pimap_sample = pu.create_pimap_sample(sample_type, patient_id, device_id, sample)
    self.assertRaises(TypeError, visualize.visualize, pimap_sample)

    # Test passing invalid PIMAP data.
    visualize_keys = ["key1", "key2"]
    visualize = pvpg.PimapVisualizePltGraph(visualize_keys)
    invalid_pimap_data = ["nonsense", "invalid", "pimap_data"]
    self.assertRaises(ValueError, visualize.visualize, invalid_pimap_data)

if __name__ == "__main__":
    unittest.main()
