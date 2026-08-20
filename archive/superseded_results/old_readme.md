# README — Lightweight IoT Intrusion Detection System with DA-AMS

## 1. Project Overview

This project implements a **lightweight IoT Intrusion Detection System (IDS)** designed for resource-constrained IoT environments.

The primary objective is to identify a suitable machine-learning detection engine by considering **both predictive performance and deployment efficiency**. Instead of manually fixing one classifier for deployment, the proposed **Deployment-Aware Automatic Model Selection (DA-AMS)** mechanism evaluates multiple candidate models and automatically selects the model with the highest deployment score.

The current notebook performs the experimental evaluation using the **RT-IoT2022 network-traffic dataset**. Traffic flows from the dataset are used for model training, validation, model selection, and final testing.

The current notebook demonstrates **dataset-based flow-level intrusion detection and deployment-aware model selection**. It does not perform live packet capture or live-network intrusion prevention.

---

## 2. Main Objective

The main objective is to develop and evaluate a lightweight IoT intrusion-detection framework that can identify a detection engine suitable for deployment on resource-constrained IoT environments.

The framework considers four deployment-related criteria:

1. **Accuracy** — predictive correctness.
2. **Macro-F1 Score** — balanced classification performance across classes.
3. **Inference Latency** — time required to process an individual network flow.
4. **Serialized Model Size** — storage footprint of the trained model.

DA-AMS combines these criteria into a weighted **Deployment Score** and automatically ranks the candidate detection engines.

---

## 3. Candidate Models

Three tree-based machine-learning models participate in DA-AMS:

* **Random Forest**
* **XGBoost**
* **LightGBM**

Each candidate is independently trained and tuned using the training subset.

### SVM Baseline

**Support Vector Machine (SVM)** is included separately as a conventional baseline.

SVM is **not included in DA-AMS model selection**.

The purpose of the SVM baseline is to provide an additional reference point for comparing the selected tree-based detection engine against a conventional machine-learning approach.

---

## 4. Dataset

The notebook uses the **RT-IoT2022** network-traffic dataset.

The dataset contains network-flow-level features associated with IoT network activity and attack traffic.

The notebook performs preprocessing before model development, including:

* Loading the dataset
* Inspecting the dataset structure
* Checking target distribution
* Separating input features and target labels
* Preparing data for model training
* Applying scaling where required by the model

The exact preprocessing operations should be followed in the notebook cells because the trained models depend on the resulting feature representation.

---

## 5. Experimental Data Split

The final notebook uses a **60/20/20 train-validation-test split**.

### Split

```text
100% Dataset
     │
     ├── 60% Training
     │
     ├── 20% Validation
     │
     └── 20% Independent Test
```

### Training Set — 60%

The training subset is used for:

* Model training
* Hyperparameter tuning
* Cross-validation within the hyperparameter-search procedure

### Validation Set — 20%

The validation subset is used for:

* Comparing the tuned candidate models
* Measuring predictive performance
* Measuring inference latency
* Measuring serialized model size
* Computing the DA-AMS Deployment Score
* Automatically selecting the detection engine

### Independent Test Set — 20%

The test subset is reserved for **final evaluation of the automatically selected detection engine**.

The test set is not used for hyperparameter tuning or DA-AMS model selection.

This separation provides an independent evaluation after the deployment-aware selection decision has been made.

---

## 6. Overall Methodology

The complete experimental workflow is:

```text
RT-IoT2022 Dataset
        │
        ▼
Data Preprocessing
        │
        ▼
60% Training ──────────────────┐
        │                      │
        ▼                      │
Hyperparameter Tuning          │
        │                      │
        ▼                      │
RF / XGBoost / LightGBM        │
        │                      │
        ▼                      │
20% Validation                20% Independent Test
        │                      │
        ▼                      │
Performance + Deployment       │
Metrics                        │
        │                      │
        ▼                      │
DA-AMS Deployment Score        │
        │                      │
        ▼                      │
Automatic Model Selection      │
        │                      │
        ▼                      │
Selected Detection Engine ────┘
        │
        ▼
Final Test Evaluation
```

SVM is evaluated separately as a baseline.

---

## 7. Hyperparameter Tuning

Random Forest, XGBoost, and LightGBM are tuned before DA-AMS evaluation.

The notebook uses a predefined hyperparameter-search procedure with cross-validation.

The purpose of tuning is to provide each candidate model with a reasonable and comparable configuration before deployment-aware comparison.

