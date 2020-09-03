"""PIMAP Store component using Kafka.

PIMAP Store Kafka is an abstraction of Kafka using PIMAP. This component does not start
a Kafka broker, but instead assumes one is already running and interfaces given the
associated Kafka host and port.

License:
Author: Sam Mansfield
"""
import ast
import random
import string
import sys
import time
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Consumer
from confluent_kafka import Producer
from confluent_kafka import KafkaException
from pimap import pimaputilities as pu

class PimapStoreKafka:
  def __init__(self, host="localhost", port=9092, system_samples=False):
    """Constructor for PIMAP Store Kafka

    Arguments:
      host (optional): The host where Kafka can be accessed. Defaults to "local"host.
      port (optional): The port where Kafka can be accessed. Defaults to 9092.
      system_samples (optional): A boolean value that indicates whether system_samples
        are produced that report the throughput of this component. Defaults to False.

    Exceptions:
      KafkaException:
        If host and port are an invalid Kafka broker.
    """
    self.broker = str(host) + ":" + str(port)
    self.system_samples = bool(system_samples)
    self.system_samples_period = 1.0
    self.stored_system_samples_updated = time.time()
    self.retrieved_system_samples_updated = time.time()

    # No exception is raised when creating the admin so we call list_topics to see
    # if the broker is valid.
    self.admin = AdminClient({"bootstrap.servers":self.broker})
    self.admin.list_topics(timeout=10.0)

    self.consumer_dict = {}
    self.num_messages = 100
    self.timeout = 0.1
    self.producer = Producer({"bootstrap.servers":self.broker})
    self.retrieved_data = 0
    self.stored_data = 0
    self.stored_topics = set()

  def store(self, pimap_data):
    """ Stores PIMAP data into Kafka. A core interaction of PIMAP Store Kafka.

    Arguments:
      pimap_data: A list of PIMAP data to be stored into Kafka.

    Exceptions:
      TypeError:
        If pimap_data is not a list.
      ValueError:
        If pimap_data contains a non-PIMAP data.
    """
    if not isinstance(pimap_data, list):
      raise TypeError("The argument pimap_data must be a list.")

    valid_pimap_data = list(map(pu.validate_datum, pimap_data))
    # If pimap_data is an empty list we still want to continue, this way we can
    # still return system_samples.
    if not any(valid_pimap_data) and len(pimap_data) != 0:
      raise ValueError("Invalid data in pimap_data.")

    for pimap_datum in pimap_data:
      topic = pu.get_type(pimap_datum)
      self.stored_topics.add(topic)
      key = pu.get_patient_id(pimap_datum)
      value = pimap_datum
      try:
        self.producer.produce(topic, value, key)
      except BufferError as e:
        self.producer.flush()
        self.producer.produce(topic, value, key)

    pimap_system_samples = []
    if self.system_samples:
      self.stored_data += len(pimap_data)
      if time.time() - self.stored_system_samples_updated > self.system_samples_period:
        sample_type = "system_samples"
        patient_id = "store_store"
        device_id = self.stored_topics
        sample = {"throughput":(self.stored_data/
                                (time.time() - self.stored_system_samples_updated)),
                  "queue_length":len(self.producer)}
        pimap_system_samples.append(pu.create_pimap_sample(sample_type, patient_id,
                                                           device_id, sample))
        self.stored_system_samples_updated = time.time()
        self.stored_data = 0

    return pimap_system_samples

  def retrieve(self, sample_or_metric_type, patient_id=None):
    """Retrieves PIMAP data from Kafka. A core interaction of PIMAP Store Kafka.

    Arguments:
      sample_or_metric_type: A sample_type or metric_type used to subscribe to
        a Kafka topic.
      patient_id (optional): An optional argument to filter retrieved data so that
        only data from one patient_id is returned. Defaults to None, which will
        not filter the retrieved data.

    Returns:
      A list of PIMAP data retrieved from Kafka.
    """
    topic = str(sample_or_metric_type)
    if topic not in self.consumer_dict:
      random_chars = [random.choice(string.ascii_letters) for i in range(10)]
      group_id = "".join(random_chars)
      self.consumer_dict[topic] = Consumer({"bootstrap.servers":self.broker,
                                            "group.id":group_id,
                                            "auto.offset.reset":"earliest"})
      self.consumer_dict[topic].subscribe([topic])
    kafka_messages = self.consumer_dict[topic].consume(num_messages=self.num_messages,
                                                       timeout=self.timeout)
    # If a timeout occured
    if len(kafka_messages) == 0:
      self.num_messages = int(self.num_messages/2)
    elif len(kafka_messages) >= self.num_messages:
      self.num_messages = (self.num_messages*2)
    if self.num_messages < 1: self.num_messages = 1
    elif self.num_messages > 1000000: self.num_messages = 1000000

    try:
      kafka_messages_wo_errors = list(filter(lambda x: x.error() == None,
                                             kafka_messages))
    except KafkaException:
      kafka_messages_wo_errors = []
      for message in kafka_messages:
        try:
          if message.error() == None: kafka_messages_wo_errors.append(message)
        except KafkaException:
          print(message.error().code())

    pimap_data = list(map(lambda x: x.value().decode(), kafka_messages_wo_errors))
    if patient_id != None:
      pimap_data = list(filter(lambda x: pu.get_patient_id(x) == patient_id, pimap_data))

    pimap_system_samples = []
    if self.system_samples:
      self.retrieved_data += len(pimap_data)
      if (time.time() - self.retrieved_system_samples_updated >
          self.system_samples_period):
        sample_type = "system_samples"
        patient_id = "store_retrieve" 
        device_id = self.consumer_dict.keys()
        sample = {"throughput":(self.retrieved_data/
                                (time.time() - self.retrieved_system_samples_updated)),
                  "num_messages":self.num_messages,
                  "messages":len(kafka_messages),
                  "timeout":self.timeout}
        pimap_system_samples.append(pu.create_pimap_sample(sample_type, patient_id,
                                                           device_id, sample))
        self.retrieved_system_samples_updated = time.time()
        self.retrieved_data = 0

    return pimap_data + pimap_system_samples

  def close(self):
    """Unsubscribes and closes all consumers."""
    for consumer in self.consumer_dict.values():
      consumer.unsubscribe()
      consumer.close()
