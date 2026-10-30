# Washing Machine Energy Disaggregation Using a CNN-Based Seq2Point Model

## 1. Introduction

Non-Intrusive Load Monitoring (NILM) is the task of estimating the
energy consumption of individual appliances from a household's aggregate
electricity signal. Instead of installing a separate meter for every
appliance, NILM uses the total household power demand to infer the
contribution of a target appliance.

This work focuses on estimating washing-machine power consumption from
aggregate household power readings using the cleaned REFIT dataset. The
data were converted to a one-minute time resolution, and a
one-dimensional convolutional neural network (1D CNN) based on the
Sequence-to-Point (Seq2Point) approach was implemented.

The implementation is inspired by Zhang et al. (2018), who introduced
sequence-to-point learning for NILM. The model uses a fixed-length
aggregate-power window to predict the washing-machine power at the
centre of that window. The implementation is an adaptation inspired by
the paper, rather than an exact reproduction.

## 2. Dataset

### 2.1 REFIT dataset

The experiments use the official cleaned REFIT electrical load
measurements dataset. REFIT contains household-level electricity
measurements, including aggregate demand and appliance-level readings.

Twenty household CSV files were available in the prepared dataset. Six
households were selected for this experiment and divided by household:

  Split        Household IDs
  ------------ ---------------
  Training     3, 7, 8, 10
  Validation   13
  Testing      16

Using different households for training, validation, and testing helps
evaluate whether the model can generalise to a household that it did not
encounter during training.

The washing-machine appliance column was selected separately for each
household using the following mapping:

  Household     Washing-machine column
  ----------- ------------------------
  3                                  6
  7                                  5
  8                                  4
  10                                 5
  13                                 3
  16                                 5

### 2.2 Data preprocessing

The following preprocessing steps were applied:

1.  The household CSV files were loaded.
2.  Rows marked with `Issues != 0` were excluded; only rows with
    `Issues == 0` were retained.
3.  Timestamps were sorted chronologically.
4.  Aggregate and washing-machine readings were resampled to one-minute
    intervals using the mean.
5.  Windows containing missing aggregate or target readings were
    excluded rather than filling missing values with zero.

The aggregate signal was used as the model input, while the
washing-machine power reading was used as the target.

The evaluation data covered the period from **10 January 2014 to 8 July
2015**, based on the first and last timestamps in the final test set.
The exact date ranges for the training and validation sets should be
added from the preprocessing output if required; they are not stated
here because they were not available in the recorded experiment details.

## 3. Methodology

### 3.1 Sequence-to-Point formulation

The model follows a CNN-based Sequence-to-Point approach. It takes a
window of 121 consecutive one-minute aggregate-power readings and
predicts the washing-machine power at the centre of the window.

-   **Input window:** 121 minutes of aggregate household power.
-   **Prediction target:** Washing-machine power at the centre position
    (index 60).
-   **Window stride:** 5 minutes when generating training and evaluation
    windows.

Although the source data were resampled to one-minute intervals, a
five-minute stride was used when generating windows. Therefore,
predictions are generated at the selected stride rather than at every
possible minute.

Conceptually:

``` text
Aggregate power:
[x(t-60), ..., x(t-1), x(t), x(t+1), ..., x(t+60)]
                              |
                              v
                       1D CNN model
                              |
                              v
             Predicted washing-machine power at t
```

### 3.2 CNN architecture

A one-dimensional CNN was implemented to learn temporal patterns in the
aggregate signal that may indicate washing-machine activity.

The architecture consists of five convolutional layers followed by fully
connected layers:

  Layer               Configuration
  ------------------- ----------------------------
  Conv1D 1            30 filters, kernel size 10
  Conv1D 2            30 filters, kernel size 8
  Conv1D 3            40 filters, kernel size 6
  Conv1D 4            50 filters, kernel size 5
  Conv1D 5            50 filters, kernel size 5
  Fully connected 1   128 units
  Fully connected 2   64 units
  Output              1 unit, linear activation

Dropout with a rate of 0.2 was used to help reduce overfitting. The
final layer produces a single continuous power estimate.

### 3.3 Training configuration

  Parameter                 Setting
  ------------------------- -----------------------------------------
  Optimiser                 Adam
  Learning rate             0.001
  Loss function             Mean Absolute Error (MAE)
  Batch size                256
  Maximum epochs            50
  Early stopping patience   8 epochs
  Learning-rate scheduler   ReduceLROnPlateau
  Input normalisation       Aggregate power divided by 3000 W
  Target normalisation      Washing-machine power divided by 2000 W

