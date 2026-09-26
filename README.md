# 🚴 Rider Churn Prediction & Retention Analysis

> **A machine-learning based predictive analytics project for identifying riders at risk of churn and prioritizing retention opportunities using behavioral, operational, and revenue data.**

## 📌 Overview

Customer churn is a major challenge for service-based businesses like EV battery swapping networks. Losing riders not only reduces the active user base but also results in significant recurring revenue loss.

This project uses **machine learning and business analytics** to identify EV riders who are highly likely to churn, understand the operational factors associated with their churn, and prioritize high-value riders for targeted retention strategies. 

By connecting **churn probability with revenue exposure and operational behavior** (such as battery wait times, station outages, and failure rates), this project generates actionable business insights for fleet managers and operations teams.

---

## 🎯 Objectives

The primary objectives of this project are:

* Predict the probability of rider churn using historical behavioral data.
* Classify riders into distinct churn-risk categories (Low, Medium, High).
* Identify important operational features associated with churn (e.g., wait times, swap failures).
* Estimate **Revenue-at-Risk** associated with high-risk rider segments.
* Identify high-churn and high-revenue riders for retention prioritization.
* Convert machine-learning predictions into actionable business insights and targeted promotional interventions.

---

## 📊 Dataset

The dataset integrates multiple operational and transactional logs, summarized below:

| Metric                 |      Value |
| ---------------------- | ---------: |
| Total modeling records | **19,950** |
| Training records       | **15,960** |
| Testing records        |  **3,990** |
| Processed features     |     **38** |
| Overall churn rate     | **33.88%** |
| Retained riders        | **13,190** |
| Churned riders         |  **6,760** |

### Key Feature Categories

* **Rider Activity:** Swap frequency, active days, distance driven (`km_since_last_swap`).
* **Service Quality:** Swap attempts, queue waiting time (`queue_wait_sec`), battery-related failures (`failed_no_charged_battery`).
* **Customer Support:** Number of tickets, resolution hours, CSAT scores.
* **Revenue & Pricing:** Revenue per swap, plan type, tariff code (STD vs. PARTNER), discounts applied.
* **Station Context:** Charger availability, grid outages (`grid_outage_hours`), ambient temperatures, and flood disruptions.

---

## 🔬 Project Workflow

```text
Raw Operational Data
       ↓
Data Cleaning & Consolidation
       ↓
Feature Engineering (Rolling averages, Lag features)
       ↓
Train/Test Split & Preprocessing
       ↓
Model Training (Logistic Regression, RF, Gradient Boosting)
       ↓
Model Evaluation & Feature Importance Extraction
       ↓
Churn Probability Scoring & Risk Classification
       ↓
Revenue-at-Risk Analysis
       ↓
Retention Prioritization & Business Insights
```

---

## 🤖 Machine Learning Models

Three classification models were evaluated to predict the likelihood of rider churn:

1. **Logistic Regression** (Baseline)
2. **Random Forest**
3. **Gradient Boosting**

### Model Performance

| Model                 |   Accuracy |  Precision |     Recall |   F1 Score |    ROC-AUC |
| --------------------- | ---------: | ---------: | ---------: | ---------: | ---------: |
| Logistic Regression   |     64.26% |     48.09% |     68.93% |     56.66% |     70.63% |
| Random Forest         |     75.64% |     61.86% |     73.30% |     67.10% |     83.50% |
| **Gradient Boosting** | **81.50%** | **91.83%** | **49.85%** | **64.62%** | **86.63%** |

**Gradient Boosting** achieved the highest **accuracy (81.50%) and ROC-AUC (86.63%)** among the evaluated models, making it highly effective at distinguishing between retained and churned riders. 

*Note: While precision is exceptionally high, the model's recall indicates that some actual churners may receive a lower predicted risk score. For a retention campaign, this model ensures that retention budgets (e.g., discounts) are spent efficiently on true at-risk riders.*

---

## 🔍 Churn Drivers & Feature Importance

Feature-importance analysis performed using the tree-based models revealed the following leading operational indicators of churn:

* **Queue Wait Times (`queue_wait_sec`):** Riders experiencing consistently long wait times at swap stations are significantly more likely to abandon the service.
* **Battery Unavailability (`failed_no_charged_battery`):** High rates of failed swap attempts due to empty station inventory directly correlate with immediate rider drop-off.
* **Decreasing Activity (`km_since_last_swap`):** A gradual decline in swap frequency and distance driven serves as an early behavioral warning sign of disengagement.
* **Support Ticket Volume & CSAT:** Riders with multiple unresolved support tickets or poor Customer Satisfaction (CSAT) scores exhibit a much higher churn probability.
* **Station Disruptions (`grid_outage_hours`):** Extended station downtime due to grid outages leads to rider frustration and eventual churn.

---

## 💡 Business Recommendations

1. **Targeted Retention Campaigns:** Implement automated promotional discounts or priority queue access for high-revenue riders whose churn probability crosses a 75% threshold.
2. **Inventory Optimization:** Prioritize battery deployment to stations with historically high `failed_no_charged_battery` events during peak hours to mitigate friction.
3. **Proactive Support Interventions:** Flag riders with low CSAT scores on recent tickets for immediate follow-up by the customer success team.

---

## 🚀 Setup & Installation

To run the analysis notebook locally:

1. Clone the repository:
   ```bash
   git clone https://github.com/himanshumittal1439/Rider-Churn-Prediction-and-Retention-Analysis.git
   cd Rider-Churn-Prediction-and-Retention-Analysis
   ```
2. Ensure your dataset files (`riders.csv`, `stations.csv`, `swap_events.csv`, etc.) are placed inside a `data/` directory in the project root.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Launch the notebook:
   ```bash
   jupyter notebook hackathon.ipynb
   ```
