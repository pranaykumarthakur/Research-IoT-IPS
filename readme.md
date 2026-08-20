# Lightweight IoT Intrusion Detection System with Deployment-Aware Automatic Model Selection (DA-AMS)

## Project Overview

This repository contains the official implementation of a **Lightweight IoT Intrusion Detection System** featuring **Deployment-Aware Automatic Model Selection (DA-AMS)**. The project is designed to evaluate, rank, and automatically select the most suitable machine-learning detection engine for resource-constrained IoT environments.

## Research Objective

The primary objective of this project is to investigate a lightweight IoT intrusion-detection framework that automatically selects a deployment-suitable machine-learning detection engine by jointly considering predictive performance and deployment efficiency.

## Main Contribution

The core contribution is the introduction of **DA-AMS**, which automatically ranks candidate models (**Random Forest**, **XGBoost**, and **LightGBM**) using a multi-criteria evaluation approach:

- **Accuracy** (Benefit) - 40%
- **Macro-F1** (Benefit) - 30%
- **Inference Latency** (Cost) - 20%
- **Serialized Model Size** (Cost) - 10%

DA-AMS normalizes these metrics and selects the model with the highest overall **Deployment Score**.

## Methodology

The experimental workflow evaluates models on the **RT-IoT2022 Dataset** using the following data split:

- **60% Training**: Used for training and hyperparameter tuning.
- **20% Validation**: Used for DA-AMS candidate model evaluation, metric calculation, and automatic model selection.
- **20% Independent Test**: Used for final evaluation of the automatically selected detection engine.

## Baseline Model

**Support Vector Machine (SVM)** is evaluated separately as a conventional baseline with fixed parameters. It is **not** included in the DA-AMS candidate ranking or model selection process.

## Final Selected Model

The artifact `models/Selected_IDPS_Model.pkl` contains the final detection engine that was automatically selected by DA-AMS as the optimal model balancing predictive capability and deployment efficiency. 
The separate baseline model is available at `models/svm_baseline.pkl`.

## Reproducibility

The authoritative final experimental implementation is provided in:

`notebook/final_60_20_20_DA_AMS.ipynb`

Researchers can run this notebook to replicate the data preparation, model training, DA-AMS selection, and final independent testing.

*Note: Please refer to the `docs/` directory for extended details on the methodology and experimental protocol, and the `archive/` directory for historical research prototypes (not part of the final methodology).*
