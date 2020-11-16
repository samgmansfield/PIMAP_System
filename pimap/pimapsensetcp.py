"""PIMAP Sense component that listens for TCP packets.

PIMAP Sense TCP is a PIMAP Sense component that starts a multi-process server on a given
host and port. PIMAP Sense TCP supports both IPv4 and IPv6.

License:
Author: Sam Mansfield
"""
import ast
import ctypes
import multiprocessing
import socket
import time
from pimap import pimaputilities as pu

class PimapSenseTcp:
  def __init__(self, host="localhost", port=31416, sample_type="tcp", ipv6=False,
               sense_workers=3, pimap_workers=1, system_samples=False):
    """Constructor for PIMAP Sense TCP

    Arguments:
      host (optional): The host of the TCP server. Defaults to "localhost".
      port (optional): The port of the TCP server. Defaults to 31415.
      sample_type (optional): The sample type given to non-pimap sensed data.
        Defaults to "udp".
      ipv6 (optional): Whether the address is IPv6. Defaults to False.
      sense_workers (optional): The number of simultaneous TCP connections.
        Defaults to 3.
      pimap_workers (optional): The number of processes to create pimap data from
        sensed data. Defaults to 3.
      system_samples (optional): A boolean value that indicates whether system_samples
        are produced that report the throughput of this component. Defaults to False.

    Exceptions:
      socket.error:
        If attempting to bind to an invalid address.
      ValueError:
        If a non-integer port is given or a port not in the range of 1024-65535.
    """
    self.host = host
    self.port = int(port)
    if self.port < 1024 or self.port > 65535:
      raise(ValueError("Port must be an integer in the range 1024-65535."))
    self.sample_type = str(sample_type)
    self.ipv6 = bool(ipv6)
    self.sense_workers = int(sense_workers)
    self.pimap_workers = int(pimap_workers)
    self.system_samples = bool(system_samples)

    # System Samples Setup
    self.sensed_data = 0
    self.system_samples_updated = time.time()
    self.system_samples_period = 1.0

    # Socket Setup
    if not self.ipv6:
      addrinfo = socket.getaddrinfo(self.host, self.port, socket.AF_INET,
                                    socket.SOCK_STREAM)
      self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      address = addrinfo[0][4]
    else:
      addrinfo = socket.getaddrinfo(self.host, self.port, socket.AF_INET6,
                                    socket.SOCK_STREAM)
      self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
      address = addrinfo[0][4]
    self.socket.settimeout(1.0)
    try: self.socket.bind(address)
    except socket.error as e:
      self.socket.close()
      raise e
    self.max_buffer_size = 4096
    self.host = self.socket.getsockname()[0]
    self.socket.listen(self.sense_workers)

    # Address Lookup Setup
    # Address lookup is by the tuple (patient_id, device_id) -> IP address.
    # TODO: Under development! May be used in the future for PIMAP commands.
    self.addresses_by_id = {}

    # Multiprocess Setup
    self.running = multiprocessing.Value(ctypes.c_bool, True)
    self.running.value = True
    self.pimap_data_queue = multiprocessing.Queue()
    self.received_address_queue = multiprocessing.Queue()
    self.sense_worker_processes = []
    for i in range(self.sense_workers):
      worker_process = multiprocessing.Process(target=self._sense_worker, daemon=True)
      self.sense_worker_processes.append(worker_process)
      worker_process.start()
    self.pimap_worker_processes = []
    for i in range(self.pimap_workers):
      worker_process = multiprocessing.Process(
        target=self._create_pimap_data_and_add_to_queue, daemon=True)
      self.pimap_worker_processes.append(worker_process)
      worker_process.start()
    time.sleep(0.1)

  def _create_pimap_data_and_add_to_queue(self):
    while self.running.value:
      if not self.received_address_queue.empty():
        (unprocessed, address) = self.received_address_queue.get()
        processed = ";;".join(unprocessed) 
        # If valid PIMAP sample/metric is received add it to the queue.
        if pu.validate_datum(processed):
          pimap_data = list(map(lambda x: x + ";;", unprocessed))
          for pimap_datum in pimap_data:
            # Add lookup addresses of incoming PIMAP data.
            patient_id = pu.get_patient_id(pimap_datum)
            device_id = pu.get_device_id(pimap_datum)
            self.pimap_data_queue.put(pimap_datum)
        else:
          for datum in unprocessed:
            patient_id = address[0]
            device_id = address[1]
            sample = datum
            pimap_datum = pu.create_pimap_sample(self.sample_type, patient_id,
                                                 device_id, sample)
            self.pimap_data_queue.put(pimap_datum)
        # TODO: Under development! May be used in the future for PIMAP commands.
        self.addresses_by_id[(patient_id, device_id)] = address

  def _sense_worker(self):
    """Worker process

    Used internally to create TCP server processes.
    """
    sense_period = 0.001
    terminator = ";;"
    while self.running.value:
      try:
        (conn, address) = self.socket.accept()
        with conn:
          previous = ""
          received_coded = conn.recv(self.max_buffer_size)
          received = []
          terminator_count = 0
          while received_coded:
            stop_time = time.time() + sense_period
            while time.time() < stop_time:
              if not received_coded: break
              if ";;" in received_coded.decode():
                terminator_count += 1
              received_unprocessed = (previous + received_coded.decode()).split(";;")
              if len(received_unprocessed) == 1:
                previous = ""
                if received_unprocessed[0] != "":
                  received.append(received_unprocessed[0])
              else:
                previous = received_unprocessed[-1]
                received.extend(received_unprocessed[:-1])
              received_coded = conn.recv(self.max_buffer_size)
            if terminator_count >= 2:
              terminator_count = 0
              self.received_address_queue.put((received, address))
              received = []
      except socket.timeout: continue

  def sense(self):
    """Core interaction of PIMAP Sense TCP.

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
    """Safely stop the TCP server.

    Terminates server processes and closes the socket.
    """
    self.running.value = False
    # Empty queues or processes won't join.
    while not self.pimap_data_queue.empty(): self.pimap_data_queue.get()
    while not self.received_address_queue.empty(): self.received_address_queue.get()
    for worker_process in self.sense_worker_processes:
      worker_process.join()
    for worker_process in self.pimap_worker_processes:
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
