# House 1 REFIT Raw Data Quality Assessment

## Scope
This document summarises the raw data quality assessment for the four House 1 REFIT datasets used in the project:

- `data1_early`: 2013-10-09 to 2014-06-27
- `data2a_part1`: 2014-06-28 to 2014-10-01
- `data2b_part2`: 2014-06-28 to 2014-10-01
- `data3_late`: 2014-10-02 to 2015-07-10

The assessment was performed without modifying, deleting, interpolating, or combining the original readings. The goal was to identify quality issues and document the risks before cleaning or modelling.

---

## Executive Summary

The data are generally usable for raw time-series analysis, but they contain several recurring issues that must be handled carefully:

- Timestamps are valid and parse correctly.
- There are no invalid timestamps and no zero Unix values.
- Duplicate timestamps are common in the early Part 1 data and particularly in the overlap period between Data 2A and Data 2B.
- Missing values are frequent and channel-dependent, especially in specific appliance channels.
- Part 1 data mostly use zero to signal unavailable readings, while Part 2 data mostly use `NaN`.
- Some aggregate readings are inconsistent with the sum of monitored appliance loads, which is expected to some degree because only selected appliances are monitored.
- There are long irregular intervals and a small number of extreme high-power readings.
- No automatic correction or imputation was applied in this inspection step.

---

## Comparison Across All Four Datasets

| Metric | Data 1 | Data 2A | Data 2B | Data 3 |
|---|---:|---:|---:|---:|
| Total rows | 3,121,234 | 1,256,643 | 954,496 | 3,185,453 |
| Invalid timestamps | 0 | 0 | 0 | 0 |
| Out-of-order transitions | 1 | 1 | 0 | 0 |
| Exact duplicate rows | 608,023 | 512,896 | 0 | 0 |
| Repeated timestamps | 657,524 | 553,480 | 0 | 0 |
| Conflicting duplicate groups | 10 | 10 | 0 | 0 |
| Missing Aggregate readings | 0 | 0 | 55,418 | 133,490 |
| Missing appliance readings | 0 | 0 | 1,991,028 | 3,101,445 |
| Zero Aggregate readings | 12 | 0 | 0 | 0 |
| Intervals > 60s | 542 | 238 | 2,870 | 733 |
| Intervals > 5 min | 327 | 53 | 23 | 49 |
| Intervals > 1 hour | 6 | 8 | 6 | 13 |
| Intervals > 24 hours | 2 | 1 | 1 | 9 |
| Negative power readings | 0 | 0 | 0 | 0 |
| Aggregate readings > 10,000 W | 7,124 | 3,032 | 2,131 | 8,778 |
| Appliance readings > 5,000 W | 1,418 | 242 | 41 | 578 |
| Aggregate = 0 while appliance total > 0 | 12 | 0 | 0 | 0 |

---

## Detailed Findings by Dataset

### 1) Data 1 (`data1_early`)

- Time range: 2013-10-09 14:06:17 to 2014-06-27 23:59:50
- Rows: 3,121,234
- Timestamp status: valid and parseable
- Duplicate issue: very high. 608,023 rows were exact duplicates across all columns, and 657,524 rows belonged to repeated timestamps.
- Data quality concern: the dataset has a strong duplicate pattern, especially in Part 1, and a few rows where `Aggregate = 0` while appliances are active.
- Missingness: no missing values in any channel in this subset.
- Zero readings: many appliance channels contain a large number of zeros, which is consistent with the Part 1 convention for unavailable readings.
- Extremes: 7,124 aggregate readings exceeded 10,000 W, and 1,418 appliance readings exceeded 5,000 W.
- Interpretation: Data 1 is valid but noisy and highly duplicated; cleaning should treat duplicate timestamps and some zero-valued inactive periods carefully.

### 2) Data 2A (`data2a_part1`)

