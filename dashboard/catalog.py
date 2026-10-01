from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = PROJECT_ROOT / "data" / "processed" / "feature_data.csv"
PRODUCT_COLUMNS = [
    "name",
    "main_category",
    "sub_category",
    "image",
    "link",
    "ratings",
    "no_of_ratings",
    "discount_price",
    "actual_price",
    "discount_percentage",
    "popularity_score",
    "value_score",
]


@st.cache_data(show_spinner="Loading the product catalog...")
def load_catalog():
    if not CATALOG_PATH.exists():
        return pd.DataFrame(columns=PRODUCT_COLUMNS + ["product_id", "brand"])

    available_columns = pd.read_csv(CATALOG_PATH, nrows=0).columns
    columns = [column for column in PRODUCT_COLUMNS if column in available_columns]
    products = pd.read_csv(CATALOG_PATH, usecols=columns, low_memory=False)

    for column in ("name", "main_category", "sub_category", "image", "link"):
        if column not in products:
            products[column] = ""
        products[column] = products[column].fillna("").astype(str).str.strip()

    for column in (
        "ratings",
        "no_of_ratings",
        "discount_price",
        "actual_price",
        "discount_percentage",
        "popularity_score",
        "value_score",
    ):
        if column not in products:
            products[column] = 0.0
        products[column] = pd.to_numeric(products[column], errors="coerce")

    products["discount_price"] = products["discount_price"].fillna(
        products["actual_price"]
    )
    products["actual_price"] = products["actual_price"].fillna(
        products["discount_price"]
    )
    products["ratings"] = products["ratings"].fillna(0).clip(0, 5)
    products = products[
        (products["name"].str.len() > 0) & (products["discount_price"] > 0)
    ].copy()
    products["image"] = products["image"].str.replace(
        r"/images/W/[^/]+/images/I/", "/images/I/", regex=True
    )
    products = products.drop_duplicates(
        subset=["name", "discount_price"], keep="first"
    )
    products["product_id"] = products["link"].where(
        products["link"].str.startswith("http"), products["name"]
    )
    products["brand"] = products["name"].str.split().str[0].str.strip(" ,")
    return products.reset_index(drop=True)


def get_categories(products):
    counts = products["sub_category"].value_counts()
    return counts.head(60).index.tolist()


def filter_products(
    products,
    query="",
    category="All categories",
    max_price=None,
    min_rating=0.0,
    brand="All brands",
):
    filtered = products
    if category != "All categories":
        filtered = filtered[filtered["sub_category"] == category]
    if max_price is not None:
        filtered = filtered[filtered["discount_price"] <= max_price]
    if min_rating:
        filtered = filtered[filtered["ratings"] >= min_rating]
    if brand != "All brands":
        filtered = filtered[filtered["brand"].str.casefold() == brand.casefold()]
    if query.strip():
        terms = [term.casefold() for term in query.split() if len(term) > 1]
        searchable = (
            filtered["name"].str.casefold()
            + " "
            + filtered["sub_category"].str.casefold()
            + " "
            + filtered["main_category"].str.casefold()
        )
        if terms:
            matches = pd.Series(False, index=filtered.index)
            for term in terms:
                matches |= searchable.str.contains(term, regex=False, na=False)
            filtered = filtered[matches]
    return filtered


def rank_products(products, budget=None, query=""):
    if products.empty:
        return products.assign(match_score=pd.Series(dtype=float))

    ranked = products.copy()
    rating_score = (ranked["ratings"] / 5).fillna(0) * 30
    value_score = ranked["value_score"].rank(pct=True).fillna(0.5) * 25
    popularity_score = ranked["popularity_score"].rank(pct=True).fillna(0.5) * 15
    deal_score = ranked["discount_percentage"].clip(0, 100).fillna(0) * 0.05
    if budget and budget > 0:
        price_ratio = ranked["discount_price"] / budget
        budget_score = (1 - (price_ratio - 0.72).abs() / 0.72).clip(0, 1) * 15
    else:
        budget_score = pd.Series(7.5, index=ranked.index)

    preference_score = pd.Series(0.0, index=ranked.index)
    terms = [term.casefold() for term in query.split() if len(term) > 1]
    if terms:
        searchable = ranked["name"].str.casefold()
        preference_score = sum(
            searchable.str.contains(term, regex=False, na=False).astype(float)
            for term in terms
        ) / len(terms) * 10

    ranked["match_score"] = (
        rating_score + value_score + popularity_score + deal_score + budget_score + preference_score
    ).clip(0, 100).round(1)
    return ranked.sort_values(
        ["match_score", "ratings", "no_of_ratings"], ascending=False
    )


def select_within_budget(products, budget, limit=6):
    selected_indices = []
    remaining = float(budget)
    for index, product in products.iterrows():
        price = float(product["discount_price"])
        if price <= remaining + 1e-9:
            selected_indices.append(index)
            remaining -= price
            if len(selected_indices) == limit:
                break
    return products.loc[selected_indices].copy()