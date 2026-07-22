import pandas as pd
import joblib
import mlflow
import mlflow.sklearn

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import cross_val_score

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

# ==========================================
# Load Dataset
# ==========================================

train = pd.read_csv("data/processed/train.csv")
test = pd.read_csv("data/processed/test.csv")

X_train = train.drop(columns=["decision"])
y_train = train["decision"]

X_test = test.drop(columns=["decision"])
y_test = test["decision"]

# ==========================================
# Base Model
# ==========================================

rf = RandomForestClassifier(
    random_state=42,
    n_jobs=-1
)

# ==========================================
# Hyperparameter Grid
# ==========================================

param_grid = {
    "n_estimators": [50, 100],
    "max_depth": [10, 20, None],
    "min_samples_split": [2, 5],
}

# ==========================================
# Grid Search
# ==========================================

grid = GridSearchCV(
    estimator=rf,
    param_grid=param_grid,
    cv=5,
    scoring="accuracy",
    n_jobs=-1
)

print("Running Grid Search...")

grid.fit(X_train, y_train)

print("\nGrid Search Completed!")

print("\nBest Parameters:")
print(grid.best_params_)

print("\nBest Cross Validation Accuracy:")
print(grid.best_score_)

# ==========================================
# Best Model
# ==========================================

best_model = grid.best_estimator_

# ==========================================
# Test Evaluation
# ==========================================

predictions = best_model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)
precision = precision_score(
    y_test,
    predictions,
    average="weighted"
)
recall = recall_score(
    y_test,
    predictions,
    average="weighted"
)
f1 = f1_score(
    y_test,
    predictions,
    average="weighted"
)

print("\nTest Results")
print("=" * 40)
print("Accuracy :", accuracy)
print("Precision:", precision)
print("Recall   :", recall)
print("F1 Score :", f1)

# ==========================================
# Cross Validation
# ==========================================

scores = cross_val_score(
    best_model,
    X_train,
    y_train,
    cv=5
)

print("\nCross Validation Scores")
print(scores)

print("\nAverage CV Accuracy")
print(scores.mean())

# ==========================================
# MLflow Logging
# ==========================================

mlflow.set_experiment("AI_Shopping_Planner_Tuning")

with mlflow.start_run(run_name="RandomForest_Tuned"):

    mlflow.log_params(grid.best_params_)

    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)
    mlflow.log_metric("f1_score", f1)
    mlflow.log_metric("cv_accuracy", scores.mean())

# ==========================================
# Save Tuned Model
# ==========================================

joblib.dump(
    best_model,
    "models/tuned_random_forest.pkl"
)

print("\nTuned Model Saved Successfully!")