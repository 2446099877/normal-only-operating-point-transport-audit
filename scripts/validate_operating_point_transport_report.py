from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

try:
    from scripts.build_operating_point_transport_report import THRESHOLDS
except ModuleNotFoundError:  # direct script execution from repository root
    from build_operating_point_transport_report import THRESHOLDS

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "experiments" / "OPERATING_POINT_TRANSPORT_REPORT_SCHEMA_V1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(report: dict[str, object]) -> dict[str, object]:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    try:
        Draft202012Validator(schema).validate(report)
    except ValidationError as exc:
        raise ValueError(f"schema validation failed: {exc.message}") from exc
    if set(report) != {"schema_version", "study", "matched_analysis", "full_n_rankings", "artifacts"}:
        raise ValueError("unexpected top-level report fields")
    study = report["study"]
    categories, detectors = set(study["categories"]), set(study["detectors"])
    expected_cells = {(category, detector) for category in categories for detector in detectors}
    families = report["matched_analysis"]["families"]
    if len(families) != 8 or len({family["family_id"] for family in families}) != 8:
        raise ValueError("expected eight unique families")
    for family in families:
        baseline, endpoint = family["family_id"].split(":", 1)
        expected_definition, expected_parameters = THRESHOLDS[baseline]
        threshold = family["threshold"]
        if threshold["rule"] != baseline or threshold["definition"] != expected_definition or threshold["parameters"] != expected_parameters:
            raise ValueError("frozen threshold metadata mismatch")
        if family["endpoint"] != endpoint:
            raise ValueError("family endpoint mismatch")
        cells = family["cells"]
        if {(cell["category"], cell["detector"]) for cell in cells} != expected_cells:
            raise ValueError(f"incomplete family matrix: {family['family_id']}")
        for cell in cells:
            if not math.isclose(cell["target_normal_fpr"] - cell["source_normal_fpr"], cell["observed_matched_gap"], abs_tol=1e-12):
                raise ValueError("matched gap arithmetic mismatch")
            if cell["supports_positive_gap"] != (cell["lower_bound"] > 0) or cell["unsupported"] == cell["supports_positive_gap"]:
                raise ValueError("cell support flag mismatch")
        positive = [cell for cell in cells if cell["lower_bound"] > 0]
        positive_categories = sorted({cell["category"] for cell in positive})
        positive_detectors = sorted({cell["detector"] for cell in positive})
        gate = len(positive_categories) >= 2 and len(positive_detectors) >= 2
        if family["positive_cell_count"] != len(positive) or family["positive_categories"] != positive_categories or family["positive_detectors"] != positive_detectors or family["gate_passed"] != gate:
            raise ValueError("family gate summary mismatch")
    if report["matched_analysis"]["gate"]["passed"] != all(family["gate_passed"] for family in families):
        raise ValueError("joint gate mismatch")
    rankings = report["full_n_rankings"]["records"]
    expected_rankings = {
        (category, endpoint, rule, criterion)
        for category in categories
        for endpoint in ("image-score", "map-maximum-image-decision")
        for rule in ("empirical_p95", "split_conformal_05", "mvtec_mean_plus_3std", "superadd_p95_gain_1p4_calmin")
        for criterion in ("target-normal-fpr", "target-anomaly-recall")
    }
    if {(row["category"], row["endpoint"], row["threshold_rule"], row["criterion"]) for row in rankings} != expected_rankings:
        raise ValueError("incomplete full-n ranking matrix")
    for row in rankings:
        if set(row["auroc_order"]) != detectors or set(row["operating_point_order"]) != detectors:
            raise ValueError("ranking detector set mismatch")
    for artifact in report["artifacts"]:
        path = ROOT / artifact["path"]
        if not path.is_file() or sha256(path) != artifact["sha256"]:
            raise ValueError(f"artifact hash mismatch: {path}")
    return {
        "schema_version": report["schema_version"],
        "families": len(families),
        "matched_cells": sum(len(family["cells"]) for family in families),
        "ranking_records": len(rankings),
        "arithmetic_recomputed": True,
        "matrix_completeness_recomputed": True,
        "gate_recomputed": True,
        "artifact_hashes_verified": True,
        "schema_validated": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path, nargs="?", default=ROOT / "experiments/tables/operating_point_transport_report_v1.json")
    args = parser.parse_args()
    print(json.dumps(validate(json.loads(args.report.read_text(encoding="utf-8"))), indent=2))


if __name__ == "__main__":
    main()
