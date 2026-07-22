import streamlit as st
from dashboard_utils import section_card


def show():
    st.markdown("<div class='page-title'>ℹ️ About</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Understand the AI Shopping Planner project, architecture, and developer details.</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.write(
        "The AI Shopping Planner is an end-to-end MLOps portfolio project designed to predict shopper decisions. "
        "It spans data preparation, model training, tracking, deployment, prediction monitoring, and automated retraining."
    )

    st.markdown("---")
    st.subheader("Project Objective")
    st.write(
        "Create a production-ready analytics dashboard that makes machine learning decisions interpretable, "
        "monitored, and easy to retrain for evolving shopping behavior."
    )

    st.markdown("---")
    st.subheader("Architecture")
    st.write(
        "Data is processed and loaded from the training pipeline, models are trained and tracked with MLflow, "
        "predictions are exposed through Streamlit, and monitoring logs drive retraining decisions."
    )

    st.markdown("---")
    st.subheader("Technologies Used")
    st.markdown(
        "- Python 3.11\n"
        "- Pandas\n"
        "- Scikit-learn\n"
        "- MLflow\n"
        "- FastAPI\n"
        "- Streamlit\n"
        "- Joblib\n"
        "- Plotly"
    )

    st.markdown("---")
    section_card(
        """
        <h3 style='margin-bottom: 0.5rem;'>Developer Information</h3>
        <p>Built as an academic MLOps showcase and portfolio dashboard with strong emphasis on modern UI, data-driven insights, and production-aware workflows.</p>
        """
    )
