import streamlit as st
from dashboard.home import show as show_home
from dashboard.dataset import show as show_dataset
from dashboard.model_performance import show as show_model_performance
from dashboard.analytics import show as show_analytics
from dashboard.prediction import show as show_prediction
from dashboard.monitoring import show as show_monitoring
from dashboard.retraining import show as show_retraining
from dashboard.about import show as show_about
from dashboard_utils import apply_dark_theme


def sidebar_menu():
    st.sidebar.markdown(
        """
        <div style='padding: 22px 18px; margin-bottom: 18px; border-radius: 18px; background: linear-gradient(135deg,#1f3160,#0f1932); text-align:center;'>
            <h2 style='color:#ffffff; margin:0;'>🛒 AI Shopping Planner</h2>
            <p style='color:#a6b4d8; margin:4px 0 0;'>End-to-End MLOps Portfolio Dashboard</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Home",
            "📊 Dataset",
            "🤖 Model Performance",
            "📈 Analytics",
            "🔮 Prediction",
            "📋 Monitoring",
            "♻ Retraining",
            "ℹ About",
        ],
        index=0,
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style='color:#9bb1d2; padding: 12px 0;'>
            <small>Track dataset quality, model metrics, predictions, monitoring, and retraining in one unified dashboard.</small>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return page


def main():
    st.set_page_config(
        page_title="AI Shopping Planner",
        page_icon="🛒",
        layout="wide",
    )

    apply_dark_theme()

    page = sidebar_menu()

    if page == "🏠 Home":
        show_home()
    elif page == "📊 Dataset":
        show_dataset()
    elif page == "🤖 Model Performance":
        show_model_performance()
    elif page == "📈 Analytics":
        show_analytics()
    elif page == "🔮 Prediction":
        show_prediction()
    elif page == "📋 Monitoring":
        show_monitoring()
    elif page == "♻ Retraining":
        show_retraining()
    elif page == "ℹ About":
        show_about()


if __name__ == "__main__":
    main()