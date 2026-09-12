import copy
import unittest

from scripts.build_operating_point_transport_report import build
from scripts.validate_operating_point_transport_report import validate


class OperatingPointTransportReportTest(unittest.TestCase):
    def test_real_bundle_is_complete(self) -> None:
        summary = validate(build())
        self.assertEqual(summary["matched_cells"], 192)
        self.assertEqual(summary["ranking_records"], 128)

    def test_gap_tampering_fails(self) -> None:
        report = copy.deepcopy(build())
        report["matched_analysis"]["families"][0]["cells"][0]["observed_matched_gap"] += 0.01
        with self.assertRaisesRegex(ValueError, "arithmetic"):
            validate(report)

    def test_schema_metadata_tampering_fails(self) -> None:
        report = copy.deepcopy(build())
        report["study"]["evidence_timing"] = "confirmatory"
        with self.assertRaisesRegex(ValueError, "schema validation"):
            validate(report)

    def test_duplicate_family_fails(self) -> None:
        report = copy.deepcopy(build())
        report["matched_analysis"]["families"][1] = copy.deepcopy(report["matched_analysis"]["families"][0])
        with self.assertRaisesRegex(ValueError, "unique families"):
            validate(report)

    def test_missing_ranking_fails(self) -> None:
        report = copy.deepcopy(build())
        report["full_n_rankings"]["records"].pop()
        with self.assertRaisesRegex(ValueError, "schema validation|ranking matrix"):
            validate(report)

    def test_gate_summary_tampering_fails(self) -> None:
        report = copy.deepcopy(build())
        family = report["matched_analysis"]["families"][0]
        family["positive_cell_count"] += 1
        with self.assertRaisesRegex(ValueError, "gate summary"):
            validate(report)

    def test_artifact_hash_tampering_fails(self) -> None:
        report = copy.deepcopy(build())
        report["artifacts"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "artifact hash"):
            validate(report)

    def test_frozen_threshold_metadata_tampering_fails(self) -> None:
        report = copy.deepcopy(build())
        report["matched_analysis"]["families"][0]["threshold"]["parameters"]["quantile"] = 0.5
        with self.assertRaisesRegex(ValueError, "threshold metadata"):
            validate(report)


if __name__ == "__main__":
    unittest.main()
