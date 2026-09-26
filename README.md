# 🚴 Rider Churn Prediction & Retention Analysis

> **A machine-learning based predictive analytics project for identifying riders at risk of churn and prioritizing retention opportunities using behavioral, operational, and revenue data.**

## 📌 Overview

Customer churn is a major challenge for service-based businesses. Losing customers not only reduces the customer base but can also result in significant revenue loss.

This project uses **machine learning and business analytics** to identify riders who are more likely to churn, understand the factors associated with churn, and identify high-value riders who may require targeted retention efforts.

The project goes beyond simply predicting churn by connecting **churn probability with revenue exposure and operational behavior** to generate actionable business insights.

---

## 🎯 Objectives

The main objectives of this project are:

* Predict the probability of rider churn.
* Classify riders into different churn-risk categories.
* Identify important features associated with churn predictions.
* Analyze high-risk rider segments.
* Estimate revenue associated with high-risk riders.
* Identify high-churn and high-revenue riders for retention prioritization.
* Convert machine-learning predictions into actionable business insights.

---

## 📊 Dataset

The project contains:

| Metric                 |      Value |
| ---------------------- | ---------: |
| Total modeling records | **19,950** |
| Training records       | **15,960** |
| Testing records        |  **3,990** |
| Processed features     |     **38** |
| Overall churn rate     | **33.88%** |
| Retained riders        | **13,190** |
| Churned riders         |  **6,760** |

The features represent different aspects of rider activity, service performance, customer support, revenue, vehicle type, plan type, and fleet status.

### Key Feature Categories

* Rider activity
* Service attempts and failures
* Failure rate
* Battery-related failures
* Support tickets
* Queue waiting time
* Resolution metrics
* Revenue
* Revenue per swap
* Vehicle class
* Plan type
* Fleet status
* Partner information

---

## 🔬 Project Workflow

```text
Raw Data
   ↓
Data Cleaning
   ↓
Feature Engineering
   ↓
Train/Test Split
   ↓
Data Preprocessing
   ↓
Model Training
   ↓
Model Evaluation
   ↓
Feature Importance Analysis
   ↓
Churn Probability Scoring
   ↓
Risk Classification
   ↓
High-Risk Rider Profiling
   ↓
Segment Analysis
   ↓
Revenue-at-Risk Analysis
   ↓
Retention Prioritization
   ↓
Business Insights
```

---

## 🤖 Machine Learning Models

Three classification models were evaluated:

1. **Logistic Regression**
2. **Random Forest**
3. **Gradient Boosting**

### Model Performance

| Model                 |   Accuracy |  Precision |     Recall |   F1 Score |    ROC-AUC |
| --------------------- | ---------: | ---------: | ---------: | ---------: | ---------: |
| Logistic Regression   |     64.26% |     48.09% |     68.93% |     56.66% |     70.63% |
| Random Forest         |     75.64% |     61.86% |     73.30% |     67.10% |     83.50% |
| **Gradient Boosting** | **81.50%** | **91.83%** | **49.85%** | **64.62%** | **86.63%** |

Gradient Boosting achieved the highest **accuracy and ROC-AUC** among the evaluated models.

However, model selection depends on the business objective. Its relatively lower recall means that some actual churners may receive lower predicted risk, so the model should be interpreted alongside the other evaluation metrics.

---

## 🔍 Churn Drivers

Feature-importance analysis was performed using the tree-based models.

Some of the strongest model-associated features included:

* **Revenue per swap**
* Total revenue
* Support tickets
* Failed attempts
* Failure rate
* Fleet status
* Plan type
* Vehicle class
* No-battery failures
* Queue waiting time
* Service attempts

### Important Note

Feature importance indicates how strongly a feature contributes to the model's predictions. It **does not by itself prove that the feature causes churn**.

---

## 🚨 Churn Risk Analysis

The test set contained **3,990 riders**.

| Risk Band     |  Riders | Percentage |
| ------------- | ------: | ---------: |
| Low Risk      |   2,262 |     56.69% |
| Medium Risk   |   1,072 |     26.87% |
| **High Risk** | **656** | **16.44%** |

The average predicted churn probability among the high-risk riders was approximately **85.43%**.

---

## 💰 Revenue at Risk

One of the key objectives was to connect churn risk with potential business exposure.