The best-performing tuned estimator for each model is retained:

```text
best_rf
best_xgb
best_lgb
```

These tuned estimators are subsequently evaluated on the validation set.

---

## 8. DA-AMS — Deployment-Aware Automatic Model Selection

DA-AMS is the central model-selection mechanism of the project.

The system does not simply select the model with the highest Accuracy.

Instead, it considers predictive performance together with deployment characteristics.

### DA-AMS Candidates

```text
Random Forest
XGBoost
LightGBM
      │
      ▼
Validation Evaluation
      │
      ├── Accuracy
      ├── Macro-F1
      ├── Inference Latency
      └── Model Size
      │
      ▼
Normalization
      │
      ▼
Weighted Deployment Score
      │
      ▼
Ranking
      │
      ▼
Highest-Scoring Model
```

The model with the highest Deployment Score becomes the selected detection engine.

---

## 9. DA-AMS Evaluation Criteria

The current DA-AMS formulation uses four criteria.

### 9.1 Accuracy

Accuracy is treated as a **benefit criterion**.

Higher accuracy produces a better normalized score.

### 9.2 Macro-F1

Macro-F1 is treated as a **benefit criterion**.

Higher Macro-F1 produces a better normalized score.

Macro-F1 is particularly useful for representing balanced predictive performance across the evaluated classes.

### 9.3 Inference Latency

Inference latency is treated as a **cost criterion**.

Lower latency is preferred because the objective is to support lightweight and responsive IoT intrusion detection.

The notebook measures prediction time and calculates the average latency per network flow.

### 9.4 Serialized Model Size

Serialized model size is treated as a **cost criterion**.

A smaller model requires less storage and is more suitable for deployment in resource-constrained environments.

The notebook serializes the trained model and measures the resulting file size.

---

## 10. Deployment Score

The current weighting scheme is:

| Criterion  | Weight | Type    |
| ---------- | -----: | ------- |
| Accuracy   |    40% | Benefit |
| Macro-F1   |    30% | Benefit |
| Latency    |    20% | Cost    |
| Model Size |    10% | Cost    |

Therefore:

```text
Deployment Score =
    0.40 × Accuracy Score
  + 0.30 × Macro-F1 Score
  + 0.20 × Latency Score
  + 0.10 × Model Size Score
```

The individual criteria are normalized before calculating the weighted score.

---

## 11. Min-Max Normalization

### Benefit Criteria

Accuracy and Macro-F1 are benefit criteria.

For a benefit criterion:

```text
Normalized Score =
(x - minimum) / (maximum - minimum)
```

A higher original value therefore produces a higher normalized score.

### Cost Criteria

Latency and model size are cost criteria.

For a cost criterion:

```text
Normalized Score =
(maximum - x) / (maximum - minimum)
```

A lower original value therefore produces a higher normalized score.

---

## 12. Model Selection

After normalization, the weighted Deployment Score is calculated for each DA-AMS candidate.

The candidates are ranked according to their Deployment Score.

The candidate with the highest score is selected automatically:

```text
Highest Deployment Score
          │
          ▼
Selected Detection Engine
          │
          ▼
Selected_IDPS_Model.pkl
```

The selected model is saved as:

```text
Selected_IDPS_Model.pkl
```

This file represents the model selected by the DA-AMS mechanism for the current experiment.

---

## 13. SVM Baseline

SVM is evaluated separately from DA-AMS.

The baseline uses fixed conventional parameters rather than participating in the DA-AMS hyperparameter-selection process.

The baseline provides an independent reference for comparing:

* Accuracy
* Macro-F1
* ROC-AUC
* Inference latency
* Model size
* Training time

The SVM result should not be used to determine which of Random Forest, XGBoost, or LightGBM is selected by DA-AMS.

---

## 14. Validation Results

The validation stage reports several metrics for the three DA-AMS candidates.

The reported metrics include:

* Accuracy
* Macro-F1
* ROC-AUC
* Correct predictions
* Errors
* Inference latency

Correct predictions and errors are included for interpretability.

For a fixed validation set:

```text
Errors = Total Validation Samples - Correct Predictions
```

Errors are therefore **not an additional independent DA-AMS criterion**, because they represent the same predictive information already reflected by accuracy.

ROC-AUC is also reported as a supplementary evaluation metric and is not part of the current four-criterion Deployment Score unless explicitly added to the formulation.

---

## 15. Final Test Evaluation

After DA-AMS selects the detection engine, the selected model is evaluated on the independent 20% test set.

