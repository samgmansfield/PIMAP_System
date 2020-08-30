"""Unittest file for pimapsenseudp.py

To run the tests in the top level directory type the command:
PYTHONPATH=. python tests/testpimapsenseudp.py

License:
Author: Sam Mansfield
"""
import ast
import socket
import threading
import time
import unittest
from pimap import pimapsenseudp as pseu
from pimap import pimaputilities as pu

class PimapSenseUdpTestCase(unittest.TestCase):
  def test_creating_and_closing_correct_usage(self):
    # Test using default values.
    sense = pseu.PimapSenseUdp()
    self.assertEqual(sense.socket.family, socket.AF_INET)
    for worker in sense.worker_processes:
      self.assertTrue(worker.is_alive())
    sense.close()
    for worker in sense.worker_processes:
      self.assertFalse(worker.is_alive())

    # Test using an IPv4 loopback address.
    host = "localhost"
    port = 1234
    sense = pseu.PimapSenseUdp(host, port)
    self.assertEqual(sense.socket.family, socket.AF_INET)
    for worker in sense.worker_processes:
      self.assertTrue(worker.is_alive())
    sense.close()
    for worker in sense.worker_processes:
      self.assertFalse(worker.is_alive())

    # Test using an IPv4 non-loopback address.
    host = socket.gethostname()
    port = 1234
    sense = pseu.PimapSenseUdp(host, port)
    self.assertEqual(sense.socket.family, socket.AF_INET)
    for worker in sense.worker_processes:
      self.assertTrue(worker.is_alive())
    sense.close()
    for worker in sense.worker_processes:
      self.assertFalse(worker.is_alive())

    # Test using an IPv6 loopback address.
    host = "localhost"
    port = 1234
    ipv6 = True
    sense = pseu.PimapSenseUdp(host, port, ipv6)
    self.assertEqual(sense.socket.family, socket.AF_INET6)
    for worker in sense.worker_processes:
      self.assertTrue(worker.is_alive())
    sense.close()
    for worker in sense.worker_processes:
      self.assertFalse(worker.is_alive())

    # Test using an IPv6 non-loopback address.
    host = socket.gethostname()
    port = 1234
    ipv6 = True
    sense = pseu.PimapSenseUdp(host, port, ipv6)
    self.assertEqual(sense.socket.family, socket.AF_INET6)
    for worker in sense.worker_processes:
      self.assertTrue(worker.is_alive())
    sense.close()
    for worker in sense.worker_processes:
      self.assertFalse(worker.is_alive())

    # Test with system_samples
    sense = pseu.PimapSenseUdp(system_samples=True)
    time.sleep(sense.system_samples_period)
    system_samples = sense.sense()
    sense.close()
    self.assertTrue(len(system_samples) > 0)
    system_sample = system_samples[0]
    sample = ast.literal_eval(pu.get_data(system_sample))
    throughput = sample["throughput"]
    correct_throughput = 0.0
    self.assertEqual(throughput, correct_throughput)

  def test_creating_and_closing_incorrect_usage(self):
    # Test creating with an invalid host.
    host = "google.com"
    port = 1234
    self.assertRaises(socket.error, pseu.PimapSenseUdp, host, port)

    # Test creating with an invalid nonsense host.
    host = "nonsense"
    port = 1234
    self.assertRaises(socket.error, pseu.PimapSenseUdp, host, port)

    # Test creating with a valid host and an invalid port.
    host = "localhost"
    port = 1000000000
    self.assertRaises(socket.gaierror, pseu.PimapSenseUdp, host, port)

    # Test creating with a non-integer port.
    host = "localhost"
    port = "nonsense"
    self.assertRaises(ValueError, pseu.PimapSenseUdp, host, port)

  def test_sense(self):
    # Test without system_samples.
    sense = pseu.PimapSenseUdp()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sample_type = "test_type" 
    patient_id = "test"
    device_id = "1"
    sample = 0
    sent_pimap_samples = []
    stop_time = time.time() + sense.system_samples_period
    while time.time() < stop_time:
      pimap_sample = pu.create_pimap_sample(sample_type, patient_id, device_id, sample)
      s.sendto(pimap_sample.encode(), (sense.host, sense.port))
      sent_pimap_samples.append(pimap_sample)
      sample += 1
    s.close() 

    sensed_pimap_samples = []
    while len(sensed_pimap_samples) < len(sent_pimap_samples):
      sensed_pimap_samples.extend(sense.sense())
    sense.close()

    self.assertEqual(len(sent_pimap_samples), len(sensed_pimap_samples))
    for sent_psample, sensed_psample in zip(sent_pimap_samples, sensed_pimap_samples):
      self.assertEqual(sent_psample, sensed_psample) 

    # Test with system_samples.
    sense = pseu.PimapSenseUdp(system_samples=True)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sample_type = "test_type" 
    patient_id = "test"
    device_id = "1"
    sample = 0
    sent_pimap_samples = []
    stop_time = time.time() + sense.system_samples_period
    while time.time() < stop_time:
      pimap_sample = pu.create_pimap_sample(sample_type, patient_id, device_id, sample)
      s.sendto(pimap_sample.encode(), (sense.host, sense.port))
      sent_pimap_samples.append(pimap_sample)
      sample += 1
    s.close() 

    sensed_samples = []
    while len(sensed_samples) < len(sent_pimap_samples):
      sensed_samples.extend(sense.sense())
    sense.close()

    sensed_system_samples = list(filter(lambda x: pu.get_type(x) == "system_samples",
                                        sensed_samples))
    sensed_pimap_samples = list(filter(lambda x: pu.get_type(x) == "test_type",
                                       sensed_samples))
    self.assertEqual(len(sent_pimap_samples), len(sensed_pimap_samples))
    for sent_psample, sensed_psample in zip(sent_pimap_samples, sensed_pimap_samples):
      self.assertEqual(sent_psample, sensed_psample)

    self.assertTrue(len(sensed_system_samples) > 0)
    system_sample = sensed_system_samples[0]
    sample = ast.literal_eval(pu.get_data(system_sample))
    throughput = sample["throughput"]
    self.assertTrue(throughput > 0.0)

if __name__ == "__main__":
    unittest.main()
