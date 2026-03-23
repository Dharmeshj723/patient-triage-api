import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

# ─── 1. Load Dataset ──────────────────────────────────────────────────────────
df = pd.read_csv("ml/disease_symptom_and_patient_profile_dataset.csv")
print("✅ Dataset loaded:", df.shape)

# ─── 2. Encode Symptom/Feature Columns First ─────────────────────────────────
binary_cols = ["Fever", "Cough", "Fatigue", "Difficulty Breathing"]
for col in binary_cols:
    df[col] = (df[col] == "Yes").astype(int)

df["Gender"] = (df["Gender"] == "Male").astype(int)

bp_map = {"Low": 0, "Normal": 1, "High": 2}
df["Blood Pressure"] = df["Blood Pressure"].map(bp_map)

chol_map = {"Low": 0, "Normal": 1, "High": 2}
df["Cholesterol Level"] = df["Cholesterol Level"].map(chol_map)

df["Outcome"] = (df["Outcome Variable"] == "Positive").astype(int)

print("✅ Encoding done")

# ─── 3. Assign Triage Level From Symptoms (Rule-Based Ground Truth) ───────────
# Known critical diseases — override to level 1
critical_diseases = {
    "Asthma", "Stroke", "Heart Disease", "Pancreatitis",
    "Cholecystitis", "Meningitis", "Pulmonary Embolism",
    "Appendicitis", "Sepsis", "Myocardial Infarction"
}

# Known urgent diseases — override to level 2
urgent_diseases = {
    "Influenza", "Diabetes", "Pneumonia", "Gastroenteritis",
    "Kidney Disease", "Liver Disease", "Hepatitis",
    "Mumps", "Schizophrenia", "Prostate Cancer",
    "Testicular Cancer", "Dementia"
}

# Minor diseases — override to level 4
minor_diseases = {
    "Common Cold", "Eczema", "Acne", "Allergic Rhinitis",
    "Tonsillitis", "Sinusitis", "Gout", "Williams Syndrome"
}

def assign_triage(row):
    disease = row["Disease"]

    # Override known diseases
    if disease in critical_diseases:
        base = 1
    elif disease in urgent_diseases:
        base = 2
    elif disease in minor_diseases:
        base = 4
    else:
        # Rule-based fallback using symptoms
        score = 0
        score += row["Fever"] * 1
        score += row["Difficulty Breathing"] * 3  # most serious symptom
        score += row["Fatigue"] * 1
        score += row["Cough"] * 1
        score += (1 if row["Blood Pressure"] == 2 else 0) * 2  # high BP
        score += row["Outcome"] * 2

        if score >= 6:
            base = 1
        elif score >= 4:
            base = 2
        elif score >= 2:
            base = 3
        else:
            base = 4

    # Positive outcome boosts severity by 1 level
    if row["Outcome"] == 1 and base > 1:
        base -= 1

    return base

df["triage_level"] = df.apply(assign_triage, axis=1)

print("✅ Triage levels assigned")
print(df["triage_level"].value_counts().sort_index())

# ─── 4. Define Features and Target ───────────────────────────────────────────
FEATURES = [
    "Age", "Gender", "Fever", "Cough",
    "Fatigue", "Difficulty Breathing",
    "Blood Pressure", "Cholesterol Level"
]

X = df[FEATURES]
y = df["triage_level"]

# ─── 5. Train/Test Split ──────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"✅ Split — Train: {len(X_train)}, Test: {len(X_test)}")

# ─── 6. Train Model ───────────────────────────────────────────────────────────
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42,
    class_weight="balanced"
)
model.fit(X_train, y_train)
print("✅ Model trained")

# ─── 7. Evaluate ─────────────────────────────────────────────────────────────
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\n✅ Accuracy: {accuracy * 100:.2f}%")
print("\nClassification Report:")

present_labels = sorted(y.unique())
label_names = {1: "Critical", 2: "Urgent", 3: "Moderate", 4: "Minor"}
target_names = [label_names[l] for l in present_labels]

print(classification_report(y_test, y_pred, labels=present_labels, target_names=target_names))

# ─── 8. Save Model and Features ──────────────────────────────────────────────
os.makedirs("ml", exist_ok=True)
joblib.dump(model, "ml/triage_model.pkl")
joblib.dump(FEATURES, "ml/features.pkl")
print("✅ Model saved → ml/triage_model.pkl")
print("✅ Features saved → ml/features.pkl")