- Time range: 2014-06-28 00:00:04 to 2014-10-01 01:27:07
- Rows: 1,256,643
- Timestamp status: valid, but one out-of-order transition exists.
- Duplicate issue: large, with 512,896 exact duplicate rows and 553,480 repeated timestamp rows.
- Missingness: no missing values in any column.
- Zero readings: many appliance channels still contain zeros, which matches the Part 1 pattern.
- Long gaps: there are a few large intervals, including one interval longer than 24 hours.
- Extremes: 3,032 aggregate readings exceed 10,000 W; 242 appliance readings exceed 5,000 W.
- Interpretation: This is a dense Part 1 dataset with many repeated samples and a standard zero-based missingness pattern. It should not be treated as a clean regular time series without duplicate handling.

### 3) Data 2B (`data2b_part2`)

- Time range: 2014-06-28 00:00:05 to 2014-10-01 23:59:59
- Rows: 954,496
- Timestamp status: valid and in order.
- Duplicate issue: no exact duplicates and no repeated timestamps.
- Missingness: clear `NaN`-based missing values are present. Example counts:
  - Aggregate missing: 55,418
  - Appliance1 missing: 134,067
  - Appliance9 missing: 953,978 (almost all)
- Zero readings: nearly all of Appliance9 reads as zero, suggesting a sensor/channel issue or a mostly inactive / unavailable channel in this part.
- Long gaps: there are 2,870 intervals above 60 seconds, but most are still short and consistent with a normal sampling sequence.
- Extremes: 2,131 aggregate readings exceed 10,000 W; only 41 appliance readings exceed 5,000 W.
- Interpretation: Data 2B is much cleaner than the Part 1 overlapping period, but it has a different missing-data representation (`NaN` instead of zero), which must be preserved during cleaning.

### 4) Data 3 (`data3_late`)

- Time range: 2014-10-02 00:00:07 to 2015-07-10 11:56:32
- Rows: 3,185,453
- Timestamp status: valid and in order.
- Duplicate issue: no duplicates or repeated timestamps.
- Missingness: substantial. Missing readings are concentrated in specific channels, especially Appliance9.
  - Aggregate missing: 133,490
  - Appliance1 missing: 303,700
  - Appliance2 missing: 331,771
  - Appliance5 missing: 351,842
  - Appliance9 missing: 956,898
- Missing-value pattern: this subset is more irregular in missingness and more likely to contain sensor outages or sensor-specific blackout periods.
- Extremes: 8,778 aggregate readings exceed 10,000 W; 578 appliance readings exceed 5,000 W.
- Long gaps: 13 intervals exceed 1 hour and 9 exceed 24 hours.
- Interpretation: Data 3 is valid but contains meaningful missing periods and long power spikes. It should be handled with a conservative strategy that preserves real data but flags large outages.

---

## Timestamp and Unix Validation

The inspected datasets meet the expected timestamp validity checks:

- No invalid timestamp parsing errors were found.
- No `Time` column entries were missing.
- No `Unix` values were zero.
- No invalid Unix values were detected.
- The raw timestamps are chronologically valid overall, with only a small number of local ordering issues in Data 1 and Data 2A.

This suggests the raw timestamps are reliable enough to use as the primary indexing field, though duplicate timestamps and out-of-order local transitions need cleaning attention.

---

## Duplicate Record Analysis

### Exact duplicates
Exact duplicates across all columns were found in the Part 1 datasets:

- Data 1: 608,023 exact duplicate rows
- Data 2A: 512,896 exact duplicate rows
- Data 2B: 0
- Data 3: 0

### Repeated timestamps
Repeated timestamps were also found in the earlier part, which suggests the overlap region or duplicate sensor logging pattern is active there.

- Data 1: 657,524 repeated-timestamp rows
- Data 2A: 553,480 repeated-timestamp rows
- Data 2B: 0
- Data 3: 0

This is a strong signal that the Part 1 raw files have duplicated readings that must be treated explicitly. The repeated-timestamp problem is not just a simple row duplication issue; in some cases, the same timestamp appears more than once with different values.

