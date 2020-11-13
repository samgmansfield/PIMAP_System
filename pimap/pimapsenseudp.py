"""PIMAP Sense component that listens for UDP packets.

PIMAP Sense UDP is a PIMAP Sense component that starts a multi-process server on a given
host and port. PIMAP Sense UDP supports both IPv4 and IPv6.

License:
Author: Sam Mansfield
"""
import ast
import ctypes
import multiprocessing
import socket
import time
from pimap import pimaputilities as pu

class PimapSenseUdp:
  def __init__(self, host="localhost", port=31415, sample_type="udp", ipv6=False,
               workers=3, system_samples=False):
    """Constructor for PIMAP Sense UDP

    Arguments:
      host (optional): The host of the UDP server. Defaults to "localhost".
      port (optional): The port of the UDP server. Defaults to 31415.
      sample_type (optional): The sample type given to non-pimap sensed data.
        Defaults to "udp".
      ipv6 (optional): Whether the address is IPv6. Defaults to False.
      workers (optional): The number of server processes. Defaults to 3.
      system_samples (optional): A boolean value that indicates whether system_samples
        are produced that report the throughput of this component. Defaults to False.

    Exceptions:
      socket.error:
        If attempting to bind to an invalid address.
      ValueError:
        If a non-integer port is given or a port not in the range of 1024-65535..
    """
    self.host = host
    self.port = int(port)
    if self.port < 1024 or self.port > 65535:
      raise(ValueError("Port must be an integer in the range 1024-65535."))
    self.sample_type = str(sample_type)
    self.ipv6 = bool(ipv6)
    self.workers = int(workers)
    self.system_samples = bool(system_samples)

    # System Samples Setup
    self.sensed_data = 0
    self.system_samples_updated = time.time()
    self.system_samples_period = 1.0

    # Socket Setup
    if not self.ipv6:
      addrinfo = socket.getaddrinfo(self.host, self.port, socket.AF_INET,
                                    socket.SOCK_DGRAM)
      self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      address = addrinfo[0][4]
    else:
      addrinfo = socket.getaddrinfo(self.host, self.port, socket.AF_INET6,
                                    socket.SOCK_DGRAM)
      self.socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
      address = addrinfo[0][4]
    self.socket.settimeout(1.0)
    try: self.socket.bind(address)
    except socket.error as e:
      self.socket.close()
      raise e
    self.max_buffer_size = 4096

    # Address Lookup Setup
    # Address lookup is by the tuple (patient_id, device_id) -> IP address.
    # TODO: Under development! May be used in the future for PIMAP commands.
    self.addresses_by_id = {}

    # Multiprocess Setup
    self.running = multiprocessing.Value(ctypes.c_bool, True)
    self.pimap_data_queue = multiprocessing.Queue()
    self.workers = self.workers
    self.worker_processes = []
    for i in range(self.workers):
      worker_process = multiprocessing.Process(target=self._sense_worker, daemon=True)
      self.worker_processes.append(worker_process)
      worker_process.start()

  def _sense_worker(self):
    """Worker process

    Used internally to create UDP server processes.
    """
    while self.running.value:
      try:
        (received_coded, address) = self.socket.recvfrom(self.max_buffer_size)
        received = received_coded.decode()
        # If a valid PIMAP sample/metric is received add it to the queue.
        if pu.validate_datum(received):
          pimap_datum = received
          # Add lookup addresses of incoming PIMAP data.
          patient_id = pu.get_patient_id(pimap_datum)
          device_id = pu.get_device_id(pimap_datum)
          # TODO: Under development! May be used in the future for PIMAP commands.
        else:
          patient_id = address[0]
          device_id = address[1]
          sample = received
          pimap_datum = pu.create_pimap_sample(self.sample_type, patient_id, device_id,
                                               sample)
        self.addresses_by_id[(patient_id, device_id)] = address
        self.pimap_data_queue.put(pimap_datum)

      except socket.timeout: continue

  def sense(self):
    """Core interaction of PIMAP Sense UDP.

    Returns:
      A list of PIMAP samples/metrics sensed since last call to sense().
    """
    # Get all PIMAP data from the queue.
    pimap_data = []
    while not self.pimap_data_queue.empty():
      pimap_data.append(self.pimap_data_queue.get())

    # Sort the PIMAP data by timestamp. The PIMAP data can be out of order because we are
    # using multiple processes to sense it.
    pimap_data.sort(key=lambda x: pu.get_timestamp(x))

    # Track the amount of sensed PIMAP data.
    self.sensed_data += len(pimap_data)

    # If system_samples is True and a system_sample was not created within the last
    # system_samples period, create a system_sample.
    pimap_system_samples = []
    if (self.system_samples and
        (time.time() - self.system_samples_updated > self.system_samples_period)):
      sample_type = "system_samples"
      # Identify PIMAP Sense using the host and port.
      patient_id = "sense"
      device_id = (self.host, self.port)
      sensed_data_per_s = self.sensed_data/(time.time() - self.system_samples_updated)
      sample = {"throughput":sensed_data_per_s}
      system_sample = pu.create_pimap_sample(sample_type, patient_id, device_id, sample)
      pimap_system_samples.append(system_sample)

      # Reset system_samples variables.
      self.system_samples_updated = time.time()
      self.sensed_data = 0

    return pimap_data + pimap_system_samples

  def close(self):
    """Safely stop the UDP server.

    Terminates server processes and closes the socket.
    """
    self.running.value = False
    for worker_process in self.worker_processes:
      worker_process.join()
    self.socket.close()

# Deprecated Methods: May be used in the future.
#
#  # get_max_buffer_size: Get the max buffer size.
#  def get_max_buffer_size(self):
#    return self.max_buffer_size
#
#  # send_command: Sends the given command to the address based on the given patient_id
#  # and device_id.
#  # Under Development!
#  def send_command(self, patient_id, device_id, command):
#    """Under Development!
#
#    """
#    if (str(patient_id), str(device_id)) in self.addresses_by_id:
#        address = self.addresses_by_id[(str(patient_id), str(device_id))]
#        self.socket.sendto(command.encode(), address)
