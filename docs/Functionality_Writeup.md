# Functionality & Technical Methodology Write-Up

## Overview
This document outlines the technical stack and data analytical methodologies employed in the "Great Reshuffling" project. The analysis was conducted entirely in **Python**, utilizing a modern data science stack to perform ETL (Extract, Transform, Load), econometric modeling, and visualization.

## 🛠️ Technical Stack & Skills Applied

### 1. Python Programming (Core Logic)
*   **Application:** Used as the primary language for all data engineering and analysis.
*   **Skills Demonstrated:**
    *   **Modular Architecture:** Organized code into a professional `src/` directory with separate modules for fetching (`fetch_migration_history.py`), analysis (`analysis_zoom_hierarchy.py`), and regression (`analysis_mechanism_regression.py`).
    *   **Reproducibility:** Designed scripts to be executable from the root directory, ensuring consistent paths and outputs.

### 2. Pandas (Advanced Data Manipulation)
*   **Application:** Handling large-scale housing and census datasets.
*   **Skills Demonstrated:**
    *   **ETL Pipelines:** Automated the ingestion of raw CSVs and JSON API responses.
    *   **Fuzzy Matching:** Implemented logic to map inconsistent city names (e.g., mapping Zillow's "Bend, OR" to the analysis cohort's "Bend-Redmond, OR").
    *   **Time-Series Normalization:** Applied a "Comparative Event Study" style normalization, indexing all housing price series to $t=0$ at March 2020 to isolate the post-pandemic shock.
    *   **Reshaping:** Used `pd.melt()` to transform wide-format Zillow data into long-format time series for analysis.
    *   **Merging:** Performed inner joins between distinct datasets (Migration vs. Housing) based on composite keys (`Year`, `City`).

### 3. APIs & Data Acquisition (Requests)
*   **Application:** Programmatically fetching data from the US Census Bureau.
*   **Skills Demonstrated:**
    *   **API Integration:** Used the `requests` library to query the US Census PEP (Population Estimates Program) API.
    *   **Pagination & Loops:** Constructed loops to fetch data across multiple vintage years (2011-2019) to build a complete historical panel.

### 4. Econometrics & Statistics (Statsmodels)
*   **Application:** Validating the "Golden Handcuffs" hypothesis.
*   **Skills Demonstrated:**
    *   **OLS Regression:** Utilized `statsmodels.api` to run an Ordinary Least Squares regression (`Price ~ Net_Migration_Rate`).
    *   **Hypothesis Testing:** Analyzed Beta coefficients, P-values, and R-squared statistics to confirm the negative correlation between pre-pandemic prices and migration.
    *   **Parallel Trends:** Conducted a "Placebo Test" on 2010-2019 data to validate the pre-shock stability of the comparative cohorts.

### 5. Data Visualization (Matplotlib)
*   **Application:** Creating publication-ready charts to communicate findings.
*   **Skills Demonstrated:**
    *   **Custom Plotting:** Generated multi-line time-series charts with custom styling.
    *   **Confidence Intervals:** Visualized intra-cohort variance using `plt.fill_between()` to show the min/max range of growth, not just the mean.
    *   **Dual-Axis Charts:** Created complex visualizations overlaying bar charts (Migration) with line charts (Prices) on shared X-axes.

### 6. Version Control (Git & GitHub)
*   **Application:** Project management and portfolio presentation.
*   **Skills Demonstrated:**
    *   **Repo Structure:** Organized project into standard `src/`, `data/`, `output/`, and `docs/` directories.
    *   **Documentation:** Wrote a comprehensive `README.md` with badges, project overview, and usage instructions.
