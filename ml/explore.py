import pandas as pd

df = pd.read_csv("ml/disease_symptom_and_patient_profile_dataset.csv")

print("Shape:", df.shape)
print("\nColumns:", df.columns.tolist())
print("\nFirst 3 rows:")
print(df.head(3))
print("\nMissing values:")
print(df.isnull().sum())
print("\nUnique values in each column:")
for col in df.columns:
    print(f"{col}: {df[col].unique()[:5]}")