The final evaluation is intended to report the performance of the selected engine on previously unseen data.

The final evaluation can include:

* Accuracy
* Macro-F1
* ROC-AUC
* Correct predictions
* Errors
* Confusion matrix
* Inference latency

The final test results should be used as the primary reported performance of the selected detection engine.

---

## 16. Confusion Matrix

The notebook generates a confusion matrix for the final selected detection engine.

The confusion matrix provides a class-level view of:

* Correct predictions
* False positives
* False negatives
* Overall classification behavior

This is useful for understanding the types of detection errors made by the final model.

---

## 17. ROC Curve Analysis

The notebook also evaluates ROC behavior for the candidate models.

ROC-AUC is used as an additional predictive-performance indicator.

ROC curves should be interpreted according to the dataset split on which they are generated.

Candidate-model ROC comparisons on the validation set should be described as **validation analysis**, while the selected model's final ROC evaluation should be based on the independent test set.

---

## 18. Feature Importance

For the selected tree-based detection engine, feature importance is extracted where supported by the model.

Feature importance helps identify which network-flow features contribute most strongly to the model's decisions.

This analysis provides interpretability for the selected detection engine and can help identify network characteristics associated with attack detection.

---

## 19. Detection Demonstration

The notebook contains a flow-level detection demonstration using samples derived from the dataset.

The demonstration passes network-flow feature rows to the selected model and produces a prediction.

Conceptually:

```text
Dataset Network Flow
        │
        ▼
Selected Detection Engine
        │
        ▼
Prediction
        │
        ├── Benign
        └── Attack
```

This demonstrates the inference stage of the proposed detection engine.

---

## 20. Current Real-Time Scope

The current notebook should be understood as a **dataset-based experimental IDS implementation**.

It does not currently perform:

* Live packet capture
* Npcap-based packet acquisition
* Live network-flow extraction
* Live network scanning
* Real-time firewall blocking
* Physical IoT-router deployment

The measured inference latency demonstrates the computational behavior of the trained detection engines and supports their evaluation for lightweight, responsive deployment.

---

## 21. Intended Future Live Deployment

The selected model can serve as the inference engine for a future live-network implementation.

A future deployment architecture could be:

```text
Live IoT Network
       │
       ▼
Packet Capture
       │
       ▼
Flow Generation
       │
       ▼
Feature Extraction
       │
       ▼
Selected_IDPS_Model.pkl
       │
       ▼
Attack / Benign Prediction
       │
       ▼
Mitigation / Alert
```

For live deployment, the feature-extraction stage must produce the same feature representation expected by the trained model.

Therefore, live deployment is a separate engineering layer built around the trained detection engine.

---

## 22. Nmap and Live Scanning

The current experimental notebook should not be interpreted as performing Nmap-based live scanning.

The current model evaluation uses network-flow records from the RT-IoT2022 dataset.

Nmap can be incorporated into a future live-network deployment for network reconnaissance or device/service discovery, but Nmap output should not be treated as a direct replacement for the network-flow features used to train the current ML models.

A live deployment would require an appropriate mechanism to convert live network activity into the feature representation expected by the selected model.

---

## 23. Resource-Constrained IoT Motivation

The lightweight objective is motivated by the limited computational and storage resources available on many IoT and edge devices.

The framework therefore evaluates not only predictive performance but also:

* Inference latency
* Model size

This creates a deployment-aware comparison between candidate detection engines.

A model with slightly higher predictive performance may not necessarily be the best deployment choice if its computational or storage requirements are substantially greater.

Conversely, a lightweight model should not be selected solely because it is small or fast if its detection performance is inadequate.

DA-AMS is designed to balance these considerations automatically.

---

## 24. Reproducibility

The notebook uses a fixed random state where applicable to improve reproducibility.

The main experimental configuration includes:

* Fixed train/validation/test splitting
* Stratified splitting
* Predefined hyperparameter search
* Cross-validation during tuning
* Fixed DA-AMS weights
* Fixed model-selection criteria

For reproducibility, the complete notebook should be executed from the beginning rather than mixing variables or outputs from older notebook versions.

---

## 25. Important Experimental Rule

Only the current final notebook should be treated as the **source of truth for the reported experimental results**.

Older notebooks may contain:

* Previous 80/20 experiments
* Earlier model configurations
* Earlier SVM experiments
* Previous DA-AMS implementations
* Intermediate results

These should not be mixed with the current 60/20/20 results.

