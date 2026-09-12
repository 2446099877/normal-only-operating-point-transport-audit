from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATCHED = ROOT / "experiments/tables/calibration_resampled_matched_v1.json"
MATCHED_COMPONENTS = ROOT / "experiments/tables/calibration_size_matched_v1.json"
RANKINGS = ROOT / "experiments/tables/operating_point_transport_rankings_v1.json"
PROTOCOL = ROOT / "experiments/CALIBRATION_RESAMPLED_PROTOCOL.md"
SCHEMA = ROOT / "experiments/OPERATING_POINT_TRANSPORT_REPORT_SCHEMA_V1.json"
OUTPUT = ROOT / "experiments/tables/operating_point_transport_report_v1.json"

ENDPOINT = {"image": "image-score", "pixel_image": "map-maximum-image-decision"}
CRITERION = {"target_normal_fpr": "target-normal-fpr", "target_anomaly_recall": "target-anomaly-recall"}
THRESHOLDS = {
    "empirical_p95": ("empirical 0.95 quantile", {"quantile": 0.95, "quantile_method": "higher"}),
    "split_conformal_05": ("finite-sample upper-tail split-conformal quantile", {"alpha": 0.05}),
    "mvtec_mean_plus_3std": ("population mean plus three population standard deviations", {"std_multiplier": 3.0, "ddof": 0}),
    "superadd_p95_gain_1p4_calmin": ("calibration minimum plus 1.4 times its distance to empirical P95", {"quantile": 0.95, "quantile_method": "higher", "gain": 1.4}),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    matched = json.loads(MATCHED.read_text(encoding="utf-8"))
    components = json.loads(MATCHED_COMPONENTS.read_text(encoding="utf-8"))
    rankings = json.loads(RANKINGS.read_text(encoding="utf-8"))
    component_cells = {
        (row["baseline"], row["endpoint"], cell["category"], cell["model"]): cell
        for row in components["analyses"]
        for cell in row["cells"]
    }
    families = []
    for analysis in matched["analyses"]:
        baseline, endpoint = analysis["baseline"], analysis["endpoint"]
        definition, parameters = THRESHOLDS[baseline]
        cells = []
        for cell in analysis["cells"]:
            source = component_cells[(baseline, endpoint, cell["category"], cell["model"])]
            cells.append({
                "category": cell["category"],
                "detector": cell["model"],
                "calibration_count": cell["calibration_images"],
                "target_normal_count": cell["target_normal_images"],
                "source_normal_fpr": source["matched_source_fpr"],
                "target_normal_fpr": source["matched_target_fpr"],
                "observed_matched_gap": cell["observed_matched_gap"],
                "bootstrap_standard_error": cell["bootstrap_standard_error"],
                "lower_bound": cell["simultaneous_lower_bound"],
                "unsupported": not cell["supports_positive_gap"],
                "supports_positive_gap": cell["supports_positive_gap"],
            })
        families.append({
            "family_id": f"{baseline}:{ENDPOINT[endpoint]}",
            "threshold": {"rule": baseline, "definition": definition, "parameters": parameters, "decision_operator": ">"},
            "endpoint": ENDPOINT[endpoint],
            "family_size": 24,
            "critical_value": analysis["max_t_critical_value"],
            "positive_cell_count": analysis["positive_lower_bound_cell_count"],
            "positive_categories": analysis["positive_lower_bound_categories"],
            "positive_detectors": analysis["positive_lower_bound_models"],
            "gate_passed": analysis["gate_passed"],
            "cells": cells,
        })
    ranking_records = [
        {
            "category": row["category"],
            "endpoint": ENDPOINT[row["endpoint"]],
            "threshold_rule": row["baseline"],
            "criterion": CRITERION[row["comparison"]],
            "auroc_order": row["quality_rank"],
            "operating_point_order": row["practical_rank"],
            "kendall_tau_b": row["kendall_tau_b"],
            "reversal_count": row["reversal_count"],
        }
        for row in rankings["transport"]["ranking_reversals"]
        if row["comparison"] in CRITERION
    ]
    return {
        "schema_version": "1.1.0",
        "study": {
            "dataset": "MVTec AD 2 public",
            "evidence_timing": "post-result-corrective",
            "categories": sorted({cell["category"] for family in families for cell in family["cells"]}),
            "detectors": ["patchcore", "padim", "efficient_ad"],
            "seeds": [17, 42, 73],
            "seed_aggregation": "mean; seeds are not independent images",
        },
        "matched_analysis": {
            "estimand_version": "loo-matched-v1",
            "estimand": "mean over validation deletions, fixed target normals, and seeds of I(target>t_-i)-I(source_i>t_-i)",
            "calibration_threshold": "n-1 leave-one-out threshold shared by source and target indicators",
            "target_normals_fixed": True,
            "confidence": 0.95,
            "bootstrap_replicates": 20_000,
            "bootstrap_seed": 20260813,
            "uncertainty_scope": "approximate calibration-sample inference conditional on fixed target-normal benchmark",
            "family_multiplicity": "24 cells controlled within each family; no control across eight families",
            "gate": {"minimum_categories": 2, "minimum_detectors": 2, "all_families_must_pass": True, "passed": matched["gate_passed"]},
            "families": families,
        },
        "full_n_rankings": {
            "threshold_calibration": "frozen full-n nominal validation threshold",
            "seed_aggregation": "mean across three seeds",
            "records": ranking_records,
        },
        "artifacts": [
            {"role": "schema", "path": str(SCHEMA.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(SCHEMA)},
            {"role": "matched-result", "path": str(MATCHED.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(MATCHED)},
            {"role": "matched-components", "path": str(MATCHED_COMPONENTS.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(MATCHED_COMPONENTS)},
            {"role": "full-n-rankings", "path": str(RANKINGS.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(RANKINGS)},
            {"role": "protocol", "path": str(PROTOCOL.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(PROTOCOL)},
        ],
    }


def main() -> None:
    OUTPUT.write_text(json.dumps(build(), indent=2) + "\n", encoding="utf-8")
    print(OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
