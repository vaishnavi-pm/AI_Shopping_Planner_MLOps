import pandas as pd

# Load cleaned dataset
df = pd.read_csv("data/processed/clean_data.csv")

print("Original Shape:", df.shape)

# Feature 1: Discount Amount
df["discount_amount"] = df["actual_price"] - df["discount_price"]

# Feature 2: Discount Percentage
df["discount_percentage"] = (
    (df["actual_price"] - df["discount_price"])
    / df["actual_price"]
) * 100

# Feature 3: Popularity Score
df["popularity_score"] = (
    df["ratings"] * df["no_of_ratings"]
)

# Feature 4: Value Score
df["value_score"] = (
    df["popularity_score"] /
    df["discount_price"]
)

# Replace infinity values if any
df.replace([float("inf"), -float("inf")], 0, inplace=True)

# Fill missing values
df.fillna(0, inplace=True)

print("\nNew Shape:", df.shape)

print("\nNew Features:")
print(df[[
    "discount_amount",
    "discount_percentage",
    "popularity_score",
    "value_score"
]].head())

# Save engineered dataset
df.to_csv(
    "data/processed/feature_data.csv",
    index=False
)

print("\nFeature Engineering Completed Successfully!")
print("Saved: data/processed/feature_data.csv")