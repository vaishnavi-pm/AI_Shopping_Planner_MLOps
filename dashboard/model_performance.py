import json
import os
import joblib
import streamlit as st
from dashboard_utils import load_json, format_number, metric_card, section_card


def show():
    st.markdown("<div class='page-title'>🤖 Model Performance</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Review training metrics, model details, and production readiness.</div>", unsafe_allow_html=True)

    metrics = load_json("models/metrics.json")
    training_info = load_json("models/training_info.json")
    model_name = None
    if os.path.exists("models/model_name.pkl"):
        model_name = joblib.load("models/model_name.pkl")

    model_path = "models/best_model.pkl"
    model_exists = os.path.exists(model_path)

    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4, gap='large')
    c1.markdown(metric_card("Best Model", model_name or "Unknown", "Primary selected model"), unsafe_allow_html=True)
    c2.markdown(metric_card("Accuracy", f"{metrics.get('Accuracy', 'N/A'):.2%}" if metrics.get('Accuracy') is not None else "N/A", "Evaluation on holdout set"), unsafe_allow_html=True)
    c3.markdown(metric_card("Precision", f"{metrics.get('Precision', 'N/A'):.2%}" if metrics.get('Precision') is not None else "N/A", "Weighted average"), unsafe_allow_html=True)
    c4.markdown(metric_card("F1 Score", f"{metrics.get('F1 Score', 'N/A'):.2%}" if metrics.get('F1 Score') is not None else "N/A", "Model balance metric"), unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📌 Training Summary")

    info_cols = st.columns(4, gap='large')
    info_cols[0].metric("Training Samples", format_number(training_info.get("training_samples", "N/A")))
    info_cols[1].metric("Testing Samples", format_number(training_info.get("testing_samples", "N/A")))
    info_cols[2].metric("Training Date", training_info.get("training_date", "N/A"))
    info_cols[3].metric("Model File", os.path.basename(model_path) if model_exists else "Missing")

    st.markdown("---")
    st.subheader("🧠 Model Details")

    if model_exists:
        model = joblib.load(model_path)
        st.write("**Model Type:**", type(model).__name__)

        properties = []
        if hasattr(model, "n_estimators"):
            properties.append(f"Number of Trees: {model.n_estimators}")
        if hasattr(model, "max_depth"):
            properties.append(f"Max Depth: {model.max_depth}")
        if hasattr(model, "random_state"):
            properties.append(f"Random State: {model.random_state}")
        if hasattr(model, "classes_"):
            properties.append(f"Target Classes: {len(model.classes_)}")

        for row in properties:
            st.write(f"- {row}")

        if os.path.exists("models/feature_names.json"):
            feature_names = load_json("models/feature_names.json")
            if isinstance(feature_names, list):
                st.write(f"- Feature Count: {len(feature_names)}")
    else:
        st.error("Best model file not found. Run training to generate model artifacts.")

    st.markdown("---")
    section_card(
        """
        <h3 style='margin-bottom: 0.5rem;'>Model Lifecycle Insights</h3>
        <p>Use the evaluation metrics and detailed model summary to validate production readiness and support retraining decisions.</p>
        """
    )
