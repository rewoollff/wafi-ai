# Benchmarks

Measurements were taken locally during development.

## Test performance

| Measurement | Result |
|---|---:|
| Full pytest suite | 2.54 s |
| Pytest with coverage | 3.63 s |
| Core coverage | 96% |

## Docker image

| Measurement | Result |
|---|---:|
| Docker image size | 403.99 MB |
| Maximum required size | 500 MB |

## Test results

- 14 tests passed
- Coverage: 96%
- Ruff: passed
- Mypy: passed
- Import-linter: passed

## Behavioral check

The service was tested against the real trained model.

A full service outage is always classified as urgent.

Example request:
The entire department cannot access the system
Affected users: 50
Category: system

Expected decision:
Team: software
Urgency: urgent

## Fast gate

The coverage test suite completed in approximately 3.63 seconds, below the required 60-second limit.