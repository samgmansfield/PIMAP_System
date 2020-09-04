"""PIMAP utilities are a common shared library for PIMAP components, such as
creating PIMAP samples/metrics as well as getting or setting information in a
PIMAP sample/metric.

License:
Author: Sam Mansfield
"""
import ast
import numpy as np
import pickle
import re
import time

def create_pimap_sample(sample_type, patient_id, device_id, sample, timestamp=None):
  """Creates a PIMAP sample.
  
  Arguments:
    sample_type: An alphanumeric value that conveys the type of a sample,
      e.g. pressure_bandage. It should not contain a ":" or ";".
    patient_id: An alphanumeric value that conveys the ID of a patient. It should
      not contain a ":" or ";".
    device_id: An alphanumeric value that conveys the ID of a device. It should not
      contain a ":" or ";".
    sample: The data that was sampled. It should not contain any of the keywords
      "sample_type", "patient_id", "device_id", "sample", or "timestamp".
    timestamp (optional): The epoch time in seconds. If a timestamp is not provided
      the current time is used.
  
  Returns:
    Returns a PIMAP sample represented as a string.
  
  Exceptions:
    ValueError:
      If a sample_type, patient_id, device_id contains a ":" or ";".
      If a sample contains any of the keywords "sample_type", "patient_id", "device_id",
        "sample", or "timestamp".
      If a timestamp cannot be converted to a float.
  """
  stype = str(sample_type)
  if ":" in stype or ";" in stype:
    raise ValueError("sample_type cannot contain a ':' or ';'.")
  
  pid = str(patient_id)
  if ":" in pid or ";" in pid:
    raise ValueError("pid cannot contain a ':' or ';'.")

  did = str(device_id)
  if ":" in did or ";" in did:
    raise ValueError("did cannot contain a ':' or ';'.")

  s = str(sample)
  # sample_type is not included as "sample" is in "sample_type".
  special_keys = ["patient_id", "device_id", "sample", "timestamp", ";"]
  if any(key in s for key in special_keys):
    raise ValueError("sample cannot contain any of the special keys:" +
                     str(special_keys))

  tstamp = str(time.time())
  if timestamp != None: tstamp = str(timestamp)
  try: tstamp_float = float(tstamp)
  except ValueError:
    raise ValueError("timestamp cannot be converted to a float.")

  return ("sample_type:" + stype + ";patient_id:" + pid + ";device_id:" + did +
          ";sample:" + s + ";timestamp:" + tstamp + ";;")

def create_pimap_metric(metric_type, pimap_datum, metric):
  """Creates a PIMAP metric.
  
  Arguments:
    metric_type: An alphanumeric value that conveys the type of a metric,
      e.g. objective_mobility. It should not contain a ":" or ";".
    pimap_datum: A PIMAP sample/metric.
    metric: The data represents the metric. It should not contain any of the keywords
      "metric_type", "patient_id", "device_id", "metric", or "timestamp".

  Exceptions:
    ValueError:
      If metric_type contains a ":" or ";".
      If metric contains the key words "metric_type", "patient_id", "device_id",
        "metric", or "timestamp".
  """
  mtype = str(metric_type)
  if ":" in mtype or ";" in mtype:
    raise ValueError("metric_type cannot contain a ':' or ';'.")

  pid = get_patient_id(pimap_datum)
  did = get_device_id(pimap_datum)

  m = str(metric)
  # metric_type is not included as "metric" is in "metric_type".
  special_keys = ["patient_id", "device_id", "metric", "timestamp", ";"]
  if any(key in m for key in special_keys):
    raise ValueError("sample cannot contain any of the special keys:" +
                     str(special_keys))
  
  tstamp = get_timestamp(pimap_datum)
  try: tstamp_float = float(tstamp)
  except ValueError:
    raise ValueError("timestamp cannot be converted to a float.")

  return ("metric_type:" + mtype + ";patient_id:" + pid + ";device_id:" + did +
          ";metric:" + m + ";timestamp:" + tstamp + ";;")

