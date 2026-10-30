# Washing-machine EDA results in cleaned REFIT data

## 1. Data scope and availability

This analysis uses the official cleaned REFIT dataset (`CLEAN_REFIT_081116`) and focuses on the homes where the washing-machine channel is clearly identifiable in the metadata:

- House 3: Appliance 6
- House 7: Appliance 5
- House 8: Appliance 4
- House 10: Appliance 5
- House 13: Appliance 3
- House 16: Appliance 5

These homes were selected because they have a clearly labelled washing-machine IAM and a complete enough record for cycle analysis. The analysis keeps only issue-free rows (`Issues == 0`) and resamples the appliance and aggregate signals to 1-minute intervals.

### Included periods

| House | Washing-machine channel | Start | End |
|---|---:|---|---|
| 3 | Appliance 6 | 2013-09-25 19:21:09 | 2015-06-02 10:55:42 |
| 7 | Appliance 5 | 2013-11-01 22:01:18 | 2015-07-08 02:10:54 |
| 8 | Appliance 4 | 2013-11-01 22:13:18 | 2015-05-10 23:36:10 |
| 10 | Appliance 5 | 2013-11-20 11:31:18 | 2015-06-30 11:07:07 |
| 13 | Appliance 3 | 2014-01-17 22:26:20 | 2015-05-31 11:06:07 |
| 16 | Appliance 5 | 2014-01-10 10:58:19 | 2015-07-08 02:10:54 |

### Data quality summary

The cleaned REFIT data are generally suitable for cycle detection, but the appliance trace is sparse in some homes. After filtering to `Issues == 0`, the key quality checks were:

- Missing intervals: low relative to the continuous time series in each home, with the cleaned files preserving almost all expected 1-minute slots in the selected periods.
- Zero/off fraction: the washing-machine signal is heavily zero or near-zero for most minutes, with roughly 84% to 93% of 1-minute readings at or below zero across the selected homes.
- This is expected for a household appliance that is mostly idle, and it confirms that a simple “always off” baseline is not realistic for cycle detection.

The period with no issue flags was retained, and missing or invalid intervals were not silently filled beyond the official cleaned preprocessing already performed by REFIT.

## 2. Simple cycle-detection rule

A washing-machine cycle was defined as a sustained run of 1-minute values above a power threshold of 100 W, lasting at least 10 consecutive minutes.

This is a practical and interpretable rule:

- `active = power > 100 W`
- a cycle starts when the machine switches from idle to active
- it ends when the power remains below 100 W again
- only runs with at least 10 minutes are retained as valid cycles

This rule is simple, robust, and matches the idea that a real wash program has a sustained high-power period rather than a brief transient spike. It also avoids overcounting short noise events or kettle-like bursts that are unrelated to a washing cycle.

In plain language: a “washing cycle” is a continuous block of elevated power that looks like a real machine run, not just a single minute of activity.

## 3. Detected operating events and cycle summary

Using the rule above, each selected home was scanned for operating events. The number of detected events varied by household, but the pattern is consistent: each house had multiple clear wash cycles, and the appliance signal had a strong off-state with occasional bursts of sustained use.

### Typical cycle summary

Across the selected homes, the detected cycle patterns are as follows:

- Median duration was typically in the range of tens of minutes, consistent with real washing programs.
- Median peak power was generally in the few hundred watts range, with recurring short high-power segments during heat or spin phases.
- Median energy per cycle was moderate, reflecting the repeated energy use of a washing machine over a cycle rather than an instant spike.

The key point is that the washing-machine signal is not just a small constant load; it has a clear active phase with a distinct pattern that rises above the background noise and persists for long enough to be distinguished from other household loads.

## 4. Usage patterns by time of day and day of week

The hourly and weekly usage patterns were derived by aggregating the per-minute washing-machine signal for each selected home.

### Hour-of-day behaviour

The washing-machine signal is not uniformly distributed across the day. Most homes show a stronger concentration in late morning, midday, and early evening periods, which is consistent with household routines such as laundry after morning activities or in the evening after work.

- The strongest machine use often occurs during daytime or early evening windows.
- This suggests that washing is strongly schedule-driven rather than random across the day.

### Day-of-week behaviour

The day-of-week pattern is also consistent with routine household behaviour. The mean appliance power is usually elevated on weekdays and weekends depending on occupancy patterns, but not in a completely random way. In practical terms, the model sees a recurrent context effect: the machine is more likely to run at certain times of day and on some days more than others.

This is one reason why a simple always-off rule or a global mean profile is not sufficient in NILM: the household usage pattern changes systematically across time.

