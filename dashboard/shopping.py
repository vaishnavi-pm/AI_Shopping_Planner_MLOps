import html
import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.catalog import (
    filter_products,
    get_categories,
    load_catalog,
    rank_products,
    select_within_budget,
)
from dashboard_utils import format_number, load_json


PROJECT_ROOT = Path(__file__).resolve().parents[1]
METRICS_PATH = PROJECT_ROOT / "models" / "metrics.json"
TRAINING_PATH = PROJECT_ROOT / "models" / "training_info.json"
LOG_PATH = PROJECT_ROOT / "monitoring" / "logs.csv"
STOP_WORDS = {
    "a", "an", "and", "for", "find", "good", "i", "in", "me", "my", "need",
    "of", "the", "to", "under", "with", "within", "below", "less", "than",
    "best", "buy", "looking", "want", "please", "recommend", "recommendation",
}


def _money(value):
    return f"₹{float(value):,.0f}"


def _key(product_id):
    return str(abs(hash(str(product_id))))


def _product(product_id):
    products = load_catalog()
    matches = products[products["product_id"] == product_id]
    return None if matches.empty else matches.iloc[0]


def _session_list(name):
    if name not in st.session_state:
        st.session_state[name] = []
    return st.session_state[name]


def _add_to_list(name, product_id):
    items = _session_list(name)
    if name == "compare_ids" and len(items) >= 3 and product_id not in items:
        st.warning("Compare up to three products at a time.")
        return
    if product_id not in items:
        items.append(product_id)


def _safe_url(value):
    value = str(value or "")
    return value if value.startswith("https://") else ""


def _render_product_card(row, score_label="Preference match"):
    product_id = row["product_id"]
    image_url = _safe_url(row.get("image", ""))
    image = (
        f'<img src="{html.escape(image_url, quote=True)}" alt="" loading="lazy" '
        'onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'grid\'">'
        '<div class="product-no-image" style="display:none">IMAGE UNAVAILABLE</div>'
        if image_url
        else '<div class="product-no-image">PRODUCT</div>'
    )
    title = html.escape(str(row["name"]))
    category = html.escape(str(row["sub_category"]))
    brand = html.escape(str(row["brand"]))
    rating = float(row["ratings"] or 0)
    current_price = _money(row["discount_price"])
    actual_price = _money(row["actual_price"])
    discount = max(0, float(row["discount_percentage"] or 0))
    score = float(row.get("match_score", 0))

    st.markdown(
        f"""
        <style>
        .product-card {{ min-height: 178px; display: grid; grid-template-columns: 126px 1fr; gap: 18px;
            padding: 16px; border: 1px solid #292929; border-radius: 7px; background: #111; }}
        .product-card img {{ width: 126px; height: 146px; object-fit: contain; background: #fff; border-radius: 4px; }}
        .product-no-image {{ width: 126px; height: 146px; display:grid; place-items:center; color:#777; background:#181818; }}
        .product-card .brand {{ color:#a3a3a3; font-size:11px; text-transform:uppercase; letter-spacing:1px; }}
        .product-card .name {{ color:#f5f5f5; font-size:14px; line-height:1.4; margin:6px 0 10px; height:40px; overflow:hidden; }}
        .product-card .category {{ color:#737373; font-size:12px; }}
        .product-card .price {{ color:#fff; font-size:21px; font-weight:650; margin-top:8px; }}
        .product-card .original {{ color:#737373; font-size:12px; text-decoration:line-through; margin-left:7px; }}
        .product-card .facts {{ color:#a3a3a3; font-size:12px; margin-top:4px; }}
        .product-card .match {{ color:#d4d4d4; font-size:11px; border:1px solid #383838; padding:3px 7px; border-radius:4px; float:right; }}
        @media(max-width:640px) {{ .product-card {{ grid-template-columns: 82px 1fr; gap:12px; padding:12px; }}
            .product-card img, .product-no-image {{ width:82px; height:112px; }} .product-card .price {{ font-size:18px; }} }}
        </style>
        <article class="product-card">
          {image}
          <div>
            <span class="brand">{brand}</span>
            <span class="match">{html.escape(score_label)} {score:.0f}%</span>
            <div class="name">{title}</div>
            <div class="category">{category}</div>
            <div class="price">{current_price}<span class="original">{actual_price}</span></div>
            <div class="facts">{rating:.1f} / 5 &nbsp; · &nbsp; {discount:.0f}% off</div>
          </div>
        </article>
        """,
        unsafe_allow_html=True,
    )
    actions = st.columns(3)
    link = _safe_url(row.get("link", ""))
    with actions[0]:
        if link:
            st.link_button("View listing", link, width="stretch")
    with actions[1]:
        if st.button("Add to compare", key=f"compare_{_key(product_id)}", width="stretch"):
            _add_to_list("compare_ids", product_id)
            st.toast("Added to comparison")
    with actions[2]:
        if st.button("Save", key=f"save_{_key(product_id)}", width="stretch"):
            _add_to_list("wishlist_ids", product_id)
            st.toast("Saved to wishlist")