Early stopping was used to stop training when validation performance
stopped improving, and the best-performing model weights were restored.
In the recorded run, the best validation loss was 0.00809 at epoch 15;
training stopped at epoch 23 and restored the best weights.

### 3.4 Handling appliance activity imbalance

Washing-machine activity is relatively infrequent compared with periods
when the appliance is off. This creates an imbalance between inactive
and active target readings.

In the training data, 240,000 samples were used:

  Target category     Number of samples   Percentage
  ----------------- ------------------- ------------
  Inactive                      227,076       94.61%
  Active                         12,924        5.39%

A threshold of 50 W was used to distinguish inactive from active
washing-machine readings for activity-related evaluation. Sample weights
were also applied during training so that active readings received
greater importance than inactive readings. Higher-power active readings
received additional emphasis. The recorded sample weights had a mean of
1, median of 0.703, and maximum of 8.436.

## 4. Evaluation

### 4.1 Evaluation setup

The final test evaluation used 123,862 observations from the held-out
test household (House 16). The same test observations were used to
evaluate the CNN and the two simple baselines.

A threshold of 50 W was used when calculating appliance activity
classification metrics. A prediction above this threshold was treated as
an active prediction.

### 4.2 Evaluation metrics

The following metrics were used:

-   **Mean Absolute Error (MAE):** The average absolute difference
    between actual and predicted power. Lower values indicate smaller
    average errors.
-   **Root Mean Squared Error (RMSE):** The square root of the average
    squared prediction error. It penalises large errors more strongly
    than MAE.
-   **Coefficient of determination (R²):** Measures how much of the
    variation in the target values is explained by the predictions. A
    negative value indicates performance worse than predicting the
    test-set mean under the standard R² definition.
-   **Precision:** The proportion of predicted active instances that
    were actually active.
-   **Recall:** The proportion of actual active instances that were
    correctly detected.
-   **F1-score:** The harmonic mean of precision and recall.
-   **Active MAE:** MAE calculated only on observations where actual
    washing-machine power exceeded 50 W.
-   **Signal Aggregate Error (SAE):** Measures the relative error in
    estimated total energy over the evaluation period. Values closer to
    zero indicate a closer match between estimated and actual aggregate
    appliance energy.

## 5. Results

### 5.1 Baseline comparison

The CNN was compared with two simple baselines:

1.  **Always OFF:** Predicts zero washing-machine power for every
    observation.
2.  **Hourly Profile:** Uses a typical washing-machine usage profile
    based on the time of day.

The results on the same test set are shown below.

  Metric             CNN Seq2Point   Always OFF   Hourly Profile
  ---------------- --------------- ------------ ----------------
  MAE (W)                    28.82        18.52            46.03
  RMSE (W)                  203.29       178.66           177.99
  R²                       -0.3088      -0.0109          -0.0033
  F1-score                  0.2704       0.0000           0.0864
  Precision                 0.1887       0.0000           0.0514
  Recall                    0.4769       0.0000           0.2705
  Active MAE (W)            524.50       764.76           723.95
  SAE                       0.2588       1.0000           0.6407

The CNN achieved a higher F1-score and recall than either baseline. It
also achieved a lower active MAE and SAE, indicating that it was more
useful than the baselines at detecting washing-machine activity and
estimating consumption during active periods.

However, the CNN did not achieve the lowest overall MAE or RMSE, and its
R² was negative. The Always OFF baseline achieved a lower overall MAE
because washing-machine readings were inactive for most of the test
observations. This illustrates why overall MAE alone is not sufficient
for evaluating appliance disaggregation on an imbalanced dataset.

The CNN should therefore not be described as the best model across all
metrics. Its results show improved activity detection compared with the
simple baselines, but substantial errors remain in its power estimates.

### 5.2 Activity detection results

For the final test set:

  Quantity                                     Count
  ---------------------------------------- ---------
  Total test observations                    123,862
  Actual active observations (\>50 W)          2,917
  Predicted active observations (\>50 W)       7,371
  True positives                               1,391
  False positives                              5,980
  False negatives                              1,526

The model detected 47.69% of actual active observations (recall), but
only 18.87% of its active predictions were correct (precision). This
indicates that the model detected some genuine washing-machine activity
but also produced many false activations.

## 6. Prediction Analysis and Failure Cases

