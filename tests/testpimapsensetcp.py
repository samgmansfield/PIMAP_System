"""Unittest file for pimapsensetcp.py

To run the tests in the top level directory type the command:
PYTHONPATH=. python tests/testpimapsensetcp.py

License:
Author: Sam Mansfield
"""
import ast
import socket
import threading
import time
import unittest
from pimap import pimapsensetcp as pset
from pimap import pimaputilities as pu

class PimapSenseTcpTestCase(unittest.TestCase):
  def test_creating_and_closing_correct_usage(self):
    # Test using default values.
    sense = pset.PimapSenseTcp()
    self.assertEqual(sense.socket.family, socket.AF_INET)
    for worker in sense.worker_processes:
      self.assertTrue(worker.is_alive())
    sense.close()
    for worker in sense.worker_processes:
      self.assertFalse(worker.is_alive())

    # Test using an IPv4 loopback address.
    host = "localhost"
    port = 1234
    sense = pset.PimapSenseTcp(host, port)
    self.assertEqual(sense.socket.family, socket.AF_INET)
    for worker in sense.worker_processes:
      self.assertTrue(worker.is_alive())
    sense.close()
    for worker in sense.worker_processes:
      self.assertFalse(worker.is_alive())

    # Test using an IPv4 non-loopback address.
    host = socket.gethostname()
    port = 1234
    sense = pset.PimapSenseTcp(host, port)
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
    sense = pset.PimapSenseTcp(host, port, ipv6=ipv6)
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
    sense = pset.PimapSenseTcp(host, port, ipv6=ipv6)
    self.assertEqual(sense.socket.family, socket.AF_INET6)
    for worker in sense.worker_processes:
      self.assertTrue(worker.is_alive())
    sense.close()
    for worker in sense.worker_processes:
      self.assertFalse(worker.is_alive())

    # Test with system_samples
    sense = pset.PimapSenseTcp(system_samples=True)
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
    self.assertRaises(socket.error, pset.PimapSenseTcp, host, port)

    # Test creating with an invalid nonsense host.
    host = "nonsense"
    port = 1234
    self.assertRaises(socket.error, pset.PimapSenseTcp, host, port)

    # Test creating with a valid host and an invalid port.
    host = "localhost"
    port = 1000000000
    self.assertRaises(ValueError, pset.PimapSenseTcp, host, port)

    # Test creating with a non-integer port.
    host = "localhost"
    port = "nonsense"
    self.assertRaises(ValueError, pset.PimapSenseTcp, host, port)

  def test_sense(self):
    # Test pimap data without system_samples.
    sense = pset.PimapSenseTcp()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((sense.host, sense.port))
    sample_type = "test_type" 
    patient_id = "test"
    device_id = "1"
    sample = 0
    sent_pimap_samples = []
    stop_time = time.time() + sense.system_samples_period
    while time.time() < stop_time:
      pimap_sample = pu.create_pimap_sample(sample_type, patient_id, device_id, sample)
      s.send(pimap_sample.encode())
      time.sleep(0.001)
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

    # Test generic data without system_samples.
    sense = pset.PimapSenseTcp()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    shost = "127.0.0.1"
    addr_info =  socket.getaddrinfo(shost, None, socket.AF_INET, socket.SOCK_STREAM)
    addr = addr_info[0][4]
    s.bind(addr)
    s.connect((sense.host, sense.port))
    sport = s.getsockname()[0]
    sport = s.getsockname()[1]
    data = 0
    sent_data = []
    stop_time = time.time() + sense.system_samples_period
    while time.time() < stop_time:
      s.send(str(data).encode())
      time.sleep(0.001)
      sent_data.append(data)
      data += 1
    sock_name = s.getsockname()
    s.close() 

    sensed_pimap_samples = []
    while len(sensed_pimap_samples) < len(sent_data):
      sensed_pimap_samples.extend(sense.sense())
    sense.close()

    self.assertEqual(len(sent_data), len(sensed_pimap_samples))
    for sent_data, sensed_psample in zip(sent_data, sensed_pimap_samples):
      sample_type = pu.get_type(sensed_psample)
      patient_id = pu.get_patient_id(sensed_psample)
      device_id = pu.get_device_id(sensed_psample)
      sensed_data = int(pu.get_sample(sensed_psample))
      self.assertEqual(sample_type, sense.sample_type)
      self.assertEqual(patient_id, shost)
      self.assertEqual(device_id, str(sport))
      self.assertEqual(sent_data, sensed_data)

    # Test pimap data with system_samples.
    sense = pset.PimapSenseTcp(system_samples=True)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((sense.host, sense.port))
    sample_type = "test_type"
    patient_id = "test"
    device_id = "1"
    sample = 0
    sent_pimap_samples = []
    stop_time = time.time() + sense.system_samples_period
    while time.time() < stop_time:
      pimap_sample = pu.create_pimap_sample(sample_type, patient_id, device_id, sample)
      s.send(pimap_sample.encode())
      time.sleep(0.001)
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
