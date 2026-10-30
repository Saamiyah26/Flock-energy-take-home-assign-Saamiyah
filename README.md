# Flock Energy Take-Home Assignment

This repository contains the work completed for the Flock Energy take-home assignment. It is designed to help someone quickly understand what was done, where the important files are, and how to move through the project from raw data inspection to reporting.

## How to navigate this project

If you are opening this repository for the first time, this is the best order to read it:

1. Start with `Data.md`  
   This file explains the raw-house data issues, quality checks, and the conservative cleaning decisions.

2. Open `assignment1.ipynb` and `data_cleaning.ipynb`  
   These notebooks contain the actual data inspection and cleaning workflow. They show how the data were split, sorted, cleaned, and visualized.

3. Review the figures in `cleaning_results/`  
   These plots show the before-and-after effect of the cleaning rules on real House 1 data.

4. Read the reports in `RESULTS/`  
   These files summarize the findings for the assignment and present the results in a more polished form.

5. Read `Recommendation.md`  
   This file contains the final practical implications and contextual discussion.

## What this project is about

The task focuses on the REFIT House 1 electricity dataset. The work was centered on understanding the quality of the raw smart-meter data and preparing it for reliable analysis.

The core questions were:

- Are the timestamps valid and in the correct order?
- Are there duplicate records or repeated timestamps?
- Are missing values represented consistently?
- Are there long gaps or irregular intervals?
- Are there suspicious high-power readings?
- How should the data be cleaned without losing important information?

## Main folders and files

### `Source Code/`
This folder contains the main analysis scripts and notebooks related to the project, including:

- `house1_raw_quality_assessment.py` — assessment script for checking the quality of the raw data
- `data_cleaning.ipynb` — notebook for the defined cleaning workflow
- `washing-machine-disaggregation.ipynb` — notebook focused on appliance-level analysis
- `washingmachineEDA.ipynb` — exploratory analysis of washing-machine-related patterns
- `generate_washingmachine_plots.py` — script to generate the washing-machine plots

### `RESULTS/`
This folder contains the polished written outputs and summaries of the analysis:

- `house1_data_quality_assessment.md` — raw-data quality summary
- `Washing_Machine_EDA_Results.md` — results from the washing-machine analysis
- `refit_washing_machine_nilm_report.md` — report-style summary of the appliance analysis

### `cleaning_results/`
This folder contains the before-and-after plots showing the effect of the cleaning rules on the House 1 data.

### `Detailed Work/`
This folder contains supporting material and intermediate project notes.

### `Images/`
This folder stores images used in the analysis or documentation.

### `Data.md`
This is the main summary of the raw dataset quality issues, cleaning strategy, and findings. It is one of the best files to read first if you want the project context quickly.

### `Recommendation.md`
This file explains the practical implications of the analysis, including realistic energy-saving opportunities and the limitations of the study.

## What was done

The project followed a conservative data-cleaning strategy:

- timestamps were checked and ordered,
- duplicate timestamps were identified and removed using a clear rule,
- missing values were examined with care,
- long gaps were flagged instead of being filled arbitrarily,
- suspicious high readings were documented,
- noisy sections were cleaned only when justified,
- before-and-after plots were generated to show the effect of the rule changes.

This was done intentionally to avoid forcing assumptions onto the raw data.

## Recommended reading path

If you want a fast understanding of the project, use this order:

1. `Data.md`
2. `assignment1.ipynb`
3. `data_cleaning.ipynb`
4. `cleaning_results/`
5. `RESULTS/house1_data_quality_assessment.md`
6. `Recommendation.md`

## Final note

This project is not just a dataset cleaning exercise. It is a structured workflow showing how a data scientist should inspect real-world energy data carefully, document assumptions, and present findings in a way that is understandable and defensible.