The actual-versus-predicted plots should be included in this section.
The scatter plot can be used to show the relationship between actual and
predicted washing-machine power, while the time-series plot can show how
the model behaves over the evaluation period.

## 6. Prediction Analysis and Failure Cases

### 6.1 Actual vs Predicted Power

![Actual vs Predicted Washing Machine Power](actual-versus-predicted scatter plot.png)

**Figure 1.** Scatter plot comparing actual and predicted washing-machine power on the held-out test household.

### 6.2 Actual and Predicted Power Over Time

![Actual and Predicted Washing Machine Power Over Time](actual_vs_predicted_timeseries.png)

**Figure 2.** Comparison of actual and predicted washing-machine power over time on the test dataset.

Ensure that timestamps are displayed in chronological order and that missing time intervals are not joined in a way that suggests continuous observations.

The evaluation identified three main types of errors:

### 6.1 False appliance activation

The model sometimes predicted high washing-machine power when the actual
washing-machine reading was zero. Examples include:

  Timestamp            Actual power (W)   Predicted power (W)
  ------------------ ------------------ ---------------------
  2014-05-22 23:28                 0.00               2604.85
  2014-05-22 23:23                 0.00               2559.44
  2014-04-05 07:21                 0.00               2284.79

These cases suggest that aggregate-power patterns from other household
activities can sometimes resemble patterns learned by the model as
washing-machine activity.

### 6.2 Missed appliance activity

The model also failed to detect some genuine washing-machine activity,
including high-power readings:

  Timestamp            Actual power (W)   Predicted power (W)
  ------------------ ------------------ ---------------------
  2014-07-10 04:39              2139.70                  0.01
  2014-12-06 05:20              2131.33                  0.00
  2014-12-21 04:27              2114.00                  0.64

These examples show that the model can miss appliance activity even when
the actual power demand is high.

### 6.3 Large errors during active periods

There were also observations where the appliance was active but the
predicted power differed substantially from the actual value. Such
errors contribute to the relatively high active MAE and RMSE.

Overall, the test results indicate that the CNN learned some useful
patterns associated with washing-machine activity, but it struggled to
distinguish washing-machine consumption from other household loads and
to estimate power accurately during all operating states.

## 7. Limitations

The experiment has several limitations:

1.  **Limited household coverage:** The model was trained using four
    households, validated using one household, and tested using one
    separate household. Results may differ across a wider range of
    homes.
2.  **Class imbalance:** Washing-machine activity represented only 2.35%
    of the final test observations, making activity detection
    challenging.
3.  **False positives:** The model generated more active predictions
    than the number of actual active observations.
4.  **Missed high-power events:** Some high-power washing-machine
    readings were predicted as inactive.
5.  **Negative R²:** The negative test R² indicates that the model did
    not explain the variation in test power readings effectively under
    the standard R² comparison.
6.  **Window stride:** A five-minute stride reduces the number of
    generated windows but does not evaluate every possible one-minute
    centre point.

## 8. Conclusion

This work implemented a CNN-based Sequence-to-Point model to estimate
washing-machine power consumption from aggregate household electricity
readings using the cleaned REFIT dataset. The data were resampled to
one-minute intervals, and household-level separation was used for
training, validation, and testing.

Compared with the Always OFF and Hourly Profile baselines, the CNN
achieved better F1-score, precision, recall, active MAE, and SAE.
However, it did not outperform the baselines in overall MAE, RMSE, or
R². The low precision and negative R² indicate that the model still
produces many false activations and has difficulty accurately estimating
washing-machine power.

The results demonstrate the potential of a CNN-based Seq2Point approach
for detecting appliance activity, while also highlighting the challenges
caused by infrequent appliance usage and overlapping household power
patterns. Further work could investigate improved activity-aware
objectives, additional household training data, and methods for reducing
false positive predictions.

## 9. References

1.  Zhang, C., Zhong, M., Wang, Z., Goddard, N., & Sutton, C. (2018).
    *Sequence-to-Point Learning with Neural Networks for Non-Intrusive
    Load Monitoring*. Proceedings of the AAAI Conference on Artificial
    Intelligence. [Google
    Scholar](https://scholar.google.com/scholar?q=Sequence-to-Point+Learning+with+Neural+Networks+for+Non-Intrusive+Load+Monitoring)

2.  Murray, D., Stankovic, L., & Stankovic, V. (2017). *An electrical
    load measurements dataset of United Kingdom households from a
    two-year longitudinal study*. Scientific Data, 4, 160122.
    <https://doi.org/10.1038/sdata.2016.122>