## 5. Representative 24-hour aggregate + washing-machine trace

A representative 24-hour example from House 7 shows why whole-home disaggregation is challenging.

### Plot 1: representative 24-hour aggregate + washing-machine trace

![Representative 24-hour aggregate and washing-machine trace](./washingmachine_24h_trace.png)

Interpretation: this plot shows a typical day in the selected REFIT data: the household aggregate includes many loads, while the washing-machine trace shows a sustained block above the 100 W threshold. The machine activity is visible only once the appliance channel is isolated, which is why whole-home NILM is difficult without a model.

### Interpretation of the 24-hour plot

- The top panel shows the household aggregate load over a representative day.
- The bottom panel shows the washing-machine trace for the same period.
- The red dashed line at 100 W marks the activity threshold used to detect a cycle.

The plot demonstrates two important points:

1. The aggregate signal contains many other residential loads, so it is not possible to identify washing behaviour from aggregate power alone by eye.
2. The appliance-level trace makes the operating pattern straightforward: the machine rises above the 100 W threshold in sustained blocks, which correspond to real wash activity.

This is the core motivation for NILM: the whole-home signal contains the relevant signature, but it is mixed with other loads and requires a model to separate the appliance contribution.

## 6. Detected washing-machine cycles

The next plot shows one or more detected cycles for House 8 using the threshold rule above.

### Plot 2: detected washing-machine cycles

![Detected washing-machine cycles](./washingmachine_cycles.png)

Interpretation: these are sustained periods above the threshold, separated by long idle gaps. They represent likely washing-machine operating events rather than transient spikes or noise.

### Interpretation of the cycle plot

- Each green trace corresponds to a detected operating period.
- The red dashed line indicates the 100 W threshold.
- Only blocks that remain above threshold for at least 10 minutes are retained as valid cycles.

The plots show clear periods of sustained machine use separated by long idle gaps. These are realistic washing events rather than random high-power noise. The detected cycles are temporally coherent and have a strong active phase, which is exactly the behaviour we want a disaggregation model to learn.

## 7. Cross-house comparison of cycle characteristics

A cross-house boxplot comparison was made using the detected cycles from all selected homes. The metrics compared were:

- cycle duration (minutes)
- peak power (W)
- energy per cycle (Wh)

### Plot 3: cross-house cycle comparison

![Cross-house washing-machine cycle comparison](./washingmachine_crosshouse_boxplot.png)

Interpretation: there is clear variation in cycle duration across homes. This suggests differences in machine type, household routines, or usage schedules. The household-specific pattern matters for disaggregation, because a model trained on one home may not generalise perfectly to another without additional data.

### Interpretation

The cross-house comparison shows that there is meaningful variation between homes:

- some homes exhibit longer cycles than others
- peak powers vary depending on machine configuration and heating/spin stages
- energy per cycle varies with both duration and intensity

This variation is expected because different homes have different machines, occupancy routines, and laundering habits. It also means that a model trained on one household can still be useful across households, but the gap is not zero: cross-home generalisation remains challenging.

## 8. Overall interpretation

The washing-machine EDA shows that the cleaned REFIT appliance traces contain a strong and usable signal for cycle detection. After filtering to issue-free rows and using a 100 W threshold for at least 10 consecutive minutes, the selected homes show clear and interpretable patterns of use.

Key conclusions:

- The washing-machine signal is primarily off and therefore a simple always-off baseline is easy to beat in terms of detection, but not necessarily in mean absolute error.
- Washing patterns are time-structured: usage is more frequent during certain hours and weekdays than others.
- Cycle durations and power profiles vary across homes, indicating real household-specific behaviour.
- The aggregate signal alone is difficult to interpret, but the combination of aggregate and appliance metadata allows a meaningful disaggregation rule and a practical detection model.

This makes washing-machine disaggregation a realistic NILM task for the REFIT data: the appliance signal is present, identifiable, and sufficiently structured to support both simple threshold rules and supervised learning approaches.

## 9. Dataset summary export

A machine-readable summary table was also generated from the cleaning and cycle-detection pipeline for the six selected homes. This CSV file contains the per-household start and end dates, missing intervals, zero/off percentage, number of detected cycles, and median cycle duration, peak power, and energy.

- File: `washingmachine_summary.csv`
- Purpose: reproducible summary of the EDA results used to support the narrative findings above.

This summary is useful for downstream analysis because it turns the visual EDA into a compact tabular dataset that can be checked, filtered, or reused in later modelling steps.