def get_sample_type(pimap_sample):
  """Gets the sample_type from a PIMAP sample.
    
  Arguments:
    pimap_sample: A PIMAP sample.

  Returns:
    Returns the sample_type as a string.

  Exceptions:
    If a sample_type is not found a ValueError is thrown.
  """
  match = re.search("sample[-_]type:([^;]+);", pimap_sample)
  if match: return match.group(1)
  else:
    raise ValueError("PIMAP sample is malformed and does not include a sample_type.")

def get_metric_type(pimap_metric):
  """Gets the metric_type from a PIMAP metric.
    
  Arguments:
    pimap_metric: A PIMAP metric.

  Returns:
    Returns the metric_type as a string.

  Exceptions:
    If a metric_type is not found a ValueError is thrown.
  """
  match = re.search("metric[-_]type:([^;]+);", pimap_metric)
  if match: return match.group(1)
  else:
    raise ValueError("PIMAP metric is malformed and does not include a metric_type.")

def get_type(pimap_datum):
  """Generalized way to return the sample_type/metric_type. 
  
  Arguments:
    pimap_datum: A PIMAP sample/metric.

  Returns:
    sample_type as a string if a PIMAP sample or metric_type as a string if a
      PIMAP metric.

  Exceptions:
    ValueError:
      If PIMAP datum is malformed, i.e. does not contain a sample_type or metric_type.
  """
  sample_match = re.search("sample[-_]type:", pimap_datum)
  if sample_match: return get_sample_type(pimap_datum)
  metric_match = re.search("metric[-_]type:", pimap_datum)
  if metric_match: return get_metric_type(pimap_datum)
  raise ValueError("PIMAP datum is malformed and does not include a sample_type or " +
                   "metric_type.")

def get_patient_id(pimap_datum):
  """Returns the patient_id of a PIMAP sample/metric.

  Arguments:
    pimap_datum: A PIMAP sample/metric.
  
  Returns:
    patient_id as a string. 

  Exceptions:
    ValueError:
      If PIMAP datum is malformed, i.e. does not contain a patient_id.
  """
  match = re.search("patient[-_]id:([^;]+);", pimap_datum)
  if match: return match.group(1)
  else:
    raise ValueError("PIMAP sample is malformed and does not include a patient_id.")

def get_device_id(pimap_datum):
  """Returns the device_id of a PIMAP sample/metric.

  Arguments:
    pimap_datum: A PIMAP sample/metric.
  
  Returns:
    device_id as a string. 

  Exceptions:
    ValueError:
      If PIMAP datum is malformed, i.e. does not contain a device_id.
  """
  match = re.search("device[-_]id:([^;]+);", pimap_datum)
  if match: return match.group(1)
  else:
    raise ValueError("PIMAP sample is malformed and does not include a device_id.")

def get_sample(pimap_sample):
  """Gets the sample from a PIMAP sample.
    
  Arguments:
    pimap_sample: A PIMAP sample.

  Returns:
    Returns the sample as a string.

  Exceptions:
    If a sample is not found a ValueError is thrown.
  """
  match = re.search("sample:([^;]+);", pimap_sample)
  if match: return match.group(1)
  else:
    raise ValueError("PIMAP sample is malformed and does not include a sample.")

def get_metric(pimap_metric):
  """Gets the metric from a PIMAP metric.
    
  Arguments:
    pimap_metric: A PIMAP metric.

  Returns:
    Returns the metric as a string.

  Exceptions:
    If a metric is not found a ValueError is thrown.
  """
  match = re.search("metric:([^;]+);", pimap_metric)
  if match: return match.group(1)
  else:
    raise ValueError("PIMAP metric is malformed and does not include a metric.")

def get_data(pimap_datum):
  """Generalized way to return the sample/metric. 
  
  Arguments:
    pimap_datum: A PIMAP sample/metric.

  Returns:
    sample as a string if a PIMAP sample or metric as a string if a PIMAP metric.

  Exceptions:
    ValueError:
      If PIMAP datum is malformed, i.e. does not contain a sample or metric.
  """
  sample_match = re.search("sample:", pimap_datum)
  if sample_match: return get_sample(pimap_datum)
  metric_match = re.search("metric:", pimap_datum)
  if metric_match: return get_metric(pimap_datum)
  raise ValueError("PIMAP datum is malformed and does not include a sample or metric")

