# VoltRelay network performance and rider retention

Corrected submission covering network trends, service experience, station patterns, batteries, pricing and cohort retention.

## Important execution status
The original repository contains retrospective exploratory outputs. Its predictive scores are not validated deployment results. The corrected pipeline has validation tests, but a full-data rerun is blocked: Google Drive returned quota-exceeded pages for five of the eight source files. Do not claim that the corrected notebook has been run on all 3.88 million events. No new numerical results are invented.

## Run
1. Download the eight original files from the link in `data/README.md`.
2. Put CSV or CSV.GZ files in `data/`.
3. Install `pip install -r requirements.txt`.
4. Run `jupyter notebook hackathon.ipynb` from this folder; run all cells in order.
5. Alternatively run `python analysis.py --data-dir data --output-dir results`.
6. Validate the critical logic with `python -m unittest discover -s tests -v`.

For Colab, upload the notebook and eight files, set DATA_DIR to their folder, and uncomment the dependency-install line. The analysis implementation is embedded in the notebook.

## What changed
- Removed machine-specific Downloads paths and supports compressed files.
- Added explicit key checks, timestamp correction, test-station exclusion, conservative retry filtering, invalid-reading rules and quality counts.
- Fixed queue aggregation weighting and missing-telemetry denominators.
- Distinguished energy-only contribution, site expenses and unmeasured battery wear; removed profitability and budget-affordability claims.
- Replaced target-overlapping churn features with equal-follow-up retention cohorts and pre-outcome experience windows.
- Corrected ticket-category rates to count riders once per category.
- Added supplier/lot/SOH comparisons, pricing segments and contract-amendment windows.
- Removed unsupported production-deployment, 100x benchmark and extrapolated future-revenue claims.

## Files and evidence
`hackathon.ipynb` and `analysis.py` are the corrected workflow. `EV_Battery_Swap_Analysis_Report_Corrected.docx` is the revised report; its original numerical outputs are explicitly marked provisional, pending rerun. `archive/original_hackathon.ipynb` preserves the original cached outputs. The original report and visuals are retained for traceability. The presentation script is an honest three-minute draft, not a recorded video.

## Remaining analytical limitations
The code provides descriptive comparisons, not causal estimates. Battery lifetime cycles are not supplied. Full wear-cost allocation, controlled pricing-pilot evaluation, adjusted battery swap-frequency comparisons and a prospective churn model are not completed. The supplied brief is an open analytics challenge; it does not require a classifier. Do not call this package a fully verified final-data analysis until the original files can be rerun.

## Source and attribution
Synthetic data generated for the Gradient Learnings Data Analytics Hackathon, seed 59500; company and partner names are fictional. Original project: https://github.com/himanshumittal1439/Rider-Churn-Prediction-and-Retention-Analysis . Dataset use remains subject to the organizer's hackathon terms.
