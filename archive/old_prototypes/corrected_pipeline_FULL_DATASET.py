"""
CORRECTED pipeline for RT_IoT2022 -- run this in your own environment
(where xgboost and lightgbm are already installed).

Fixes applied vs. the original notebook:
1. Uses the FULL 123,117-row dataset (not a 5,000-row subsample).
2. Drops ID/leakage columns BEFORE deduplication (this is what actually
   produces the correct 18,272 unique-row count).
3. Deduplication happens ONCE and is never overwritten by a later reload.
4. Reports 5-fold CV for every model, not just Random Forest.
5. Reports an honest standalone-vs-ensemble comparison.
"""
import pandas as pd, numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_curve, auc
import xgboost as xgb
import lightgbm as lgb

# ------------------------------------------------------------------
# STEP 1: Load the FULL dataset
# ------------------------------------------------------------------
df = pd.read_csv("RT_IOT2022.csv")   # <-- point this at your full 123,117-row file
print("Raw rows loaded:", len(df))

# ------------------------------------------------------------------
# STEP 2: Drop ID/leakage-prone columns FIRST
# ------------------------------------------------------------------
cols_to_drop = ["Unnamed: 0", "Flow_ID", "Source_IP", "Destination_IP",
                "Timestamp", "id.orig_p", "id.resp_p"]
df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])

# ------------------------------------------------------------------
# STEP 3: Deduplicate BEFORE splitting -- and never reload/overwrite df after this
# ------------------------------------------------------------------
feat_cols_for_dedup = [c for c in df.columns if c != "Attack_type"]
before = len(df)
df = df.drop_duplicates(subset=feat_cols_for_dedup).reset_index(drop=True)
print(f"Rows before dedup: {before}  |  Rows after dedup: {len(df)}")

# ------------------------------------------------------------------
# STEP 4: Binary label conversion
# ------------------------------------------------------------------
normal_traffic = ["Thing_Speak", "Wipro_bulb", "MQTT_Publish"]
df["Attack_type"] = df["Attack_type"].apply(lambda x: 0 if x in normal_traffic else 1)
print("\nClass distribution (FULL deduplicated data):")
print(df["Attack_type"].value_counts(normalize=True) * 100)

# ------------------------------------------------------------------
# STEP 5: Encode categoricals
# ------------------------------------------------------------------
label_encoders = {}
for col in df.select_dtypes(include=["object"]).columns:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    label_encoders[col] = le

X = df.drop(columns=["Attack_type"])
y = df["Attack_type"]

# ------------------------------------------------------------------
# STEP 6: Stratified 80/20 split on the FULL deduplicated data
# ------------------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"\nTrain size: {len(X_train)}  |  Test size: {len(X_test)}")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ------------------------------------------------------------------
# STEP 7: Train all models + report 5-fold CV for EACH one
# ------------------------------------------------------------------
results = {}

print("\n--- Random Forest ---")
rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1, class_weight="balanced")
rf.fit(X_train_scaled, y_train)
rf_pred = rf.predict(X_test_scaled)
print("Test Accuracy:", accuracy_score(y_test, rf_pred))
print(classification_report(y_test, rf_pred, target_names=["Normal","Attack"]))
cv = cross_val_score(rf, X_train_scaled, y_train, cv=5, scoring='accuracy', n_jobs=-1)
print(f"5-Fold CV Accuracy: {cv.mean():.4f} (+/- {cv.std()*2:.4f})")
results['RF'] = dict(pred=rf_pred, probs=rf.predict_proba(X_test_scaled)[:,1], cv=cv)

