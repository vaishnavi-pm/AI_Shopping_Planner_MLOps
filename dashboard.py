import streamlit as st
from dashboard import shopping
from dashboard.model_performance import show as show_model_performance
from dashboard.analytics import show as show_analytics
from dashboard.about import show as show_about
from dashboard_utils import apply_dark_theme


def sidebar_menu():
    st.sidebar.markdown(
        """
        <div style='padding: 12px 10px 18px; margin-bottom: 12px; border-bottom: 1px solid #262626;'>
            <div style='color:#fff;font-size:12px;letter-spacing:1px;font-weight:700'>AI / SHOPPING PLANNER</div>
            <p style='color:#737373;margin:5px 0 0;font-size:11px'>Smarter shopping. Powered by intelligence.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.sidebar.radio(
        "WORKSPACE",
        [
            "Overview",
            "Discover",
            "AI Planner",
            "Recommendations",
            "Compare",
            "Wishlist",
            "Price Tracker",
            "ML Intelligence",
            "Data Pipeline",
            "Experiments",
            "Model Registry",
            "Monitoring",
            "Retraining",
            "Activity",
            "Settings",
            "Model Performance",
            "Analytics",
            "About",
        ],
        key="navigation",
        label_visibility="collapsed",
    )

    st.sidebar.markdown(
        """
        <div style='color:#a3a3a3; padding: 12px 0 6px;border-top:1px solid #262626;margin-top:14px'>
            <small><span style='color:#22c55e'>●</span> All systems operational</small>
            <div style='margin-top:16px;color:#e5e5e5'>Demo workspace</div>
            <small>Local model · Indian catalog</small>
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
    header, search, status = st.columns([1.2, 4, 1.3], vertical_alignment="center")
    with header:
        st.markdown(f"**{page}**")
    with search:
        with st.form("global_search_form"):
            query_col, button_col = st.columns([8, 1])
            with query_col:
                query = st.text_input(
                    "Global search",
                    placeholder="Search products, categories, or ask AI...",
                    label_visibility="collapsed",
                    key="global_search_query",
                )
            with button_col:
                search_submitted = st.form_submit_button("Search", use_container_width=True)
        if search_submitted:
            st.session_state["discover_query"] = query
            st.session_state["navigation"] = "Discover"
            st.rerun()
    with status:
        st.markdown("<div style='text-align:right;color:#a3a3a3;font-size:12px'>● LOCAL SYSTEMS OK</div>", unsafe_allow_html=True)

    if page == "Overview":
        shopping.show_overview()
    elif page == "Discover":
        shopping.show_discover()
    elif page == "AI Planner":
        shopping.show_planner()
    elif page == "Recommendations":
        shopping.show_recommendations()
    elif page == "Compare":
        shopping.show_compare()
    elif page == "Wishlist":
        shopping.show_wishlist()
    elif page == "Price Tracker":
        shopping.show_price_tracker()
    elif page == "ML Intelligence":
        shopping.show_ml_intelligence()
    elif page == "Data Pipeline":
        shopping.show_dataset()
    elif page == "Experiments":
        shopping.show_experiments()
    elif page == "Model Registry":
        shopping.show_registry()
    elif page == "Monitoring":
        shopping.show_monitoring()
    elif page == "Retraining":
        shopping.show_retraining()
    elif page == "Activity":
        shopping.show_activity()
    elif page == "Settings":
        shopping.show_settings()
    elif page == "Model Performance":
        show_model_performance()
    elif page == "Analytics":
        show_analytics()
    elif page == "About":
        show_about()


if __name__ == "__main__":
    main()