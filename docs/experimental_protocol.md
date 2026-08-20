# Experimental Protocol

## DA-AMS Criteria

The candidate models are ranked using the following Deployment Score weights:
- Accuracy = 40%
- Macro-F1 = 30%
- Inference Latency = 20%
- Model Size = 10%

## Baseline

The Support Vector Machine (SVM) uses conventional parameters and is evaluated solely to provide a performance baseline. It is fundamentally excluded from DA-AMS candidate ranking.

## Evaluation Split Breakdown

The 60/20/20 final dataset distribution is implemented internally via a two-stage process:
- **Stage 1**: 80% temporary pool / 20% final independent test.
- **Stage 2**: The 80% temporary pool is divided such that 75% goes to training (amounting to 60% of total data) and 25% goes to validation (amounting to 20% of total data).
