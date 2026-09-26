# Three-minute presentation draft

VoltRelay operates an electric two- and three-wheeler battery-swap network across six Indian cities. The business question is how to improve reliability and retention while understanding the economics of growth. Our source is the hackathon's synthetic dataset covering January 2024 through June 2025.

We reviewed the existing analysis and connected its claims to the calculations behind them. The original notebook reports about 3.88 million attempts and a 3.47 percent no-battery failure rate. Jaipur and Delhi NCR stand out in the historical reliability analysis, with Jaipur reaching 12.94 percent in May 2024. These results suggest that summer readiness and local operating constraints deserve attention. They do not establish that temperature or equipment age alone causes failures.

Our most important methodological finding concerns retention. The original model used activity and revenue from the same period that defined inactivity. That overlap makes its predictive performance unsuitable for a future-facing early-warning system. In addition, the eligibility flag did not actually enforce adequate rider history, and support-category churn rates counted ticket rows rather than unique riders.

The corrected workflow separates activation from return. It measures early activity during the first thirty days after sign-up, then checks for a completed swap in days thirty through fifty-nine. Only riders with the full follow-up period are included. Early service experience and support tickets are measured before the return window, and each rider is counted once within each ticket category. This provides a fairer basis for comparing cohorts without assuming that low lifetime activity proves an onboarding problem.

The economics also need careful interpretation. The original contribution figure subtracts electricity but excludes battery wear, rent, maintenance and other costs. We therefore label it energy-only contribution and add a separate calculation for prorated station expenses. We cannot use that figure alone to conclude that the business can afford a network-wide investment.

Our recommendations are to inspect historically unreliable sites, test battery-buffer and backup-power changes against comparable sites, audit billing processes, and evaluate onboarding alongside service improvements. The corrected notebook also adds supplier, manufacturing-lot, battery-health, pricing and contract comparisons. Any production churn model should wait for time-based validation and a clear campaign-cost framework.

One important limitation remains: Google Drive blocked five source files with download-quota errors during this revision. Eight targeted logic tests passed, but the corrected full-dataset analysis has not been rerun. The report labels the old numbers as provisional and preserves the original charts for traceability. We have not invented replacement results or claimed that this is a completed causal investigation.

Recording note: this is a script, not a submitted or recorded video. Read at roughly 145–155 words per minute and rehearse against the three-minute limit.
