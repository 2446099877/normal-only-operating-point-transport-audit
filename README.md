# Normal-only Operating-Point Transport Audit — reproducibility release

This repository contains the frozen protocol, derived report, independent
validator, report builder, and regression tests for the Pattern Recognition
Letters benchmark/protocol note.

## Reproduction

From the repository root:

```powershell
python -m pip install -r requirements.txt
python scripts/validate_operating_point_transport_report.py
python -m pytest -q tests/test_operating_point_transport_report.py
```

The validator must report 8 families, 192 matched cells, and 128 ranking
records. The current locked result is post-result-corrective and does not
constitute private-test confirmation.

## Contents

- `experiments/OPERATING_POINT_TRANSPORT_REPORT_SCHEMA_V1.json`
- `experiments/tables/calibration_resampled_matched_v1.json`
- `experiments/tables/calibration_size_matched_v1.json`
- `experiments/tables/operating_point_transport_rankings_v1.json`
- `experiments/tables/operating_point_transport_report_v1.json`
- `experiments/CALIBRATION_RESAMPLED_PROTOCOL.md`
- `scripts/build_operating_point_transport_report.py`
- `scripts/validate_operating_point_transport_report.py`
- `tests/test_operating_point_transport_report.py`

Underlying benchmark datasets are not redistributed. The release contains
derived aggregate audit artifacts only.

## Release metadata

- Prepared: 2026-09-12
- Manuscript result artifact SHA-256: `fac072f9b97c4454dfc5d36b582291ac6db0d770cf52e9ee246e0aff61fa1be2`
- Report SHA-256: `40558585a5ae36e800b172012d15c1635eae284e7b83247c81354d4606fccb18`
- Public DOI: **to be assigned by the repository host**