def get_timestamp(pimap_datum):
  """Returns the timestamp of a PIMAP sample/metric.

  Arguments:
    pimap_datum: A PIMAP sample/metric.
  
  Returns:
    timestamp as a string. 

  Exceptions:
    ValueError:
      If PIMAP datum is malformed, i.e. does not contain a timestamp.
  """
  match = re.search("timestamp:([^;]+);", pimap_datum)
  if match: return match.group(1)
  else:
    raise ValueError("PIMAP datum is malformed and does not include a timestamp.")

def validate_datum(possible_pimap_datum):
  """Validates a PIMAP sample/metric.
  
  Arguments:
    possible_pimap_datum: A possible PIMAP sample/metric.

  Returns:
    True if possible_pimap_datum is a PIMAP sample/metric.
    False otherwise.
  """
  try:
    typ = get_type(possible_pimap_datum)
    pid = get_patient_id(possible_pimap_datum)
    did = get_device_id(possible_pimap_datum)
    d = get_data(possible_pimap_datum)
    tstamp = get_timestamp(possible_pimap_datum)
  except ValueError:
    return False
  return True

# Deprecated methods: May be used in the future.
#
# TODO: This is not used. It could be useful, but less code is less code to support.
#       Delete and test.
# set_type: A generalized way to set the sample or metric type of a PIMAP datum.
#def set_type(pimap_datum, new_type):
#  sample_type = get_sample_type(pimap_datum)
#  metric_type = get_metric_type(pimap_datum)
#  if sample_type == None:
#    return set_metric_type(pimap_datum, new_type)
#  return set_sample_type(pimap_datum, new_type)
## TODO: This is not used anywhere. Delete and test.
#
## set_sample: Sets the sample of a PIMAP sample
#def set_sample(pimap_sample, sample):
#  return re.sub("sample:[^;]+;", "sample:" + sample + ";", pimap_sample)
#
## TODO: This is not used anywhere. Delete and test.
#def set_metric(pimap_metric, metric):
#    return re.sub("metric:[^;]+;", "metric:" + metric + ";", pimap_metric)
#
## TODO: This is not used anywhere. Delete and test.
#def set_timestamp(pimap_datum, timestamp=None):
#    if timestamp == None:
#        timestamp = time.time()
#    return re.sub("timestamp:[^;]+;", "timestamp:" + str(timestamp) + ";", pimap_datum)
#
## TODO: This does not seem like a utility function. Delete this and test.
## create_pimap_metric_from_many: Creates a PIMAP metric from many PIMAP data.
#def create_pimap_metric_from_many(metric_type, pimap_data, metric):
#  pimap_datum = pimap_data[0]
#  timestamps = list(map(lambda x: float(get_timestamp(x)), pimap_data))
#  timestamp = np.mean(timestamps)
#  return ("metric_type:" + str(metric_type) + ";patient_id:" +
#          get_patient_id(pimap_datum) + ";device_id:" + get_device_id(pimap_datum) +
#          ";metric:" + str(metric) + ";timestamp:" + str(timestamp) +
#          ";;")
#
## TODO: This is not used. It could be useful, but less code is less code to support.
##       Delete this and test.
## set_sample_Type: Sets the sample_type of a PIMAP sample.
#def set_sample_type(pimap_sample, new_sample_type):
#  return re.sub("sample_type:[^;]+;", "sample_type:" + new_sample_type + ";",
#                pimap_sample)
#
#
## TODO: This is not used. It could be useful, but less code is less code to support.
##       Delete and test.
## set_metric_type: Sets the metric_type of a PIMAP metric.
#def set_metric_type(pimap_metric, new_metric_type):
#  return re.sub("metric_type:[^;]+;", "metric_type:" + new_metric_type + ";",
#                pimap_metric)
