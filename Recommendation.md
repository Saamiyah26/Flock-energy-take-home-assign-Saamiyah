# 4. Practical implications

## A practical saving opportunity

One useful opportunity is to encourage households to move some appliance use away from the busiest evening hours. If the analysis shows that things like washing machines, dishwashers, tumble dryers, and kettles are often used in the early evening, then a company or energy provider could suggest cheaper off-peak times or send simple reminders to shift that usage. This is a realistic idea because it does not require changing the home or buying new equipment; it simply changes when the appliance is used.

To check whether this works, I would test it with a small group of households first. I would compare their evening electricity use before and after the suggestion or tariff change. If energy use in the evening falls, while total daily usage stays similar or drops, then the approach is working.

## Limitations

Several limitations should be considered before applying this approach in a real-world energy-monitoring system.

- Overlapping appliance signatures: Different household appliances can produce similar power-consumption patterns. For example, heating elements in washing machines, kettles, and other appliances may generate comparable power peaks. Since the model uses aggregate electricity readings, it may incorrectly attribute another appliance's consumption to the washing machine. This is reflected in the false-positive predictions observed during testing.

- Missing and irregular data: Missing timestamps, duplicate readings, and irregular sampling intervals can affect the quality of the input signal. Although timestamps were sorted and duplicates removed during preprocessing, gaps and extreme readings still required investigation. Missing intervals can reduce the reliability of model predictions, particularly when they occur within the input windows.

- Household differences: Appliance models, household size, user behaviour, washing frequency, and electrical consumption patterns vary between homes. A model trained on a limited number of households may not generalise reliably to households with different consumption characteristics. The experiment used four training households, one validation household, and one separate test household, so broader evaluation would be necessary.

- UK-to-India generalisation: REFIT contains electricity consumption data from UK households. Applying a model trained on this dataset to Indian households may be challenging because of differences in appliance models, rated power, voltage conditions, household structures, usage habits, and electricity consumption patterns. The model would therefore require validation and potentially retraining or fine-tuning using representative Indian household data before practical deployment.

## What if we only had 15-minute or 30-minute meter data?

If only 15-minute or 30-minute smart-meter readings were available instead of one-minute readings, appliance disaggregation would become considerably more difficult. Washing machines operate through different phases, such as water heating, washing, rinsing, and spinning, which produce changing power-consumption patterns. At a lower sampling resolution, short-duration power peaks and transitions may be averaged out or missed entirely. Multiple appliance activities occurring within the same interval would also become harder to distinguish. Consequently, the model would lose important temporal information, making it more difficult to identify individual washing-machine cycles, estimate their power consumption accurately, and separate their signatures from other household appliances. The analysis would likely need to rely more heavily on longer-term usage patterns rather than detailed appliance-level behaviour.