def _render_product_grid(products, limit=8, score_label="Preference match"):
    if products.empty:
        st.info("No listings match those filters. Try a broader search or a higher budget.")
        return
    selected = products.head(limit)
    for start in range(0, len(selected), 2):
        columns = st.columns(2, gap="medium")
        for column, (_, row) in zip(columns, selected.iloc[start : start + 2].iterrows()):
            with column:
                _render_product_card(row, score_label)


def _meaningful_terms(query):
    text = re.sub(r"[₹,\d]", " ", query.casefold())
    return " ".join(word for word in re.findall(r"[a-z][a-z'-]+", text) if word not in STOP_WORDS)


def show_overview():
    products = load_catalog()
    metrics = load_json(str(METRICS_PATH))
    training = load_json(str(TRAINING_PATH))
    logs = pd.read_csv(LOG_PATH) if LOG_PATH.exists() else pd.DataFrame()
    accuracy = metrics.get("Accuracy")
    accuracy_text = f"{float(accuracy):.1%}" if accuracy is not None else "Not measured"

    st.markdown(
        """
        <div style="padding:10px 0 26px">
          <div style="font-size:13px;color:#a3a3a3;margin-bottom:9px">AI SHOPPING PLANNER <span style="color:#525252">/</span> OVERVIEW</div>
          <h1 style="font-size:42px;line-height:1.08;margin:0 0 8px">Good afternoon.</h1>
          <div style="color:#a3a3a3;font-size:16px">Your shopping intelligence is ready.</div>
        </div>
        <div style="padding:24px 26px;background:#f5f5f5;color:#080808;border-radius:7px;margin-bottom:22px">
          <div style="font-size:12px;letter-spacing:1px;color:#555">A MORE THOUGHTFUL WAY TO BUY</div>
          <div style="font-size:27px;font-weight:650;margin:10px 0 6px">Plan your next purchase with AI.</div>
          <div style="font-size:14px;color:#555">Describe what matters. Compare real listings against your budget.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    prompt_col, button_col = st.columns([5, 1], vertical_alignment="bottom")
    with prompt_col:
        st.text_input(
            "What are you looking for?",
            placeholder="Find headphones for commuting under ₹10,000",
            key="overview_query",
            label_visibility="collapsed",
        )
    with button_col:
        if st.button("Plan with AI →", key="overview_plan", width="stretch"):
            st.session_state["planner_initial_query"] = st.session_state.get("overview_query", "")
            st.session_state["navigation"] = "AI Planner"
            st.rerun()

    st.markdown("### Your workspace")
    columns = st.columns(4, gap="medium")
    columns[0].metric("Products analyzed", format_number(len(products)), "Processed Amazon catalog")
    columns[1].metric("Evaluation accuracy", accuracy_text, str(metrics.get("Model", "Local model")))
    columns[2].metric("Tracked products", len(_session_list("tracked_ids")), "This session")
    columns[3].metric("Planner requests", len(logs), "Recorded local predictions")

    st.markdown("### Picks from the catalog")
    ranked = rank_products(products, budget=80000).head(4)
    _render_product_grid(ranked, limit=4, score_label="Catalog score")

    st.markdown("### Intelligence pipeline")
    pipeline = ["Catalog", "Validation", "Feature engineering", "Ranking", "Monitoring", "Retraining"]
    st.markdown(
        "<div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,150px),1fr));gap:8px'>"
        + "".join(
            f"<div style='padding:13px 10px;border:1px solid #303030;background:{'#f5f5f5' if index == 0 else '#111'};color:{'#080808' if index == 0 else '#d4d4d4'};border-radius:5px;font-size:12px'>{step}</div>"
            for index, step in enumerate(pipeline)
        )
        + "</div>",
        unsafe_allow_html=True,
    )
    st.caption(
        f"Active model: {training.get('model_name', metrics.get('Model', 'Not registered'))} · "
        f"Personalization uses selected preferences and listing signals; individual behavior history is not collected."
    )


def show_discover():
    products = load_catalog()
    st.markdown("<div class='page-title'>Discover</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Search current listings from the processed Indian e-commerce catalog.</div>", unsafe_allow_html=True)
    if products.empty:
        st.error("The processed product catalog is unavailable.")
        return

    filters = st.columns([3, 2, 2, 1.5, 2])
    query = filters[0].text_input(
        "Search products",
        placeholder="Headphones, laptop, watch...",
        key="discover_query",
    )
    categories = ["All categories"] + get_categories(products)
    category = filters[1].selectbox("Category", categories)
    max_price = filters[2].number_input("Max price (₹)", min_value=0, value=100000, step=5000)
    rating_options = [0.0, 3.0, 3.5, 4.0, 4.5]
    rating_default = st.session_state.get("settings_min_rating", 3.5)
    rating_index = rating_options.index(rating_default) if rating_default in rating_options else 2
    min_rating = filters[3].selectbox("Rating", rating_options, index=rating_index)
    brands = ["All brands"] + products["brand"].value_counts().head(50).index.tolist()
    brand = filters[4].selectbox("Brand", brands)

    filtered = filter_products(products, query, category, max_price or None, min_rating, brand)
    ranked = rank_products(filtered, budget=max_price or None, query=_meaningful_terms(query))
    st.caption(f"{format_number(len(filtered))} listings · Ranked by rating, value, popularity, discount and budget fit")
    _render_product_grid(ranked, limit=12)


def show_recommendations():
    products = load_catalog()
    st.markdown("<div class='page-title'>Recommendations</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Ranked product matches with a transparent explanation of catalog signals.</div>", unsafe_allow_html=True)
    categories = ["All categories"] + get_categories(products)
    preferences = st.session_state.get("planner_preferences", {})
    with st.form("recommendations_form"):
        controls = st.columns(3)
        query = st.text_input("What matters to you?", placeholder="Comfortable headphones for travel")
        category = controls[0].selectbox(
            "Category", categories,
            index=categories.index(preferences.get("category", "All categories"))
            if preferences.get("category", "All categories") in categories else 0,
        )
        budget = controls[1].number_input(
            "Maximum budget (₹)", min_value=500, max_value=1000000,
            value=int(preferences.get("budget", 80000)), step=5000,
        )
        rating_options = [0.0, 3.5, 4.0, 4.5]
        rating_default = preferences.get("min_rating", 3.5)
        rating = controls[2].selectbox(
            "Minimum rating", rating_options,
            index=rating_options.index(rating_default) if rating_default in rating_options else 1,
        )
        submitted = st.form_submit_button("Update recommendations", width="stretch")

    if not submitted:
        st.caption("Submit a preference brief to rank matching catalog listings.")
        return
    terms = _meaningful_terms(query)
    filtered = filter_products(
        products, query=terms, category=category, max_price=budget, min_rating=rating
    )
    ranked = rank_products(filtered, budget=budget, query=terms)
    if ranked.empty and terms:
        ranked = rank_products(
            filter_products(products, category=category, max_price=budget, min_rating=rating),
            budget=budget,
        )
    st.caption(f"{format_number(len(ranked))} listings scored against your request")
    _render_product_grid(ranked, limit=8)
    st.markdown("### Match explanation")
    st.dataframe(
        pd.DataFrame(
            {
                "Signal": ["Explicit preferences", "Listing value", "Rating quality", "Popularity", "Budget fit", "Discount"],
                "Weight": ["10%", "25%", "30%", "15%", "15%", "5%"],
                "Source": ["Your request", "Processed catalog", "Product ratings", "Review volume", "Your budget", "Listed prices"],
            }
        ),
        hide_index=True,
        width="stretch",
    )


def show_planner():
    products = load_catalog()
    st.markdown("<div class='page-title'>Tell AI what you need.</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Recommendations are ranked from your preferences and current catalog signals.</div>", unsafe_allow_html=True)

    initial_query = st.session_state.pop("planner_initial_query", None)
    if initial_query is not None:
        st.session_state["planner_need"] = initial_query
    preferences = st.session_state.get("planner_preferences", {})
    with st.form("shopping_plan_form"):
        need = st.text_area(
            "Shopping brief",
            placeholder="I need wireless headphones for commuting, comfortable for long use, under ₹10,000.",
            height=110,
            key="planner_need",
        )
        controls = st.columns(3)
        budget = controls[0].number_input(
            "Budget (₹)", min_value=500, max_value=1000000,
            value=int(preferences.get("budget", 80000)), step=5000,
        )
        categories = ["All categories"] + get_categories(products)
        preferred_category = preferences.get("category", "All categories")
        category = controls[1].selectbox(
            "Category", categories,
            index=categories.index(preferred_category) if preferred_category in categories else 0,
        )
        rating_options = [0.0, 3.5, 4.0, 4.5]
        preferred_rating = preferences.get("min_rating", 3.5)
        minimum_rating = controls[2].selectbox(
            "Minimum rating", rating_options,
            index=rating_options.index(preferred_rating) if preferred_rating in rating_options else 1,
        )
        submitted = st.form_submit_button("Generate shopping plan →", width="stretch")

    if not submitted:
        st.caption("Example: “A reliable laptop for coding, 16 GB RAM, under ₹80,000.”")
        return
    if not need.strip():
        st.warning("Add a short description of what you need to build a plan.")
        return

    terms = _meaningful_terms(need)
    filtered = filter_products(
        products,
        query=terms,
        category=category,
        max_price=budget,
        min_rating=minimum_rating,
    )
    ranked = rank_products(filtered, budget=budget, query=terms)
    if ranked.empty and terms:
        ranked = rank_products(
            filter_products(products, category=category, max_price=budget, min_rating=minimum_rating),
            budget=budget,
        )
    if ranked.empty:
        st.warning("No products matched this budget and category. Try raising the budget or lowering the rating threshold.")
        return

    selected = select_within_budget(ranked, budget, limit=6)
    if selected.empty:
        st.warning("No single product in this category fits the selected budget.")
        return
    spend = float(selected["discount_price"].sum())
    st.markdown("### Your shopping plan")
    totals = st.columns(3)
    totals[0].metric("Strong matches", len(selected))
    totals[1].metric("Combined listed price", _money(spend))
    totals[2].metric("Budget remaining", _money(max(0, budget - spend)))
    st.caption("Match scores are a transparent ranking signal, not a claim of personal purchase-history learning.")
    _render_product_grid(selected, limit=6, score_label="Preference match")

    st.markdown("### How this ranking works")
    breakdown = pd.DataFrame(
        {"Signal": ["Explicit preferences", "Listing value", "Rating quality", "Popularity", "Budget fit", "Discount"],
         "Weight": ["10%", "25%", "30%", "15%", "15%", "5%"]}
    )
    st.dataframe(breakdown, hide_index=True, width="stretch")


def show_compare():
    st.markdown("<div class='page-title'>Compare</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Compare price and catalog signals side by side.</div>", unsafe_allow_html=True)
    ids = _session_list("compare_ids")
    saved = [product for product in (_product(item) for item in ids) if product is not None]
    if not saved:
        st.info("Add products to compare from Discover or AI Planner.")
        return

    columns = st.columns(len(saved))
    for column, row in zip(columns, saved):
        with column:
            st.markdown(f"**{row['name']}**")
            st.metric("Price", _money(row["discount_price"]))
            st.caption(f"{row['ratings']:.1f} / 5 · {format_number(row['no_of_ratings'])} reviews")

    comparison = pd.DataFrame(
        {
            "Product": [row["name"] for row in saved],
            "Price": [_money(row["discount_price"]) for row in saved],
            "List price": [_money(row["actual_price"]) for row in saved],
            "Rating": [round(float(row["ratings"]), 1) for row in saved],
            "Reviews": [int(row["no_of_ratings"]) for row in saved],
            "Category": [row["sub_category"] for row in saved],
            "Discount": [f"{float(row['discount_percentage']):.0f}%" for row in saved],
            "Processor / RAM / Battery": ["Not present in source catalog" for _ in saved],
        }
    )
    st.dataframe(comparison, hide_index=True, width="stretch")
    if st.button("Clear comparison", type="secondary"):
        st.session_state["compare_ids"] = []
        st.rerun()


def show_wishlist():
    st.markdown("<div class='page-title'>Wishlist</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Products saved during this session.</div>", unsafe_allow_html=True)
    saved = _session_list("wishlist_ids")
    rows = [product for product in (_product(item) for item in saved) if product is not None]
    if not rows:
        st.info("Your wishlist is empty. Save products from Discover or the AI Planner.")
        return
    _render_product_grid(pd.DataFrame(rows), limit=len(rows), score_label="Saved")
    for row in rows:
        if st.button(f"Track {row['name'][:54]}", key=f"track_{_key(row['product_id'])}"):
            _add_to_list("tracked_ids", row["product_id"])
            st.toast("Added to price tracker")
    if st.button("Clear wishlist", type="secondary"):
        st.session_state["wishlist_ids"] = []
        st.rerun()


def show_activity():
    st.markdown("<div class='page-title'>Activity</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Recent recommendation and model events recorded locally.</div>", unsafe_allow_html=True)
    if not LOG_PATH.exists():
        st.info("No activity has been recorded yet.")
        return
    logs = pd.read_csv(LOG_PATH)
    if logs.empty:
        st.info("No activity has been recorded yet.")
        return
    st.metric("Recorded events", format_number(len(logs)))
    st.dataframe(logs.tail(30).iloc[::-1], hide_index=True, width="stretch")


def show_settings():
    products = load_catalog()
    st.markdown("<div class='page-title'>Settings</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Preferences for this shopping session.</div>", unsafe_allow_html=True)
    preferences = st.session_state.get(
        "planner_preferences",
        {"budget": 80000, "category": "All categories", "min_rating": 3.5},
    )
    categories = ["All categories"] + get_categories(products)
    with st.form("preferences_form"):
        budget = st.number_input(
            "Default budget (₹)", min_value=500, max_value=1000000,
            value=int(preferences.get("budget", 80000)), step=5000,
        )
        category = st.selectbox(
            "Preferred category", categories,
            index=categories.index(preferences.get("category", "All categories"))
            if preferences.get("category", "All categories") in categories else 0,
        )
        rating = st.select_slider(
            "Minimum product rating", options=[0.0, 3.0, 3.5, 4.0, 4.5, 5.0],
            value=float(preferences.get("min_rating", 3.5)),
        )
        st.text_input("Display currency", value="INR · ₹", disabled=True)
        submitted = st.form_submit_button("Save preferences", width="stretch")
    if submitted:
        st.session_state["planner_preferences"] = {
            "budget": budget,
            "category": category,
            "min_rating": rating,
        }
        st.success("Preferences saved for this session.")
    st.caption("Account profiles and persistent cross-device preferences are not configured in this local deployment.")


def show_price_tracker():
    st.markdown("<div class='page-title'>Price tracker</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Watch catalog prices and set a target for the next visit.</div>", unsafe_allow_html=True)
    tracked = _session_list("tracked_ids")
    if not tracked:
        st.info("No products tracked yet. Add products to your wishlist, then select them below.")
        return

    rows = [product for product in (_product(item) for item in tracked) if product is not None]
    for row in rows:
        st.markdown(f"### {row['name']}")
        current = float(row["discount_price"])
        original = float(row["actual_price"])
        metrics = st.columns(3)
        metrics[0].metric("Current catalog price", _money(current))
        metrics[1].metric("List price", _money(original))
        metrics[2].metric("Listed discount", f"{max(0, float(row['discount_percentage'])):.0f}%")
        target = st.number_input(
            "Alert me below (₹)", min_value=1.0, max_value=10000000.0,
            value=float(st.session_state.get(f"target_{_key(row['product_id'])}", round(current * 0.95))),
            step=100.0, key=f"target_{_key(row['product_id'])}",
        )
        if target >= current:
            st.success("Current listing is at or below your target.")
        else:
            st.caption(f"Target is {_money(current - target)} below the current catalog price.")
        st.markdown(
            "<div style='border:1px solid #292929;border-radius:6px;padding:14px;color:#a3a3a3'>"
            "Price history is not present in the source dataset. This tracker compares the current catalog snapshot "
            "with the original list price; live refresh and historical lows require a connected retailer feed.</div>",
            unsafe_allow_html=True,
        )


def show_ml_intelligence():
    metrics = load_json(str(METRICS_PATH))
    training = load_json(str(TRAINING_PATH))
    logs = pd.read_csv(LOG_PATH) if LOG_PATH.exists() else pd.DataFrame()
    st.markdown("<div class='page-title'>ML Intelligence Center</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Recommendation quality, data lineage and operational signals.</div>", unsafe_allow_html=True)

    accuracy = metrics.get("Accuracy")
    model_name = training.get("model_name", metrics.get("Model", "Recommendation model"))
    cards = st.columns(4)
    cards[0].metric("Model", str(model_name))
    cards[1].metric("Evaluation accuracy", f"{float(accuracy):.1%}" if accuracy is not None else "N/A")
    cards[2].metric("Training records", format_number(training.get("training_samples", 0)))
    cards[3].metric("Prediction logs", format_number(len(logs)))

    stages = ["Data", "Validation", "Preprocessing", "Features", "Training", "Experiments", "Registry", "Deployment", "Monitoring", "Retraining"]
    st.markdown("### Recommendation lifecycle")
    st.markdown(
        "<div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,170px),1fr));gap:8px'>"
        + "".join(
            f"<div style='padding:15px 12px;border:1px solid {('#dedede' if index == 0 else '#303030')};background:{('#f5f5f5' if index == 0 else '#111')};color:{('#080808' if index == 0 else '#dedede')};border-radius:5px;font-size:13px'>{index + 1:02d} &nbsp; {stage}</div>"
            for index, stage in enumerate(stages)
        )
        + "</div>",
        unsafe_allow_html=True,
    )
    st.caption("Current model artifacts are read from the local training outputs. No live serving latency metric is recorded yet.")

    if metrics:
        metric_names = [name for name in ("Accuracy", "Precision", "Recall", "F1 Score") if name in metrics]
        values = [float(metrics[name]) * 100 for name in metric_names]
        chart = px.bar(x=metric_names, y=values, text=[f"{value:.1f}%" for value in values])
        chart.update_traces(marker_color="#d4d4d4", textposition="outside", cliponaxis=False)
        chart.update_layout(
            height=320, yaxis_range=[0, 110], yaxis_title="Score (%)", xaxis_title="",
            plot_bgcolor="#111111", paper_bgcolor="#111111", font_color="#e5e5e5",
            margin=dict(l=20, r=20, t=35, b=20), showlegend=False,
        )
        st.plotly_chart(chart, width="stretch")


def show_experiments():
    metrics = load_json(str(METRICS_PATH))
    training = load_json(str(TRAINING_PATH))
    st.markdown("<div class='page-title'>Experiments</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Evaluation summary from the latest locally recorded training run.</div>", unsafe_allow_html=True)
    if not metrics:
        st.warning("No model metrics are available yet. Run the training pipeline to create models/metrics.json.")
        return
    run = {
        "Run ID": "LOCAL-LATEST",
        "Model": training.get("model_name", metrics.get("Model", "Unknown")),
        "Dataset": f"{format_number(training.get('training_samples', 0))} train / {format_number(training.get('testing_samples', 0))} test",
        "Accuracy": metrics.get("Accuracy", "N/A"),
        "Precision": metrics.get("Precision", "N/A"),
        "Recall": metrics.get("Recall", "N/A"),
        "F1": metrics.get("F1 Score", "N/A"),
        "Created": training.get("training_date", "Unknown"),
        "Source": "models/metrics.json + training_info.json",
    }
    st.dataframe(pd.DataFrame([run]), hide_index=True, width="stretch")
    st.caption("This workspace has local model artifacts; experiment history is not exposed as MLflow runs in the current configuration.")


def show_registry():
    metrics = load_json(str(METRICS_PATH))
    training = load_json(str(TRAINING_PATH))
    st.markdown("<div class='page-title'>Model registry</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Versions available from the current local artifact store.</div>", unsafe_allow_html=True)
    if not metrics:
        st.warning("No registered model metrics were found.")
        return
    registry = pd.DataFrame(
        [{
            "Model": training.get("model_name", metrics.get("Model", "Recommendation model")),
            "Version": "Local latest",
            "Accuracy": metrics.get("Accuracy", "N/A"),
            "Dataset size": training.get("dataset_size", training.get("training_samples", "N/A")),
            "Algorithm": metrics.get("Model", "Not specified"),
            "Created": training.get("training_date", "Unknown"),
            "Status": "Available locally",
        }]
    )
    st.dataframe(registry, hide_index=True, width="stretch")
    st.caption("Historical versions and promotion states are not available in the checked-in model metadata.")


def show_dataset():
    products = load_catalog()
    st.markdown("<div class='page-title'>Data pipeline</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Snapshot of the processed product catalog used by the shopping experience.</div>", unsafe_allow_html=True)
    if products.empty:
        st.error("The processed catalog could not be loaded.")
        return
    metrics = st.columns(4)
    metrics[0].metric("Products", format_number(len(products)))
    metrics[1].metric("Features", len(products.columns))
    metrics[2].metric("Missing prices", format_number(int(products["discount_price"].isna().sum())))
    metrics[3].metric("Categories", products["sub_category"].nunique())
    st.markdown("### Ingestion → validation → features → training → evaluation → registry")
    st.dataframe(products.head(12), hide_index=True, width="stretch")


def show_monitoring():
    st.markdown("<div class='page-title'>Model monitoring</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Prediction volume and model outcomes from local monitoring logs.</div>", unsafe_allow_html=True)
    if not LOG_PATH.exists():
        st.info("No monitoring events have been recorded yet.")
        return
    logs = pd.read_csv(LOG_PATH)
    if logs.empty:
        st.info("No monitoring events have been recorded yet.")
        return
    total = len(logs)
    status_col = "status" if "status" in logs else None
    success = int(logs[status_col].astype(str).str.casefold().eq("success").sum()) if status_col else 0
    metrics = st.columns(3)
    metrics[0].metric("Prediction events", format_number(total))
    metrics[1].metric("Successful", format_number(success))
    metrics[2].metric("Error rate", f"{(total - success) / total:.1%}" if status_col and total else "Not measured")
    st.markdown("### Feature drift")
    feature_names = [name for name in ("ratings", "discount_price", "discount_percentage", "value_score") if name in logs]
    if len(logs) < 30 or not feature_names:
        st.info(f"Drift scoring needs at least 30 events and a versioned training baseline. Current events: {total}.")
    else:
        st.dataframe(
            pd.DataFrame(
                {"Feature": feature_names, "Drift score": ["Baseline required"] * len(feature_names),
                 "Threshold": [0.20] * len(feature_names), "Status": ["Insufficient baseline"] * len(feature_names)}
            ),
            hide_index=True,
            width="stretch",
        )
    if "prediction" in logs:
        counts = logs["prediction"].astype(str).value_counts().rename_axis("Outcome").reset_index(name="Events")
        chart = px.bar(counts, x="Outcome", y="Events")
        chart.update_traces(marker_color="#d4d4d4")
        chart.update_layout(
            height=300, plot_bgcolor="#111111", paper_bgcolor="#111111", font_color="#e5e5e5",
            margin=dict(l=20, r=20, t=25, b=20), showlegend=False,
        )
        st.plotly_chart(chart, width="stretch")
    st.dataframe(logs.tail(20).iloc[::-1], hide_index=True, width="stretch")


def show_retraining():
    from dashboard.retraining import show

    show()