| Metric                              |              Value |
| ----------------------------------- | -----------------: |
| Total test-set revenue              | **₹45,916,065.75** |
| High-risk rider revenue             |  **₹4,779,133.70** |
| High-risk revenue share             |         **10.41%** |
| Average revenue per high-risk rider |      **₹7,285.26** |

This provides a business-oriented view of churn rather than looking only at classification metrics.

---

## 📈 High-Risk Segments

### Vehicle Class

* **2W:** 579 high-risk riders — **88.26%**
* **3W:** 77 high-risk riders — **11.74%**

### Plan Type

* **Partner-billed:** 432 — **65.85%**
* **Pay-as-you-go:** 152 — **23.17%**
* **Prepaid pack:** 72 — **10.98%**

### Largest High-Risk Revenue Segment

The largest high-risk segment was:

> **2W + Partner-billed + Fleet Partner**

* High-risk riders: **359**
* Revenue: **₹2,796,182.10**
* Revenue share of high-risk population: **58.51%**

---

## 🎯 Retention Prioritization

The project combines:

**Churn Probability + Revenue Exposure**

to identify riders who may represent higher business exposure.

The analysis identified:

* **15 high-churn + high-revenue target riders**
* Revenue represented: **₹291,043.05**
* High-revenue threshold: **₹17,424.51**

This allows a business to move from:

> **"Who might churn?"**

to:

> **"Which potentially high-value riders should we investigate first?"**

---

## 💡 Key Business Insights

### 1. Churn is a significant business problem

The overall dataset churn rate was **33.88%**, indicating a substantial portion of riders were classified as churned.

### 2. High-risk riders represent meaningful revenue exposure

The 656 high-risk riders represented approximately **₹4.78 million**, or **10.41% of test-set revenue**.

### 3. High-risk riders are concentrated in 2W

2W riders represented **88.26% of the high-risk population**.

### 4. Operational factors matter

Service failures, support activity, and queue waiting time were among the variables contributing to model predictions.

### 5. Revenue can improve retention prioritization

Combining churn probability with revenue helps distinguish between riders with different levels of potential business exposure.

---

## 🛠️ Technologies Used

* **Python**
* **Pandas**
* **NumPy**
* **Scikit-learn**
* **Matplotlib**
* **Seaborn**
* **Jupyter Notebook**

### Machine Learning

* Logistic Regression
* Random Forest
* Gradient Boosting
* Feature importance analysis
* Probability-based risk scoring

---

## 📂 Project Structure

```text
Rider-Churn-Prediction/
│
├── 📓 Rider_Churn_Prediction_Analysis.ipynb
│
├── 📊 data/
│   └── dataset files
│
├── 📈 visualizations/
│   └── generated charts
│
├── 📄 report/
│   └── project report
│
└── README.md
```

> Dataset files may be excluded from the repository if they contain confidential or restricted information.

---

## 🚀 How to Run

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd Rider-Churn-Prediction
```

### 2. Install dependencies

```bash
pip install pandas numpy scikit-learn matplotlib seaborn jupyter
```

### 3. Launch Jupyter Notebook

```bash
jupyter notebook
```

### 4. Open

```text
Rider_Churn_Prediction_Analysis.ipynb
```

Run the notebook from beginning to end.

---

## 📌 Final Outcome

This project demonstrates an end-to-end machine-learning workflow:

**Data → Features → Models → Predictions → Risk → Revenue → Business Action**

Rather than stopping at model accuracy, the project connects predictive modeling with **customer retention and revenue-at-risk analysis**.

---

## 👥 Project

**Project:** Rider Churn Prediction & Retention Analysis
**Category:** Data Analytics / Machine Learning / Predictive Analytics
**Focus:** Customer Churn, Risk Scoring & Retention

---

## ⭐ Conclusion

The project demonstrates how machine learning can be used to identify potential churn, understand model-associated churn signals, segment high-risk riders, and prioritize retention opportunities based on both **predicted churn probability and revenue exposure**.

The final analysis provides a foundation for a data-driven retention strategy and demonstrates how predictive analytics can be translated into practical business insights.

---

### 📬 Future Improvements

Potential future extensions include:

* Hyperparameter tuning
* Cross-validation
* Model calibration
* Explainable AI using SHAP
* Automated retention recommendations
* Interactive Power BI dashboard
* Real-time churn monitoring
* Model deployment through an API
* Periodic retraining with new rider behavior data

---

⭐ **If you found this project interesting, consider starring the repository!**
