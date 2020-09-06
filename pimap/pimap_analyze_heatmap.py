import pickle

from sentineltoolkit.sentinel_analysis import analyze_sample_discrete_heatmap

class PimapAnalyzeHeatmap:
    """
    Converts a calibrated sentinel bandage scan into a heatmap.
    """
    def __init__(self, frequency, analysis_type):
        # Which frequency to display on the heatmap
        self.frequency = frequency
        # Which heatmap type: 0 for discrete, 1 for continuous
        self.analysis_type = analysis_type

    def analyze(self, pimap_samples):
        pimap_metrics = []

        for pimap_sample in pimap_samples:
            split_pimap_sample = pimap_sample.split(";")

            pickled_scan = split_pimap_sample[3][7:].encode()

            sensor_data = pickle.loads(pickled_scan)

            if self.analysis_type == 0:
                heatmap_data = analyze_sample_discrete_heatmap(sensor_data, self.frequency)
            elif self.analysis_type == 1:
                heatmap_data = analyze_sample_continuous_heatmap(sensor_data, self.frequency)
            else:
                assert False

            metric_results = pickle.dumps(heatmap_data, 0).decode()

            pimap_metric = "metric:"

            pimap_metric += metric_results

            split_pimap_sample[0] = "metric_type:SentinelHeatmap"
            split_pimap_sample[3] = pimap_metric

            pimap_metric = ";".join(split_pimap_sample)

            pimap_metrics.append(pimap_metric)

        return pimap_metrics
