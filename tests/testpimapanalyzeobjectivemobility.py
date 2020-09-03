"""Unittest file for pimapanalyzeobjectivemobility.py

To run the tests in the top level directory type the command:
PYTHONPATH=. python tests/testpimapanalyzeobjectivemobility.py

License:
Author: Sam Mansfield
"""
import ast
import numpy as np
import time
import unittest
from pimap import pimapanalyzeobjectivemobility as paom
from pimap import pimaputilities as pu

class PimapAnalyzeObjectiveMobilityTestCase(unittest.TestCase):
  def test_creating_incorrect_usage(self):
    # Test using an invalid max_pressure value.
    max_pressure = "invalid"
    self.assertRaises(ValueError, paom.PimapAnalyzeObjectiveMobility, max_pressure)

  def test_analyze_correct_usage(self):
    # Test using system_system samples with an empty list.
    analyze = paom.PimapAnalyzeObjectiveMobility(system_samples=True)
    system_samples = analyze.analyze([])
    while len(system_samples) == 0:
      system_samples = analyze.analyze([])

    sample = ast.literal_eval(pu.get_data(system_samples[0]))
    throughput_in = sample["throughput_in"]
    throughput_out = sample["throughput_out"]
    correct_throughput = 0.0
    self.assertEqual(throughput_in, correct_throughput)
    self.assertEqual(throughput_out, correct_throughput)

    # Test x_angle and y_angle flat plane.
    device_type = "pressure_bandage"
    patient_id = "1"
    device_id = "1"
    sample = {}
    sample["pressure_bandage"] = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
    pimap_sample = pu.create_pimap_sample(device_type, patient_id, device_id,
                                          str(sample))
    max_pressure = 100.0
    analyze = paom.PimapAnalyzeObjectiveMobility(max_pressure)
    time.sleep(analyze.aggregation_period)
    pimap_metrics = analyze.analyze([pimap_sample])
    metric_string = pu.get_metric(pimap_metrics[0])
    metric = ast.literal_eval(metric_string)
    x_angle = metric["x_angle"]
    correct_x_angle = 0.0
    self.assertEqual(x_angle, correct_x_angle)
    y_angle = metric["y_angle"]
    correct_y_angle = 0.0
    self.assertEqual(y_angle, correct_y_angle)

    # Test x_angle 45 degree plane.
    device_type = "pressure_bandage"
    patient_id = "1"
    device_id = "1"
    sample = {}
    sample["pressure_bandage"] = [[0,1,2,3],[0,1,2,3],[0,1,2,3],[0,1,2,3]]
    pimap_sample = pu.create_pimap_sample(device_type, patient_id, device_id,
                                          str(sample))
    max_pressure = 3.0
    analyze = paom.PimapAnalyzeObjectiveMobility(max_pressure)
    time.sleep(analyze.aggregation_period)
    pimap_metrics = analyze.analyze([pimap_sample])
    metric_string = pu.get_metric(pimap_metrics[0])
    metric = ast.literal_eval(metric_string)
    x_angle = round(metric["x_angle"], 5)
    correct_x_angle = 45.0
    self.assertEqual(x_angle, correct_x_angle)
    y_angle = round(metric["y_angle"], 5)
    correct_y_angle = 0.0
    self.assertEqual(x_angle, correct_x_angle)

    # Test x_angle -45 degree plane.
    device_type = "pressure_bandage"
    patient_id = "1"
    device_id = "1"
    sample = {}
    sample["pressure_bandage"] = [[3,2,1,0],[3,2,1,0],[3,2,1,0],[3,2,1,0]]
    pimap_sample = pu.create_pimap_sample(device_type, patient_id, device_id,
                                          str(sample))
    maxPressure = 3.0
    analyze = paom.PimapAnalyzeObjectiveMobility(max_pressure)
    time.sleep(analyze.aggregation_period)
    pimap_metrics = analyze.analyze([pimap_sample])
    metric_string = pu.get_metric(pimap_metrics[0])
    metric = ast.literal_eval(metric_string)
    x_angle = round(metric["x_angle"], 5)
    correct_x_angle = -45.0
    self.assertEqual(x_angle, correct_x_angle)
    y_angle = round(metric["y_angle"], 5)
    correct_y_angle = 0.0
    self.assertEqual(y_angle, correct_y_angle)

    # Test y_angle 45 degree plane.
    device_type = "pressure_bandage"
    patient_id = "1"
    device_id = "1"
    sample = {}
    sample["pressure_bandage"] = [[0,0,0,0],[1,1,1,1],[2,2,2,2],[3,3,3,3]]
    pimap_sample = pu.create_pimap_sample(device_type, patient_id, device_id,
                                          str(sample))
    max_pressure = 3.0
    analyze = paom.PimapAnalyzeObjectiveMobility(max_pressure)
    time.sleep(analyze.aggregation_period)
    pimap_metrics = analyze.analyze([pimap_sample])
    metric_string = pu.get_metric(pimap_metrics[0])
    metric = ast.literal_eval(metric_string)
    x_angle = round(metric["x_angle"], 5)
    correct_x_angle = 0.0
    self.assertEqual(x_angle, correct_x_angle)
    y_angle = round(metric["y_angle"], 5)
    correct_y_angle = 45.0
    self.assertEqual(y_angle, correct_y_angle)

    # Test y_angle -45 degree plane.
    device_type = "pressure_bandage"
    patient_id = "1"
    device_id = "1"
    sample = {}
    sample["pressure_bandage"] = [[3,3,3,3],[2,2,2,2],[1,1,1,1],[0,0,0,0]]
    pimap_sample = pu.create_pimap_sample(device_type, patient_id, device_id,
                                          str(sample))
    max_pressure = 3.0
    analyze = paom.PimapAnalyzeObjectiveMobility(max_pressure)
    time.sleep(analyze.aggregation_period)
    pimap_metrics = analyze.analyze([pimap_sample])
    metric_string = pu.get_metric(pimap_metrics[0])
    metric = ast.literal_eval(metric_string)
    x_angle = round(metric["x_angle"], 5)
    correct_x_angle = 0.0
    self.assertEqual(x_angle, correct_x_angle)
    y_angle = round(metric["y_angle"], 5)
    correct_y_angle = -45.0
    self.assertEqual(y_angle, correct_y_angle)

    # Test x_angle, y_angle 45 degree plane.
    device_type = "pressure_bandage"
    patient_id = "1"
    device_id = "1"
    sample = {}
    sample["pressure_bandage"] = [[0,1,2,3],[1,2,3,4],[2,3,4,5],[3,4,5,6]]
    pimap_sample = pu.create_pimap_sample(device_type, patient_id, device_id,
                                          str(sample))
    max_pressure = 3.0
    analyze = paom.PimapAnalyzeObjectiveMobility(max_pressure)
    time.sleep(analyze.aggregation_period)
    pimap_metrics = analyze.analyze([pimap_sample])
    metric_string = pu.get_metric(pimap_metrics[0])
    metric = ast.literal_eval(metric_string)
    x_angle = round(metric["x_angle"], 5)
    correct_x_angle = 45.0
    self.assertEqual(x_angle, correct_x_angle)
    y_angle = round(metric["y_angle"], 5)
    correct_y_angle = 45.0
    self.assertEqual(y_angle, correct_y_angle)

    # Test xy_gradient and movements_per_min.
    device_type = "pressure_bandage"
    patient_id = "1"
    device_id = "1"
    sample_0 = {}
    sample_0["pressure_bandage"] = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
    sample_45 = {}
    sample_45["pressure_bandage"] = [[0,1,2,3],[0,1,2,3],[0,1,2,3],[0,1,2,3]]
    sample_neg_45 = {}
    sample_neg_45["pressure_bandage"] = [[3,2,1,0],[3,2,1,0],[3,2,1,0],[3,2,1,0]]

    max_pressure = 3.0
    analyze = paom.PimapAnalyzeObjectiveMobility(max_pressure)
    time.sleep(analyze.aggregation_period)

    # Send x_angle 0, 45, 0, -45 degree plane PIMAP samples in sequence.
    pimap_samples = []
    correct_angles = []
    # Because we are generating four PIMAP samples per iteration this will result
    # in four times the movements_per_min_period.
    for i in range(analyze.movements_per_min_period):
      pimap_samples.append(pu.create_pimap_sample(device_type, patient_id, device_id,
                                                  str(sample_0)))
      correct_angles.append(0.0)
      pimap_samples.append(pu.create_pimap_sample(device_type, patient_id, device_id,
                                                  str(sample_45)))
      correct_angles.append(45.0)
      pimap_samples.append(pu.create_pimap_sample(device_type, patient_id, device_id,
                                                  str(sample_0)))
      correct_angles.append(0.0)
      pimap_samples.append(pu.create_pimap_sample(device_type, patient_id, device_id,
                                                  str(sample_neg_45)))
      correct_angles.append(-45.0)

    pimap_metrics = analyze.analyze(pimap_samples)

    gradient_pimap_metrics = list(filter(lambda x: "xy_gradient" in ast.literal_eval(
                                                   pu.get_metric(x)),
                                         pimap_metrics))
    metrics = list(map(lambda x: ast.literal_eval(pu.get_metric(x)), pimap_metrics))
    filtered_gradient_metrics = list(filter(lambda x: "xy_gradient" in x, metrics))
    self.assertEqual(len(gradient_pimap_metrics), len(filtered_gradient_metrics))

    gradients = list(map(lambda x: x["xy_gradient"], filtered_gradient_metrics)) 
    correct_gradients = np.abs(np.gradient(correct_angles))
    for gradient, correct_gradient in zip(gradients, correct_gradients):
      self.assertEqual(gradient, correct_gradient)

    filtered_movement_metrics = list(filter(lambda x: "movements_per_min" in x, metrics))
    movements = list(map(lambda x: x["movements_per_min"], filtered_movement_metrics))
    self.assertTrue(len(correct_gradients) > analyze.movements_per_min_period)
    correct_movements = []
    for i in range(len(correct_gradients)):
      window_start = i
      window_end = i + analyze.movements_per_min_period
      # The metric movements_per_min is a sliding window, so at each iteration make sure
      # the end of the window is in range, otherwise we have checked all windows.
      if len(correct_gradients) > window_end:
        gradient_pimap_metrics_window = gradient_pimap_metrics[window_start:window_end]
        gradient_window = np.array(correct_gradients[window_start:window_end])
        timestamps = list(map(lambda x: float(pu.get_timestamp(x)),
                              gradient_pimap_metrics_window))
        elapsed_time = timestamps[-1] - timestamps[0]
        correct_movement = 60.0*np.sum(gradient_window > 2)/elapsed_time
        correct_movements.append(correct_movement)
      else: break

    for movement, correct_movement in zip(movements, correct_movements):
      self.assertEqual(movement, correct_movement)

  def test_analyze_incorrect_usage(self):
    # Test passing a pimap_sample instead of a list of pimap_samples
    analyze = paom.PimapAnalyzeObjectiveMobility()
    device_type = "pressure_bandage"
    patient_id = "1"
    device_id = "1"
    sample = {}
    sample["pressure_bandage"] = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
    pimap_sample = pu.create_pimap_sample(device_type, patient_id, device_id,
                                          str(sample))
    self.assertRaises(TypeError, analyze.analyze, pimap_sample)

    # Test passing a list of non-PIMAP data.
    analyze = paom.PimapAnalyzeObjectiveMobility()
    invalid_pimap_samples = ["nonsense", "invalid_data"]
    self.assertRaises(ValueError, analyze.analyze, invalid_pimap_samples)

if __name__ == "__main__":
    unittest.main()
