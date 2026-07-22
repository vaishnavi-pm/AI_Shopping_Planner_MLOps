import json
import joblib
import os
from datetime import datetime

import mlflow
import mlflow.sklearn
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

# ==========================================
# Load Data
# ==========================================

print("=" * 60)
print("Loading Dataset...")
print("=" * 60)

train = pd.read_csv("data/processed/train.csv")
test = pd.read_csv("data/processed/test.csv")

X_train = train.drop(columns=["decision"])
y_train = train["decision"]

X_test = test.drop(columns=["decision"])
y_test = test["decision"]

print("Training Samples :", X_train.shape[0])
print("Testing Samples  :", X_test.shape[0])

# ==========================================
# Models
# ==========================================

models = {
    "Random Forest": RandomForestClassifier(
        n_estimators=50,
        random_state=42,
        n_jobs=-1
    ),

    "Decision Tree": DecisionTreeClassifier(
        random_state=42
    ),

    "KNN": KNeighborsClassifier(
        n_neighbors=5
    )
}

# ==========================================
# MLflow
# ==========================================

mlflow.set_experiment("AI_Shopping_Planner")

best_model = None
best_accuracy = 0
best_model_name = ""

# ==========================================
# Train Models
# ==========================================

for name, model in models.items():

    with mlflow.start_run(run_name=name):

        print("\n" + "=" * 60)
        print("Training :", name)
        print("=" * 60)

        # -----------------------------
        # Train
        # -----------------------------
        model.fit(X_train, y_train)

        # -----------------------------
        # Predict
        # -----------------------------
        y_pred = model.predict(X_test)

        # -----------------------------
        # Metrics
        # -----------------------------
        accuracy = accuracy_score(y_test, y_pred)

        precision = precision_score(
            y_test,
            y_pred,
            average="weighted"
        )

        recall = recall_score(
            y_test,
            y_pred,
            average="weighted"
        )

        f1 = f1_score(
            y_test,
            y_pred,
            average="weighted"
        )

        cm = confusion_matrix(y_test, y_pred)

        report = classification_report(y_test, y_pred)

        # -----------------------------
        # Print Results
        # -----------------------------
        print(f"Accuracy  : {accuracy:.4f}")
        print(f"Precision : {precision:.4f}")
        print(f"Recall    : {recall:.4f}")
        print(f"F1 Score  : {f1:.4f}")

        print("\nConfusion Matrix")
        print(cm)

        print("\nClassification Report")
        print(report)

        # -----------------------------
        # MLflow Parameters
        # -----------------------------
        mlflow.log_param("Model", name)

        if name == "Random Forest":
            mlflow.log_param("n_estimators", 50)
            mlflow.log_param("random_state", 42)

        elif name == "Decision Tree":
            mlflow.log_param("random_state", 42)

        elif name == "KNN":
            mlflow.log_param("n_neighbors", 5)

        # -----------------------------
        # MLflow Metrics
        # -----------------------------
        mlflow.log_metric("Accuracy", accuracy)
        mlflow.log_metric("Precision", precision)
        mlflow.log_metric("Recall", recall)
        mlflow.log_metric("F1 Score", f1)

        # -----------------------------
        # Log Model
        # -----------------------------
        try:
            mlflow.sklearn.log_model(
                sk_model=model,
                name="model"
            )
            print("\nModel logged successfully to MLflow.")

        except Exception as e:
            print("\nMLflow Model Logging Skipped")
            print(e)

        # -----------------------------
        # Save Best Model
        # -----------------------------
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_precision = precision
            best_recall = recall
            best_f1 = f1
            best_confusion_matrix = cm.tolist()
            best_model = model
            best_model_name = name

# ==========================================
# Save Best Model and Artifacts
# ==========================================

os.makedirs("models", exist_ok=True)
joblib.dump(best_model, "models/best_model.pkl")
joblib.dump(best_model_name, "models/model_name.pkl")

feature_names = list(X_train.columns)
metrics_data = {
    "Model": best_model_name,
    "Accuracy": best_accuracy,
    "Precision": best_precision,
    "Recall": best_recall,
    "F1 Score": best_f1,
    "confusion_matrix": best_confusion_matrix,
}
training_info = {
    "model_name": best_model_name,
    "training_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "training_samples": X_train.shape[0],
    "testing_samples": X_test.shape[0],
    "feature_names": feature_names,
}

with open("models/metrics.json", "w", encoding="utf-8") as file:
    json.dump(metrics_data, file, indent=2)

with open("models/feature_names.json", "w", encoding="utf-8") as file:
    json.dump(feature_names, file, indent=2)

with open("models/training_info.json", "w", encoding="utf-8") as file:
    json.dump(training_info, file, indent=2)

# ==========================================
# Final Output
# ==========================================

print("\n" + "=" * 60)
print("TRAINING COMPLETED")
print("=" * 60)

print(f"Best Model    : {best_model_name}")
print(f"Best Accuracy : {best_accuracy:.4f}")

print("\nFiles Saved")

print("✔ models/best_model.pkl")
print("✔ models/model_name.pkl")
print("✔ models/metrics.json")
print("✔ models/feature_names.json")
print("✔ models/training_info.json")

print("=" * 60)