import os

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard_utils import format_number, load_dataframe, metric_card, section_card


def show():
    st.markdown("<div class='page-title'>📊 Dataset Overview</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Explore dataset quality, structure, and feature distributions.</div>", unsafe_allow_html=True)

    DATA_PATH = "data/processed/train.csv"
    df = load_dataframe(DATA_PATH)

    if df.empty:
        st.error(f"Dataset not found: {DATA_PATH}")
        st.info("Please ensure data/processed/train.csv exists and contains the processed dataset.")
        return

    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4, gap='large')
    with c1:
        metric_card("Total Rows", format_number(df.shape[0]), "Processed training rows")
    with c2:
        metric_card("Total Columns", format_number(df.shape[1]), "Feature count")
    with c3:
        metric_card("Missing Values", format_number(df.isnull().sum().sum()), "Across all columns")
    with c4:
        metric_card("Duplicate Rows", format_number(df.duplicated().sum()), "Data quality check")

    st.markdown("---")
    st.subheader("📋 Dataset Preview")
    st.dataframe(df.head(10), use_container_width=True)

    st.markdown("---")
    st.subheader("📌 Column Information")
    info_df = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str),
        "Missing": df.isnull().sum().values,
    })
    st.dataframe(info_df, use_container_width=True)

    st.markdown("---")
    st.subheader("🧠 Statistical Summary")
    st.dataframe(df.describe(include='all').transpose(), use_container_width=True)

    st.markdown("---")
    st.subheader("📊 Missing Values and Correlation")
    col1, col2 = st.columns(2, gap='large')

    with col1:
        missing = df.isnull().sum().reset_index()
        missing.columns = ["Feature", "Missing Values"]
        fig_missing = px.bar(
            missing,
            x="Feature",
            y="Missing Values",
            title="Missing Values by Feature",
            color="Missing Values",
            template="plotly_dark",
        )
        fig_missing.update_layout(height=420, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_missing, use_container_width=True)

    with col2:
        numeric_df = df.select_dtypes(include=["number"])
        corr = numeric_df.corr()
        fig_corr = px.imshow(
            corr,
            text_auto=True,
            title="Correlation Heatmap",
            color_continuous_scale="Aggrnyl",
            template="plotly_dark",
        )
        fig_corr.update_layout(height=420, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_corr, use_container_width=True)

    st.markdown("---")
    section_card(
        """
        <h3 style='margin-bottom: 0.5rem;'>Feature Summary</h3>
        <p>The dataset covers purchase decision behavior for over 267,000 shopping records.
        Use the dataset insights to validate model inputs and detect potential drift.</p>
        """
    )
