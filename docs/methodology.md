# Scientific Methodology

The methodology for DA-AMS follows this pipeline:

1. **RT-IoT2022 Dataset**: Data is loaded and prepared.
2. **Data Preprocessing**: Features and binary targets are cleaned and encoded.
3. **Dataset Splitting**: The data is partitioned into:
   - 60% Training
   - 20% Validation
   - 20% Independent Test
4. **Candidate Training**: Random Forest, XGBoost, and LightGBM are trained and hyperparameter-tuned on the training set.
5. **DA-AMS Evaluation**: Candidate models are evaluated on the 20% validation set using four criteria:
   - Accuracy (Benefit)
   - Macro-F1 (Benefit)
   - Inference Latency (Cost)
   - Serialized Model Size (Cost)
6. **Normalization and Scoring**: Metrics are normalized, and a Deployment Score is computed based on defined weightings.
7. **Automatic Model Selection**: The model with the highest Deployment Score is selected.
8. **Final Evaluation**: The selected model is evaluated against the 20% independent test set.

**Baseline Constraint**: SVM is evaluated separately as a fixed-parameter baseline and is not subjected to DA-AMS.
