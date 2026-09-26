# Validation and remaining work

## Completed before the midnight deadline
- Eight unittest checks passed: city normalization, zero denominators, weighted queue means, missing queue values, equal retention follow-up, unique-rider ticket denominators, idle-station costs, missing files and HTML-download rejection (some checks share a test).
- Every code cell in the replacement notebook passed Python syntax parsing.
- Corrected Word report exported successfully with installed Microsoft Word; its 13-page layout was reviewed.
- Six report tables and all fourteen original chart placements retained. Original Word reports and the original notebook with cached outputs are preserved under archive/.

## Not verified or completed
- Full 3.88M-row execution is blocked by Google Drive quota errors for swap events, telemetry, riders, batteries and support tickets. Station, city-context and fleet tables were downloadable, but are insufficient for the complete analysis.
- The eight tests validate selected critical calculations, not the entire pipeline at production scale. Runtime, memory requirements and the full notebook's top-to-bottom execution on the original data remain unverified.
- No prospective churn classifier, calibrated probabilities, causal pricing estimate or completed battery-wear allocation is delivered.
- No new model accuracy, updated failure rate or future revenue-at-risk estimate is asserted.
- No GitHub commit, push or pull request was made. This is a local replacement package ready for upload.
- No video was recorded; a presentation script is included.

## Original notebook issues corrected or explicitly qualified
Cell numbers below are zero-based indices in archive/original_hackathon.ipynb.

| Original location | Issue | Resolution |
|---|---|---|
| Cells 4–8 and others | Hard-coded Windows Downloads paths | Configurable data directory; CSV/GZ support |
| Cell 8 | Unweighted averaging of chunk queue means | Observation-level sum/count |
| Cell 46 | Eligibility duplicates churn condition and is unused | Equal signup follow-up and separate activation/return |
| Cells 48, 59, 63, 65–68 | Features overlap the outcome period | Pre-outcome descriptive cohort measures; old scores withdrawn from deployment use |
| Cell 61 | Ticket rows counted as churned riders | Unique rider/category observations |
| Cells 6 and 41–42 | Energy-only margin presented as broad economics | Explicit energy-only label and separate site costs |
| Cells 73–74 versus report | Gradient Boosting scores described as Random Forest deployment | Attribution corrected; no monthly deployment claim |
| README and new report | Unsupported 100x benchmark | Claim withdrawn pending reproducible benchmark |
| New report | Historical flagged revenue extrapolated to future network loss | Extrapolation explicitly rejected |

Source: organizer brief supplied by the user and public repository at https://github.com/himanshumittal1439/Rider-Churn-Prediction-and-Retention-Analysis .
