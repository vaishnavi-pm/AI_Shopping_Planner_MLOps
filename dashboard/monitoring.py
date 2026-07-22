import os

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard_utils import section_card, load_dataframe


def show():
    st.markdown("<div class='page-title'>📋 Monitoring</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Track prediction health, success rate, and recent production outputs.</div>", unsafe_allow_html=True)

    log_path = "monitoring/logs.csv"
    df = load_dataframe(log_path)

    if df.empty:
        st.warning("No prediction logs found.")
        st.info("Run a prediction to generate monitoring data.")
        return

    st.markdown("---")
    total_predictions = len(df)
    success_count = len(df[df["status"].astype(str).str.lower() == "success"])
    failure_count = total_predictions - success_count

    c1, c2, c3 = st.columns(3, gap='large')
    c1.metric("Total Predictions", total_predictions)
    c2.metric("Successful", success_count)
    c3.metric("Failed", failure_count)

    st.markdown("---")
    st.subheader("📈 Prediction Distribution")
    fig_dist = px.histogram(
        df,
        x="prediction",
        color="status" if "status" in df.columns else None,
        title="Predictions by Outcome",
        template="plotly_dark",
    )
    fig_dist.update_layout(height=420)
    st.plotly_chart(fig_dist, use_container_width=True)

    st.markdown("---")
    st.subheader("Recent Predictions")
    st.dataframe(df.tail(12), use_container_width=True)

    st.markdown("---")
    section_card(
        """
        <p>This monitoring panel gives a real-time summary of prediction volume, outcomes, and the latest model outputs.
        Use these signals to trigger retraining or investigate drift.</p>
        """
    )
