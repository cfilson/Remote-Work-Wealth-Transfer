# Prompt for Generating the Research Paper

**Instructions:** Copy and paste the text below into Gemini (or another advanced LLM) to generate a high-quality first draft of your research paper.

---

**System Role:** You are a senior academic economist at the NBER. You specialize in urban economics and housing markets. Your writing style is empirical, precise, and formal.

**Task:** Write a comprehensive research paper based on the following project details. The paper should be suitable for submission to a pre-doctoral research program.

**Title:** The Great Reshuffling: Quantifying the Inflationary Externality of Remote Work on US Housing Markets

## 1. Abstract
Write a 200-word abstract summarizing:
*   **The Shock:** The sudden decoupling of employment from location in March 2020.
*   **The Methodology:** A Difference-in-Differences (DiD) framework analyzing Zillow (ZHVI) data across three city cohorts.
*   **The Findings:** "Nature Enclaves" (e.g., Bozeman, MT) experienced 53.5% inflation, significantly outpacing "Sunbelt Hubs" (45.7%) and "Wealth Exporters" (35.6%).
*   **The Mechanism:** Validated via Census migration data (2011-2019) showing that high-income workers were "trapped" in coastal cities by job requirements ("Golden Handcuffs") until the pandemic broke the link.

## 2. Introduction
*   Contextualize the "Zoom Shock" as a structural break in the bid-rent curve.
*   State the core hypothesis: Remote work acted as a wealth transfer mechanism, exporting inflation from inelastic coastal markets to inelastic scenic markets.
*   Preview the results: The "Lifestyle Premium" is quantifiable and persistent.

## 3. Data & Methodology
*   **Data Sources:**
    *   **Housing:** Zillow Home Value Index (ZHVI), smoothed, seasonally adjusted.
    *   **Migration:** US Census Bureau Population Estimates Program (PEP), Vintage 2019.
*   **Cohorts:**
    *   *Cohort A (Wealth Exporters):* SF, NY, Boston, etc. (The control group for "origin").
    *   *Cohort B (Sunbelt Hubs):* Austin, Miami, Phoenix (The traditional destination).
    *   *Cohort C (Nature Enclaves):* Bozeman, Bend, Asheville (The remote-work destination).
*   **Econometric Strategy:**
    *   Event Study / Difference-in-Differences.
    *   Normalization: All price series indexed to $t=0$ at March 2020.
    *   Parallel Trends Assumption: Validated using a placebo test on 2010-2019 data (confirming cohorts moved in unison prior to the shock).

## 4. Empirical Results
*   **Result 1: The Divergence.** Post-2020, Cohort C (Nature) separated from the pack, showing that amenities became a primary driver of price appreciation over pure agglomeration benefits.
*   **Result 2: The Mechanism (Golden Handcuffs).** Present the regression finding: A statistically significant negative correlation (Beta = -4405) between pre-pandemic net migration and housing prices in Wealth Exporters.
    *   *Interpretation:* People were leaving these cities (negative migration) even as prices rose, proving they were constrained by job location. Remote work removed this constraint.

## 5. Conclusion
*   Summarize the implications: The "Zoom Town" phenomenon is not transient; it represents a permanent re-pricing of lifestyle amenities.
*   Policy Implication: Small, scenic towns face an affordability crisis driven by external capital shocks they cannot supply-side respond to quickly enough.

---

**Formatting Requirements:**
*   Use academic headers (I. Introduction, II. Data, etc.).
*   Cite "Gupta et al. (2022)" regarding the "Flattening of the Bid-Rent Curve" as related literature.
*   Keep the tone objective and data-driven.
