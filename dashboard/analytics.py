import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dashboard_utils import load_json, section_card


def show():
    st.markdown("<div class='page-title'>📈 Analytics</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Interactive performance charts and model comparison insights.</div>", unsafe_allow_html=True)

    metrics = load_json("models/metrics.json")
    training_info = load_json("models/training_info.json")

    if not metrics:
        st.warning("Model metrics not available. Run src/train.py to generate metrics.json.")
        return

    accuracy = metrics.get("Accuracy", 0)
    precision = metrics.get("Precision", 0)
    recall = metrics.get("Recall", 0)
    f1 = metrics.get("F1 Score", 0)

    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4, gap='large')
    c1.metric("Accuracy", f"{accuracy:.2%}")
    c2.metric("Precision", f"{precision:.2%}")
    c3.metric("Recall", f"{recall:.2%}")
    c4.metric("F1 Score", f"{f1:.2%}")

    st.markdown("---")
    st.subheader("📊 Metric Comparison")
    metrics_df = {
        "Metric": ["Accuracy", "Precision", "Recall", "F1 Score"],
        "Score": [accuracy * 100, precision * 100, recall * 100, f1 * 100],
    }

    fig_metrics = px.bar(
        metrics_df,
        x="Metric",
        y="Score",
        color="Metric",
        text="Score",
        title="Model Evaluation Metrics",
        template="plotly_dark",
    )
    fig_metrics.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    fig_metrics.update_layout(yaxis=dict(range=[0, 100]), height=420, showlegend=False)
    st.plotly_chart(fig_metrics, use_container_width=True)

    st.markdown("---")
    st.subheader("🧠 Confusion Matrix")

    if metrics.get("confusion_matrix"):
        cm = metrics["confusion_matrix"]
        fig_cm = go.Figure(
            data=go.Heatmap(
                z=cm,
                x=["Predicted: No", "Predicted: Yes"],
                y=["Actual: No", "Actual: Yes"],
                colorscale="Blues",
                showscale=True,
            )
        )
        fig_cm.update_layout(title="Confusion Matrix", template="plotly_dark", height=420)
        st.plotly_chart(fig_cm, use_container_width=True)
    else:
        st.info("Confusion matrix is not available in metrics.json.")

    st.markdown("---")
    st.subheader("🌟 Model Comparison")
    section_card(
        """
        <p>Use overall metric trends to compare model performance and assess stability across dataset splits.</p>
        """
    )

    if training_info.get("feature_importance"):
        fig_importance = px.bar(
            x=list(training_info["feature_importance"].keys()),
            y=list(training_info["feature_importance"].values()),
            title="Feature Importance",
            template="plotly_dark",
        )
        fig_importance.update_layout(xaxis_title="Feature", yaxis_title="Importance", height=420)
        st.plotly_chart(fig_importance, use_container_width=True)
    else:
        st.info("Feature importance not available. Generate and store it in training_info.json.")

    if os.path.exists("monitoring/logs.csv"):
        log_df = pd.read_csv("monitoring/logs.csv")
        hist_fig = px.histogram(
            log_df,
            x="prediction",
            title="Prediction Distribution",
            template="plotly_dark",
        )
        hist_fig.update_layout(height=420)
        st.plotly_chart(hist_fig, use_container_width=True)
    else:
        st.info("Prediction distribution chart will appear once monitoring logs are created.")