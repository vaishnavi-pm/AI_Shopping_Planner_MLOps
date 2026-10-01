import os
import joblib
import streamlit as st

from dashboard_utils import (
    load_json,
    metric_card,
    section_card,
    format_number,
)


def show():

    st.markdown(
        "<div class='page-title'>🤖 AI Planner Performance</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='page-subtitle'>Evaluate the AI Shopping Planner and its deployment readiness.</div>",
        unsafe_allow_html=True,
    )

    metrics = load_json("models/metrics.json")
    training_info = load_json("models/training_info.json")

    model_name = "AI Shopping Planner"

    if os.path.exists("models/model_name.pkl"):
        model_name = joblib.load("models/model_name.pkl")

    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Recommendation Engine",
            model_name,
            "Active Model",
        )

    with c2:
        metric_card(
            "Recommendation Accuracy",
            f"{metrics.get('Accuracy',0):.2%}",
            "Prediction Quality",
        )

    with c3:
        metric_card(
            "Products",
            format_number(training_info.get("dataset_size", 267970)),
            "Amazon Dataset",
        )

    with c4:
        metric_card(
            "Deployment",
            "Ready",
            "Production Status",
        )

    st.markdown("---")

    st.subheader("📊 Dataset Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Training Samples",
            format_number(
                training_info.get(
                    "training_samples",
                    "N/A",
                )
            ),
        )

    with col2:
        st.metric(
            "Testing Samples",
            format_number(
                training_info.get(
                    "testing_samples",
                    "N/A",
                )
            ),
        )

    with col3:
        st.metric(
            "Training Date",
            training_info.get(
                "training_date",
                "N/A",
            ),
        )

    st.markdown("---")

    st.subheader("🛒 Shopping Planner Features")

    feature_col1, feature_col2 = st.columns(2)

    with feature_col1:

        st.success("✔ Budget-based Planning")

        st.success("✔ Purpose Filtering")

        st.success("✔ Priority Matching")

        st.success("✔ Product Ranking")

        st.success("✔ Buy Now Decision")

    with feature_col2:

        st.success("✔ Wait Recommendation")

        st.success("✔ Avoid Recommendation")

        st.success("✔ Remaining Budget")

        st.success("✔ AI Shopping Summary")

        st.success("✔ Monitoring Logs")

    st.markdown("---")

    st.subheader("⚙ Recommendation Engine")

    st.write("**Model Name:**", model_name)

    st.write("**Recommendation Type:** Budget-aware Product Recommendation")

    st.write("**Input Features:**")

    st.write("- Budget")

    st.write("- Purpose")

    st.write("- Priority")

    st.write("- Family Size")

    st.write("**Outputs:**")

    st.write("- Buy Now")

    st.write("- Wait")

    st.write("- Avoid")

    st.write("- Total Cost")

    st.write("- Remaining Budget")

    st.write("- AI Shopping Summary")

    st.markdown("---")

    st.subheader("🚀 MLOps Pipeline")

    st.info(
        """
Data Collection

↓

Data Preprocessing

↓

Feature Engineering

↓

Model Training

↓

Evaluation

↓

MLflow Tracking

↓

Deployment

↓

Prediction

↓

Monitoring

↓

Retraining
"""
    )

    st.markdown("---")

    section_card(
        """
        <h3>Production Readiness</h3>

        <p>

        The AI Shopping Planner has been developed using an
        end-to-end MLOps workflow.

        The recommendation engine supports intelligent
        shopping decisions based on budget, purpose,
        priority, and family size.

        Every prediction is logged for monitoring,
        enabling future retraining and continuous
        model improvement.

        </p>
        """
    )