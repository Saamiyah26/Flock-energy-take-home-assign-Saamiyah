# Raw Data Coverage and Quality Findings

## 1. Dataset coverage

The House 1 REFIT raw data were split into four time-based datasets for analysis:

- `data1_early`: 2013-10-09 to 2014-06-27
- `data2a_part1`: 2014-06-28 to 2014-10-01
- `data2b_part2`: 2014-06-28 to 2014-10-01
- `data3_late`: 2014-10-02 to 2015-07-10

The datasets represent the same household but come from different raw files and different parts of the measurement period. The split was necessary because the Part 1 and Part 2 raw files overlap in time and use different missingness conventions.

## 2. Raw-data quality overview

Overall, the measurements are usable, but they are not perfectly clean raw sensor data. The main issues are:

- duplicate timestamps in the early Part 1 data,
- different missing-value conventions between Part 1 and Part 2,
- irregular sampling intervals and occasional long gaps,
- a number of extreme or suspicious high-power readings,
- inconsistent aggregate values in a small number of rows.

The raw data were inspected without altering the original values. The goal was to understand the data quality before applying cleaning decisions.

## 3. Coverage and timestamp quality

### Timestamp validity
- All four datasets parsed correctly as datetime values.
- No invalid timestamps were found.
- No missing `Time` values were found.
- No `Unix = 0` values were found.
- No invalid Unix timestamps were detected.

### Time ordering
- Most datasets were chronologically ordered after sorting.
- A small number of out-of-order transitions were detected in Data 1 and Data 2A.
- These are not necessarily serious, but they confirm that the raw files are not perfectly ordered in the original row sequence.

## 4. Duplicate and repeated timestamps

### Exact duplicates
The Part 1 datasets contain a large number of exact duplicate rows across all columns:

- Data 1: 608,023 exact duplicate rows
- Data 2A: 512,896 exact duplicate rows
- Data 2B: 0
- Data 3: 0

### Repeated timestamps
The same timestamp also appears multiple times in the earlier part of the recording:

- Data 1: 657,524 repeated-timestamp rows
- Data 2A: 553,480 repeated-timestamp rows
- Data 2B: 0
- Data 3: 0

This is a strong sign that the raw Part 1 files contain repeated records or overlap duplicates that must be handled explicitly. The repeated timestamps are not just harmless duplicates; in some cases, the same timestamp occurs with different values.

## 5. Missing-data findings

### Missing-value convention difference
The datasets do not use one consistent representation for unavailable readings:

- Part 1 data mostly mark missing sensor values as zero.
- Part 2 data mostly use `NaN`.

This distinction matters. Converting all zeros to missing would distort the raw data semantics and remove valid information.

### Missingness by dataset
- Data 1 and Data 2A: very low missingness, but many zero readings in appliance channels.
- Data 2B and Data 3: much more `NaN`-based missingness, especially in individual appliance columns.
- The most affected channels include Appliance 9 in Data 2B and Data 3, which has a very large missing fraction.

This means that missingness is channel-specific and not uniform across the whole dataset.

## 6. Aggregate vs appliance consistency

The aggregate load is expected to be larger than or equal to the monitored appliance loads, but it does not necessarily equal the sum of the appliance channels. The monitored appliances are only a subset of the full household consumption.

The investigation found:

- Data 1: 12 rows where `Aggregate = 0` but appliance total > 0
- Data 2A: 0 such rows
- Data 2B: 0 such rows
- Data 3: 0 such rows

These inconsistent rows should be flagged, not silently replaced, because they may indicate real sensor anomalies or a data-logging issue.

## 7. Irregular sampling and missing periods

The data are not evenly sampled in time. There are many short irregular gaps and some large gaps. The interval analysis showed:

- Data 1: intervals above 5 minutes, 1 hour, and 24 hours are present
- Data 2A: similar but smaller irregularities
- Data 2B: some long gaps are still present despite the overall regular pattern
- Data 3: longer outages and bigger gaps are present than in earlier subsets

These gaps should be treated as genuine missing periods, not something to fill automatically without justification.

## 8. Outliers and extreme values

High readings were found in all datasets. The threshold checks showed:

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

Some suspicious repeated values were also identified, including values like `32,767`, `65,535`, and `98,301`. These should be treated as suspicious but not automatically invalid, because they may be legitimate sensor values or clipped readings.

## 9. Cleaning decisions taken

The cleaning strategy is intentionally conservative and inspection-based.

### Sorting
All datasets were sorted by `Time` before any cleaning logic was applied.

### Duplicate removal
The cleaning rule used was:

- sort by `Time`
- remove duplicate timestamps using `drop_duplicates(subset='Time', keep='first')`

This keeps the earliest reading and discards later duplicates. It is a transparent rule and does not require guessing missing values.

### Missing gaps
Short missing runs were flagged and recorded rather than filled automatically.

Longer outages were also flagged instead of being filled without justification.

This is important because the raw dataset contains non-trivial gaps and missing periods, and blanket imputation could hide actual sensor interruptions.

### Outliers and suspicious values
High readings were not deleted automatically. They were flagged for review because the data source is real-world smart-meter data and such spikes may be legitimate load events or sensor artifacts.

### Aggregate values
The aggregate channel was not replaced with the sum of appliance loads. That would be an unjustified assumption. The aggregate reading is treated as its own measurement, while appliance totals are used for consistency checks only.

## 10. Remaining concerns

The main concerns that remain after inspection are:

1. Duplicate timestamps in Data 1 and Data 2A.
2. Mixed missingness conventions between Part 1 and Part 2.
3. Long outages and irregular gaps in some channels.
4. Suspicious high-power readings that require domain checks.
5. A few aggregate inconsistencies in the early dataset.

These are manageable, but they should be handled with careful, documented rules rather than a blanket cleaning approach.

## 11. Final interpretation

The House 1 raw data are suitable for further cleaning and modelling if the cleaning is done conservatively. The most important step is to preserve raw structure, remove clear duplicates, flag gaps and suspicious values, and avoid forcing assumptions that are not supported by the measurement system.

The data are not “bad,” but they are definitely not a perfectly clean time series. They require a transparent and minimally invasive cleaning strategy.