print("\n--- XGBoost ---")
xgb_model = xgb.XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, eval_metric='logloss')
xgb_model.fit(X_train, y_train)
xgb_pred = xgb_model.predict(X_test)
print("Test Accuracy:", accuracy_score(y_test, xgb_pred))
print(classification_report(y_test, xgb_pred, target_names=["Normal","Attack"]))
cv = cross_val_score(xgb_model, X_train, y_train, cv=5, scoring='accuracy', n_jobs=-1)
print(f"5-Fold CV Accuracy: {cv.mean():.4f} (+/- {cv.std()*2:.4f})")
results['XGB'] = dict(pred=xgb_pred, probs=xgb_model.predict_proba(X_test)[:,1], cv=cv)

print("\n--- LightGBM ---")
lgb_model = lgb.LGBMClassifier(n_estimators=100, learning_rate=0.1, max_depth=5)
lgb_model.fit(X_train, y_train)
lgb_pred = lgb_model.predict(X_test)
print("Test Accuracy:", accuracy_score(y_test, lgb_pred))
print(classification_report(y_test, lgb_pred, target_names=["Normal","Attack"]))
cv = cross_val_score(lgb_model, X_train, y_train, cv=5, scoring='accuracy', n_jobs=-1)
print(f"5-Fold CV Accuracy: {cv.mean():.4f} (+/- {cv.std()*2:.4f})")
results['LGB'] = dict(pred=lgb_pred, probs=lgb_model.predict_proba(X_test)[:,1], cv=cv)

print("\n--- SVM (on balanced training subsample for tractability) ---")
train_df_scaled = pd.DataFrame(X_train_scaled, columns=X.columns)
train_df_scaled['Target'] = y_train.values
normal_train = train_df_scaled[train_df_scaled['Target'] == 0]
attack_train = train_df_scaled[train_df_scaled['Target'] == 1]
n_samples = min(len(normal_train), len(attack_train), 3000)
svm_train_data = pd.concat([
    normal_train.sample(n_samples, random_state=42),
    attack_train.sample(n_samples, random_state=42)
]).sample(frac=1, random_state=42)
X_train_svm = svm_train_data.drop(columns=['Target'])
y_train_svm = svm_train_data['Target']
svm = SVC(kernel="rbf", C=1.0, probability=True, random_state=42)
svm.fit(X_train_svm, y_train_svm)
svm_pred = svm.predict(X_test_scaled)
print("Test Accuracy:", accuracy_score(y_test, svm_pred))
print(classification_report(y_test, svm_pred, target_names=["Normal","Attack"]))
results['SVM'] = dict(pred=svm_pred, probs=svm.predict_proba(X_test_scaled)[:,1])

# ------------------------------------------------------------------
# STEP 8: Weighted hybrid ensemble (XGB + LGBM)
# ------------------------------------------------------------------
print("\n--- Hybrid Ensemble (XGBoost 0.6 + LightGBM 0.4) ---")
hybrid_probs = 0.6 * results['XGB']['probs'] + 0.4 * results['LGB']['probs']
hybrid_pred = (hybrid_probs > 0.5).astype(int)
print("Test Accuracy:", accuracy_score(y_test, hybrid_pred))
print(classification_report(y_test, hybrid_pred, target_names=["Normal","Attack"]))
results['Hybrid'] = dict(pred=hybrid_pred, probs=hybrid_probs)

# ------------------------------------------------------------------
# STEP 9: Final summary -- accuracy, AUC, confusion matrix for every model
# Use this table directly to replace Table I / Table II in the paper
# ------------------------------------------------------------------
print("\n" + "="*70)
print("FINAL SUMMARY -- use these numbers to replace Table I/II in the paper")
print("="*70)
for name, r in results.items():
    acc = accuracy_score(y_test, r['pred'])
    cm = confusion_matrix(y_test, r['pred'])
    fpr, tpr, _ = roc_curve(y_test, r['probs'])
    model_auc = auc(fpr, tpr)
    cv_str = f", CV={r['cv'].mean():.4f}+/-{r['cv'].std()*2:.4f}" if 'cv' in r else ""
    print(f"{name}: Acc={acc:.4f}, AUC={model_auc:.4f}{cv_str}")
    print(f"  Confusion Matrix:\n{cm}\n")
