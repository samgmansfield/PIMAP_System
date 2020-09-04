"""Unittest file for pimaputilities.py

License:
Author: Sam Mansfield
"""
import ast
import unittest
import time
from pimap import pimaputilities as pu

class PimapUtilitiesTestCase(unittest.TestCase):
  def test_create_pimap_sample_correct_usage(self):
    # Test using all string arguments without getters.
    sample_type = "test_sample"
    patient_id = "1"
    device_id = "1"
    sample = "{'test':[1, 2, 3, 4]}"
    timestamp = str(time.time())
    pimap_sample = pu.create_pimap_sample(sample_type, patient_id, device_id, sample,
                                          timestamp)
    correct_pimap_sample = ("sample_type:" + sample_type + ";patient_id:" + patient_id +
      ";device_id:" + device_id + ";sample:" + sample + ";timestamp:" + timestamp + ";;")
    self.assertEqual(pimap_sample, correct_pimap_sample)

    # Test using all non-string arguments without getters.
    sample_type = 1
    patient_id = 2
    device_id = 3
    sample = {"test":[1, 2, 3, 4]}
    timestamp = time.time()
    pimap_sample = pu.create_pimap_sample(sample_type, patient_id, device_id, sample,
                                          timestamp)
    correct_pimap_sample = ("sample_type:" + str(sample_type) + ";patient_id:" +
      str(patient_id) + ";device_id:" + str(device_id) + ";sample:" + str(sample) +
      ";timestamp:" + str(timestamp) + ";;")
    self.assertEqual(pimap_sample, correct_pimap_sample)

    # Test without timestamp.
    sample_type = "test_sample"
    patient_id = "1"
    device_id = "1"
    sample = "{'test':[1, 2, 3, 4]}"
    test_timestamp = time.time()
    pimap_sample = pu.create_pimap_sample(sample_type, patient_id, device_id, sample)
    gotten_timestamp = float(pu.get_timestamp(pimap_sample))
    self.assertTrue(gotten_timestamp - test_timestamp < 0.001)

  def test_create_pimap_sample_incorrect_usage(self):
    # Test invalid sample_type.
    sample_type = "test_sample;"
    patient_id = "1"
    device_id = "1"
    sample = "{'test':[1, 2, 3, 4]}"
    timestamp = str(time.time())
    self.assertRaises(ValueError, pu.create_pimap_sample, sample_type, patient_id, 
      device_id, sample, timestamp)
   
    # Test invalid patient_id.
    sample_type = "test_sample"
    patient_id = "1:"
    device_id = "1"
    sample = "{'test':[1, 2, 3, 4]}"
    timestamp = str(time.time())
    self.assertRaises(ValueError, pu.create_pimap_sample, sample_type, patient_id, 
      device_id, sample, timestamp)
    
    # Test invalid device_id.
    sample_type = "test_sample"
    patient_id = "1"
    device_id = "1;"
    sample = "{'test':[1, 2, 3, 4]}"
    timestamp = str(time.time())
    self.assertRaises(ValueError, pu.create_pimap_sample, sample_type, patient_id, 
      device_id, sample, timestamp)
    
    # Test invalid sample.
    sample_type = "test_sample"
    patient_id = "1"
    device_id = "1"
    sample = "{'sample_type':[1, 2, 3, 4]}"
    timestamp = str(time.time())
    self.assertRaises(ValueError, pu.create_pimap_sample, sample_type, patient_id, 
      device_id, sample, timestamp)
    
    # Test invalid timestamp.
    sample_type = "test_sample"
    patient_id = "1"
    device_id = "1"
    sample = "{'test':[1, 2, 3, 4]}"
    timestamp = "test"
    self.assertRaises(ValueError, pu.create_pimap_sample, sample_type, patient_id, 
      device_id, sample, timestamp)

  def test_create_pimap_metric_correct_usage(self):
    sample_type = "test_sample"
    patient_id = "test"
    device_id = "3"
    sample = {"test":[1, 2, 3, 4]}
    timestamp = str(time.time())
    pimap_sample = pu.create_pimap_sample(sample_type, patient_id, device_id, sample,
                                          timestamp)
    metric_type = "test_metric"
    metric = "{'new_analysis':4}"
    pimap_metric = pu.create_pimap_metric(metric_type, pimap_sample, metric)
    correct_pimap_metric = ("metric_type:" + metric_type + ";patient_id:" + patient_id +
      ";device_id:" + device_id + ";metric:" + metric + ";timestamp:" + timestamp + ";;")
    self.assertEqual(pimap_metric, correct_pimap_metric)

  def test_create_pimap_metric_incorrect_usage(self):
    sample_type = "test_sample"
    patient_id = "test"
    device_id = "3"
    sample = {"test":[1, 2, 3, 4]}
    timestamp = str(time.time())
    pimap_sample = pu.create_pimap_sample(sample_type, patient_id, device_id, sample,
                                          timestamp)
    metric_type = "test_metric;"
    metric = "{'new_analysis':4}"
    self.assertRaises(ValueError, pu.create_pimap_metric, metric_type, pimap_sample,
                      metric)
    
    metric_type = "test_metric"
    metric = "{'new_metric':4}"
    self.assertRaises(ValueError, pu.create_pimap_metric, metric_type, pimap_sample,
                      metric)

  def test_getters_correct_usage(self):
    sample_type = "test_sample"
    patient_id = "1"
    device_id = "1"
    sample = {"test":[1, 2, 3, 4]}
    timestamp = str(time.time())
    pimap_sample = pu.create_pimap_sample(sample_type, patient_id, device_id, sample,
                                          timestamp)
    metric_type = "test_metric"
    metric = {"new_analysis":5}
    pimap_metric = pu.create_pimap_metric(metric_type, pimap_sample, metric)

    # Test get_type PIMAP sample.
    gotten_type = pu.get_type(pimap_sample)
    self.assertEqual(gotten_type, sample_type)
    
    # Test get_type PIMAP metric.
    gotten_type = pu.get_type(pimap_metric)
    self.assertEqual(gotten_type, metric_type)
    
    # Test get_patient_id PIMAP sample.
    gotten_patient_id = pu.get_patient_id(pimap_sample)
    self.assertEqual(gotten_patient_id, patient_id)
    
    # Test get_patient_id PIMAP metric.
    gotten_patient_id = pu.get_patient_id(pimap_metric)
    self.assertEqual(gotten_patient_id, patient_id)
    
    # Test get_device_id PIMAP sample.
    gotten_device_id = pu.get_device_id(pimap_sample)
    self.assertEqual(gotten_device_id, device_id)
    
    # Test get_device_id PIMAP metric.
    gotten_device_id = pu.get_device_id(pimap_metric)
    self.assertEqual(gotten_device_id, device_id)

    # Test get_data PIMAP sample.
    gotten_sample_string = pu.get_data(pimap_sample)
    gotten_sample = ast.literal_eval(gotten_sample_string)
    self.assertEqual(gotten_sample, sample)
    
    # Test get_data PIMAP sample.
    gotten_sample_string = pu.get_data(pimap_sample)
    gotten_sample = ast.literal_eval(gotten_sample_string)
    self.assertEqual(gotten_sample, sample)
    
    # Test get_data PIMAP metric.
    gotten_metric_string = pu.get_data(pimap_metric)
    gotten_metric = ast.literal_eval(gotten_metric_string)
    self.assertEqual(gotten_metric, metric)

    # Test get_timestamp PIMAP sample.
    gotten_timestamp = pu.get_timestamp(pimap_sample)
    self.assertEqual(gotten_timestamp, timestamp)
    
    # Test get_timestamp PIMAP metric.
    gotten_timestamp = pu.get_timestamp(pimap_metric)
    self.assertEqual(gotten_timestamp, timestamp)

  def test_getters_incorrect_usage(self):
    invalid_pimap_sample = "invalid pimap sample"
    invalid_pimap_metric = "invalid pimap metric"
    
    # Test no type PIMAP sample
    self.assertRaises(ValueError, pu.get_type, invalid_pimap_sample)
    
    # Test no type PIMAP metric
    self.assertRaises(ValueError, pu.get_type, invalid_pimap_metric)

    # Test no patient_id PIMAP sample
    self.assertRaises(ValueError, pu.get_patient_id, invalid_pimap_sample)
    
    # Test no patient_id PIMAP metric
    self.assertRaises(ValueError, pu.get_patient_id, invalid_pimap_metric)
    
    # Test no device_id PIMAP sample
    self.assertRaises(ValueError, pu.get_device_id, invalid_pimap_sample)
    
    # Test no device_id PIMAP metric
    self.assertRaises(ValueError, pu.get_device_id, invalid_pimap_metric)
    
    # Test no data PIMAP sample
    self.assertRaises(ValueError, pu.get_data, invalid_pimap_sample)
    
    # Test no data PIMAP metric 
    self.assertRaises(ValueError, pu.get_data, invalid_pimap_metric)
    
    # Test no timestamp PIMAP sample
    self.assertRaises(ValueError, pu.get_timestamp, invalid_pimap_sample)
    
    # Test no timestamp PIMAP metric
    self.assertRaises(ValueError, pu.get_timestamp, invalid_pimap_metric)

  def test_getters_unusual_usage(self): 
    # Test creating a sample with the word "metric" and creating a PIMAP metric from that
    # sample and then using get_data on the PIMAP metric.
    sample_type = "test_sample"
    patient_id = "Aaron"
    device_id = "1"
    sample = {"test":"metric:[1, 2, 3]"}
    timestamp = str(time.time())
    pimap_sample = pu.create_pimap_sample(sample_type, patient_id, device_id, sample,
                                          timestamp)
    metric_type = "test_metric"
    metric = {"new_analysis":5}
    pimap_metric = pu.create_pimap_metric(metric_type, pimap_sample, metric)

    gotten_metric_string = pu.get_data(pimap_metric)
    gotten_metric = ast.literal_eval(gotten_metric_string)
    self.assertEqual(gotten_metric, metric)

  def test_validate_datum_correct_usage(self):
    sample_type = "test_sample"
    patient_id = "Aaron"
    device_id = "1"
    sample = {"test":[1, 2, 3]}
    timestamp = str(time.time())
    pimap_sample = pu.create_pimap_sample(sample_type, patient_id, device_id, sample,
                                          timestamp)
    metric_type = "test_metric"
    metric = {"new_analysis":5}
    pimap_metric = pu.create_pimap_metric(metric_type, pimap_sample, metric)
   
    self.assertTrue(pu.validate_datum(pimap_sample))
    self.assertTrue(pu.validate_datum(pimap_metric))

  def test_validate_datum_incorrect_usage(self):
    invalid_pimap_sample = "invalid pimap sample"
    invalid_pimap_metric = "invalid pimap metric"
    self.assertFalse(pu.validate_datum(invalid_pimap_sample)) 
    self.assertFalse(pu.validate_datum(invalid_pimap_metric)) 

    # Test incomplete PIMAP sample
    incomplete_pimap_sample = "sample_type:test;patient_id:1"
    incomplete_pimap_metric = "metric_type:test;metric:[1, 2, 3];;"
    self.assertFalse(pu.validate_datum(incomplete_pimap_sample)) 
    self.assertFalse(pu.validate_datum(incomplete_pimap_metric)) 

if __name__ == "__main__":
  unittest.main()