Older notebooks can be retained in an archive for experimental history, but the final paper should use results generated from the final notebook.

---

## 26. Recommended Project Structure

```text
IoT_IDS_Project/
│
├── Final/
│   ├── final.ipynb
│   ├── README.md
│   ├── Selected_IDPS_Model.pkl
│   ├── svm_baseline.pkl
│   └── figures/
│
├── data/
│   └── RT_IoT2022.csv
│
└── Archive/
    ├── notebook_v1.ipynb
    ├── notebook_v2.ipynb
    ├── notebook_80_20.ipynb
    └── old_experiments/
```

The exact filenames may be changed according to the local project organization.

---

## 27. Expected Outputs

After successful execution, the notebook should produce:

1. Dataset inspection results.
2. Train/validation/test split information.
3. Hyperparameter-search results.
4. Best RF model.
5. Best XGBoost model.
6. Best LightGBM model.
7. SVM baseline results.
8. Candidate validation metrics.
9. Correct and incorrect prediction counts.
10. Inference latency measurements.
11. Serialized model sizes.
12. Normalized DA-AMS scores.
13. Deployment Scores.
14. Candidate ranking.
15. Automatically selected detection engine.
16. `Selected_IDPS_Model.pkl`.
17. Final independent test results.
18. Confusion matrix.
19. ROC analysis.
20. Feature-importance analysis.
21. Dataset-flow detection demonstration.

---

## 28. Interpretation of the Final Result

The selected model should not be predetermined.

DA-AMS should select the model that achieves the highest Deployment Score according to the predefined weighting scheme.

For example, if XGBoost achieves the highest predictive performance but LightGBM has substantially lower inference latency, DA-AMS determines which trade-off is preferable according to the predefined weights.

The model-selection result should therefore be reported exactly as produced by the algorithm.

The selected model should not be manually changed after seeing the results.

---

## 29. Research Contribution

The central contribution of the implementation is the **Deployment-Aware Automatic Model Selection (DA-AMS)** mechanism.

The framework moves beyond selecting a classifier solely according to predictive performance.

Instead, it considers:

```text
Detection Performance
        +
Deployment Efficiency
        ↓
Automatic Model Selection
```

The mechanism is intended to support the selection of a suitable lightweight detection engine for resource-constrained IoT environments.

The current experimental results validate this mechanism using the RT-IoT2022 dataset.

---

## 30. Limitations

The current implementation has several limitations that should be acknowledged:

1. Evaluation is based on the RT-IoT2022 dataset.
2. The current notebook does not perform live packet capture.
3. The current notebook does not perform live Npcap-based traffic acquisition.
4. The current notebook does not implement live firewall blocking.
5. Live deployment would require a reliable flow-generation and feature-extraction pipeline.
6. Cross-dataset validation is not part of the current experiment.
7. Hardware-level resource consumption on embedded IoT devices is not directly measured.
8. The measured model latency represents inference over the prepared dataset features and should not be interpreted as complete end-to-end packet-to-decision latency.

These limitations define the boundary of what is experimentally demonstrated by the current notebook.

---

## 31. Future Work

Future development can extend the framework toward:

* Live packet capture using Npcap or an equivalent mechanism.
* Automated live network-flow generation.
* Real-time feature extraction.
* Deployment on ARM-based edge devices or IoT gateways.
* Firewall-based automated mitigation.
* Cross-dataset validation.
* Independent network-traffic collection.
* Hardware-level memory and CPU profiling.
* IPv6-specific telemetry.
* Evaluation under changing IoT traffic conditions.
* End-to-end packet-to-decision latency measurement.

---

## 32. Summary

This notebook implements a **60/20/20 experimental framework for lightweight IoT intrusion detection**.

The workflow uses:

```text
60% Training
      ↓
Hyperparameter Tuning
      ↓
RF / XGBoost / LightGBM
      ↓
20% Validation
      ↓
DA-AMS
      ↓
Deployment Score
      ↓
Automatic Model Selection
      ↓
20% Independent Test
      ↓
Final Evaluation
```

SVM is maintained as a **separate conventional baseline** and does not participate in DA-AMS selection.

The central objective is to automatically identify a detection engine that provides an appropriate balance between **predictive performance and deployment efficiency**, supporting the broader goal of lightweight IoT intrusion detection.

The current notebook validates the proposed approach using **dataset-derived network flows**. Live network capture, live feature extraction, and automated mitigation are considered deployment extensions rather than components of the current dataset-based experimental validation.
