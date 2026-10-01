import streamlit as st
from dashboard_utils import metric_card, tech_card, section_card


def show():
    st.markdown(
        "<div class='page-title'>🛒 AI Shopping Planner</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='page-subtitle'>End-to-End AI Shopping Planner with MLOps Pipeline</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        
        """
        <div class='section-banner'>
        <strong>Project Status:</strong>
        <span style='color:#7CFC00;'>● Running</span>
        &nbsp;&nbsp;&nbsp;
        <strong>Deployment:</strong> Streamlit + FastAPI
        &nbsp;&nbsp;&nbsp;
        <strong>Tracking:</strong> MLflow
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card(
            "Products",
            "267,970",
            "Amazon Product Dataset",
        )

    with col2:
        metric_card(
            "Planner",
            "AI Ready",
            "Budget Recommendation Engine",
        )

    with col3:
        metric_card(
            "Deployment",
            "Online",
            "FastAPI + Streamlit",
        )

    with col4:
        metric_card(
            "Monitoring",
            "Active",
            "Prediction Logging Enabled",
        )

    st.markdown("---")

    section_card(
        """
        <h3>Project Overview</h3>

        <p>

        AI Shopping Planner is an intelligent recommendation system
        that helps users purchase products according to their

        ✔ Budget

        ✔ Purpose

        ✔ Priority

        ✔ Family Size

        Instead of recommending random products,
        the planner generates a personalized shopping list
        and categorizes every product as

        <b>Buy Now</b>,
        <b>Wait</b>,
        or
        <b>Avoid</b>.

        It also calculates

        • Total Cost

        • Remaining Budget

        • AI Shopping Summary

        • Monitoring Logs

        </p>
        """
    )

    st.markdown("---")

    st.subheader("AI Shopping Planner Workflow")

    st.success(
        """
Budget

↓

Purpose

↓

Priority

↓

Family Size

↓

Product Filtering

↓

AI Recommendation Engine

↓

Buy Now / Wait / Avoid

↓

Shopping Summary

↓

Monitoring

↓

Auto Retraining
"""
    )

    st.markdown("---")

    st.subheader("Technology Stack")

    tech_cols = st.columns(3)

    technologies = [

        (
            "Python",
            "Core programming language used for the project.",
        ),

        (
            "Pandas",
            "Data preprocessing and product filtering.",
        ),

        (
            "Scikit-learn",
            "Machine Learning model training and evaluation.",
        ),

        (
            "MLflow",
            "Experiment tracking and model versioning.",
        ),

        (
            "FastAPI",
            "REST API deployment for predictions.",
        ),

        (
            "Streamlit",
            "Interactive dashboard interface.",
        ),

        (
            "Joblib",
            "Model saving and loading.",
        ),

        (
            "Plotly",
            "Interactive visualizations and analytics.",
        ),

        (
            "GitHub",
            "Version control and collaboration.",
        ),
    ]

    for index, tech in enumerate(technologies):
        with tech_cols[index % 3]:
            tech_card(
                tech[0],
                tech[1],
            )

    st.markdown("---")

    section_card(
        """
        <h3>Key Features</h3>

        <ul>

        <li>💰 Budget-based Shopping Planner</li>

        <li>🏠 Purpose-wise Product Recommendation</li>

        <li>⭐ Priority-based Product Selection</li>

        <li>👨‍👩‍👧 Family Size Support</li>

        <li>🛍 Buy Now / Wait / Avoid Decision</li>

        <li>📊 Total Cost & Remaining Budget</li>

        <li>🤖 AI Shopping Summary</li>

        <li>📈 Prediction Monitoring</li>

        <li>🔄 MLflow Tracking</li>

        <li>♻ Auto Retraining Ready</li>

        </ul>
        """
    )

    st.markdown("---")

    section_card(
        """
        <h3>Dashboard Modules</h3>

        <p>

        📂 Home

        <br>

        🛒 AI Shopping Planner

        <br>

        📊 Analytics

        <br>

        📈 Monitoring

        <br>

        🔄 Retraining

        <br>

        ⚙ MLflow Experiments

        </p>
        """
    )