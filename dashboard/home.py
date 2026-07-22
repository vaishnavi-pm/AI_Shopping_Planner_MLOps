import streamlit as st
from dashboard_utils import metric_card, tech_card, section_card


def show():
    st.markdown("<div class='page-title'>🛒 AI Shopping Planner</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>End-to-End MLOps Pipeline for Product Recommendation and Monitoring</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-banner'><strong>Project Status:</strong> <span style='color:#8bf38b;'>Running</span> · <strong>Deployment:</strong> Streamlit + FastAPI · <strong>Tracking:</strong> MLflow</div>", unsafe_allow_html=True)

    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4, gap='large')
    with col1:
        metric_card("Dataset Size", "267,970 rows", "Processed training records")
    with col2:
        metric_card("Best Model", "Random Forest", "Selected by accuracy")
    with col3:
        metric_card("Accuracy", "99.9%", "Weighted evaluation")
    with col4:
        metric_card("System Status", "Operational", "Live monitoring enabled")

    st.markdown("---")

    section_card(
        """
        <h3 style='margin-bottom: 0.5rem;'>Project Overview</h3>
        <p>The AI Shopping Planner is an end-to-end MLOps portfolio project built to support real-time shopping decision prediction.
        It includes preprocessing, model training, feature tracking, deployment, prediction monitoring, and retraining workflows.</p>
        """
    )

    st.subheader("Modern MLOps Workflow")
    st.info(
        """
        <b>Data Ingestion</b> → <b>Feature Engineering</b> → <b>Model Training</b> → <b>Evaluation</b> → <b>MLflow Tracking</b> → <b>Deployment</b> → <b>Monitoring</b> → <b>Retraining</b>
        """,
        icon="ℹ️",
    )

    st.markdown("---")

    st.subheader("Technology Stack")
    tech_cols = st.columns(3, gap='large')
    tech_items = [
        ("Python", "Primary development language for data processing, modelling and backend."),
        ("Scikit-learn", "Core library for model training and evaluation."),
        ("MLflow", "Experiment tracking, model registry, and metric logging."),
        ("FastAPI", "Deployment API for real-time inference and integration."),
        ("Streamlit", "Frontend dashboard for interactive monitoring and predictions."),
        ("Pandas", "Data transformation, profiling, and dataset management."),
        ("Joblib", "Model serialization and persistence."),
        ("Plotly", "Interactive analytics and chart rendering."),
    ]

    for index, tech in enumerate(tech_items):
        with tech_cols[index % 3]:
            tech_card(tech[0], tech[1])

    st.markdown("---")
    section_card(
        """
        <h3 style='margin-bottom: 0.5rem;'>Dashboard Summary</h3>
        <p>This dashboard provides a polished enterprise-style view of the AI Shopping Planner project.
        Access dataset quality, model performance, analytics, prediction workflows, monitoring trends, and retraining controls from a single interface.</p>
        """
    )
