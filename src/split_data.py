import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Load feature engineered dataset
df = pd.read_csv("data/processed/feature_data.csv")

# -------------------------
# Create target column
# -------------------------
def shopping_decision(row):
    if row["ratings"] >= 4.2 and row["discount_percentage"] >= 40:
        return "Buy Now"
    elif row["ratings"] >= 3.5 or row["discount_percentage"] >= 20:
        return "Wait"
    else:
        return "Avoid"

df["decision"] = df.apply(shopping_decision, axis=1)

# -------------------------
# Encode categorical columns
# -------------------------
encoder_main = LabelEncoder()
encoder_sub = LabelEncoder()

df["main_category"] = encoder_main.fit_transform(df["main_category"])
df["sub_category"] = encoder_sub.fit_transform(df["sub_category"])

# -------------------------
# Select features
# -------------------------
X = df[
    [
        "ratings",
        "no_of_ratings",
        "discount_price",
        "actual_price",
        "discount_amount",
        "discount_percentage",
        "popularity_score",
        "value_score",
        "main_category",
        "sub_category",
    ]
]

y = df["decision"]

# -------------------------
# Split dataset
# -------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Training Samples:", len(X_train))
print("Testing Samples:", len(X_test))

# Save datasets
train_df = X_train.copy()
train_df["decision"] = y_train.values

test_df = X_test.copy()
test_df["decision"] = y_test.values

train_df.to_csv("data/processed/train.csv", index=False)
test_df.to_csv("data/processed/test.csv", index=False)

print("Train and Test datasets saved successfully!")