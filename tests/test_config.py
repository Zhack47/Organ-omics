import sys
sys.path.append("../organomics")
from utils.parse import config_total_seg


class TestConfig:
    organs_to_extract, labels_dict, new_correspondence = config_total_seg("data/Dataset001_Test/dataset.json")
    
    def test_config_nb_tasks(self):
        assert list(self.organs_to_extract.keys()) == ["total", "abdominal_muscles"]

    def test_config_beckground_exists(self):
        assert "background" in self.labels_dict.keys()

    def test_config_background_is_zero(self):
        assert int(self.labels_dict["background"]) == 0

    def test_config_nb_labels(self):
        assert len(self.labels_dict.keys()) == 6

    def test_config_nb_orig_labels(self):
        corr_labels = []
        for task in self.new_correspondence:
            for organ_group in self.new_correspondence[task]:
                    for item in self.new_correspondence[task][organ_group]:
                        corr_labels.append(item)
        task_labels = []
        for task in self.organs_to_extract:
            for item in self.organs_to_extract[task]:
                    task_labels.append(item)
        assert corr_labels==task_labels
