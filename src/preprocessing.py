import pandas as pd
import os
from dashboard.prediction import show as show_predictionvs

print("Running:", os.path.abspath(__file__))

# Load dataset
df = pd.read_csv("data/raw/Amazon-Products.csv")

print("Original Shape:", df.shape)

# Remove unwanted column
df.drop(columns=["Unnamed: 0"], inplace=True)

# Remove duplicates
df.drop_duplicates(inplace=True)

# Remove missing product names
df.dropna(subset=["name"], inplace=True)

# Clean price columns
for col in ["discount_price", "actual_price"]:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace("₹", "", regex=False)
        .str.replace(",", "", regex=False)
    )

    df[col] = pd.to_numeric(df[col], errors="coerce")

# Clean ratings
df["ratings"] = pd.to_numeric(df["ratings"], errors="coerce")

# Clean number of ratings
df["no_of_ratings"] = (
    df["no_of_ratings"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .str.extract(r"(\d+)", expand=False)
)

df["no_of_ratings"] = pd.to_numeric(
    df["no_of_ratings"],
    errors="coerce"
)

# Remove rows missing essential values
df.dropna(
    subset=[
        "ratings",
        "discount_price",
        "actual_price",
        "no_of_ratings",
    ],
    inplace=True,
)

print("Cleaned Shape:", df.shape)

# Save processed dataset
df.to_csv(
    "data/processed/clean_data.csv",
    index=False
)

print("Preprocessing completed successfully!")