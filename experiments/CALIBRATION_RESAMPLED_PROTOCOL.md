# Calibration-Resampled Matched Transport Sensitivity

Status: **frozen on 2026-08-13 before this analysis was implemented or run**

This post-result sensitivity addresses a methods-review objection to the first
calibration-size-matched audit. Resampling indices from a fixed leave-one-out
deletion table does not represent uncertainty from drawing a new nominal
calibration sample. This analysis therefore resamples the original calibration
images and recomputes every leave-one-out threshold inside each bootstrap
replicate. It reuses frozen detector scores and maps; no detector is retrained
and no score, category, detector, seed, rule, or endpoint is changed.

## Estimand and resampling unit

For each category, draw `n` calibration-image indices with replacement from the
observed `n` nominal validation images. The same indices are reused across all
detectors and seeds in that category. Within the resampled calibration set,
delete each position in turn, recompute the frozen threshold `t*_-i` from the
remaining `n-1` scores, and calculate

`mean_i[ mean_j 1(target_j > t*_-i) - 1(source*_i > t*_-i) ]`.

The target-normal benchmark images are held fixed. Thus the analysis represents
calibration-sample uncertainty conditional on the observed MVTec AD 2 public
target-normal set, detector outputs, categories, and seeds. It does not provide
target-population inference, a deployment guarantee for the full-`n` threshold,
or a causal acquisition-shift estimate.

## Frozen computation

- Four unchanged threshold rules and two unchanged image-decision endpoints.
- Three seeds are averaged and are not treated as independent images.
- `20,000` bootstrap replicates with PRNG seed `20260813`.
- One-sided approximate 95% max-`t` lower confidence bounds over the 24
  category--detector cells within each fixed threshold--endpoint family.
- The eight families are analyzed separately; there is no study-wide 95%
  guarantee across all eight families.
- Zero-variance cells fail closed at a non-positive lower bound.

## Frozen sensitivity gate

Each separately analyzed family passes only if positive calibration-resampled
lower bounds occur in at least two categories and at least two detector
identities. This deterministic gate does not convert a post-result correction
into confirmatory or preregistered evidence.

If any family fails, nominal-95% language and the positive transport headline
must be removed; only descriptive matched gaps and the calibration-fragility
boundary may remain. If all families pass, the manuscript may report the result
only as approximate calibration-resampled, within-family evidence conditional
on the fixed target-normal benchmark set.

No parameter or gate may be changed after results are read.