---

## Missing Data Analysis

### Important raw-data note
The data do not use a single missing-value convention across all files:

- Part 1 tends to use zero when readings are unavailable.
- Part 2 tends to use `NaN` when readings are unavailable.

This distinction is important because a blanket conversion of zero to missing would distort the real data semantics.

### Missing-value pattern
- Data 1 and Data 2A show near-zero missing values in all channels and rely more on zero values.
- Data 2B and Data 3 show clear `NaN` gaps, especially in appliance channels and the aggregate channel.
- Some channels (for example Appliance 9 in Data 2B and Data 3) are missing at a very high rate and should be treated as potentially unreliable or sensor-specific.

---

## Aggregate and Appliance Consistency

The aggregate total should generally be greater than or equal to the sum of monitored appliance loads, but it does not necessarily equal it exactly because the monitored channels do not cover all household loads.

The assessment found:

- Data 1: 12 rows where `Aggregate = 0` while appliance total > 0
- Data 2A: 0 such rows
- Data 2B: 0 such rows
- Data 3: 0 such rows

This indicates that Data 1 contains a small number of inconsistent aggregate records that require inspection rather than automatic replacement.

In all datasets, `Aggregate` is often much larger than the monitored appliance sum, which is physically reasonable because many household loads are not included in the monitored appliance columns.

---

## Sampling Interval Analysis

The raw measurements are not perfectly regular. The data contain irregular gaps and occasional very large intervals.

Examples from the summary:

- Data 1: 327 intervals above 5 minutes; 6 above 1 hour; 2 above 24 hours
- Data 2A: 53 intervals above 5 minutes; 8 above 1 hour; 1 above 24 hours
- Data 2B: 23 intervals above 5 minutes; 6 above 1 hour; 1 above 24 hours
- Data 3: 49 intervals above 5 minutes; 13 above 1 hour; 9 above 24 hours

These are not necessarily errors, but they do represent genuine gaps or sampling irregularities that must be kept in mind during later cleaning and resampling.

---

## Extreme / Suspicious Power Values

The raw data include some very large readings, which are not automatically invalid but should be treated as suspicious until checked against the domain context.

Examples from the investigation thresholds:

- Aggregate > 10,000 W:
  - Data 1: 7,124
  - Data 2A: 3,032
  - Data 2B: 2,131
  - Data 3: 8,778
- Appliance > 5,000 W:
  - Data 1: 1,418
  - Data 2A: 242
  - Data 2B: 41
  - Data 3: 578

Several suspicious values such as `32,767`, `65,535`, and `98,301` were observed, and these are worth flagging for manual review rather than automatic deletion.

---

## Conclusion

The House 1 REFIT raw data are valid enough to proceed to cleaning, but they are not a simple “ready-to-use” dataset. The most important quality issues are:

1. Duplicate timestamps and exact duplicate rows in the early Part 1 data.
2. Different missing-value conventions between Part 1 and Part 2.
3. Gaps and irregular intervals in the raw sampled data.
4. Some inconsistent aggregate records and extreme readings.
5. Channel-specific sensor outage or inactivity patterns.

The correct next step is a conservative cleaning pipeline that:

- keeps the original rows untouched,
- handles duplicate timestamps explicitly,
- preserves the difference between zero and `NaN`,
- does not force aggregate values to appliance sums,
- flags long gaps and suspicious extremes without deleting them blindly,
- and only applies a limited, documented cleaning rule after inspection.

This inspection stage has successfully identified the main data-quality risks and produced a reproducible raw-assessment record for the next cleaning step.

---

## Output Files Produced

- `house1_data_quality_report.txt`
- `house1_comparison_summary.csv`
- `house1_quality_reports/`
- `house1_quality_plots/`
- `house1_suspicious_records.csv`
- `house1_long_gaps.csv`
