import pandas as pd

# Dataset path
DATA_PATH = "data/raw/Amazon-Products.csv"

# Load dataset
df = pd.read_csv(DATA_PATH)

print("="*50)
print("Dataset Loaded Successfully")
print("="*50)

print("\nShape:")
print(df.shape)

print("\nColumns:")
print(df.columns)

print("\nFirst 5 Rows:")
print(df.head())

print("\nDataset Information:")
print(df.info())

print("\nMissing Values:")
print(df.isnull().sum())

print("\nDuplicate Rows:")
print(df.duplicated().sum())