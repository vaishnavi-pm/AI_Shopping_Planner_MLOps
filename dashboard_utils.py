import json
import os
from datetime import datetime

import pandas as pd
import streamlit as st


def load_json(path):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
    except Exception:
        pass
    return {}


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def load_dataframe(path):
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()


def apply_dark_theme():
    st.markdown(
        """
        <style>
        :root {
            color-scheme: dark;
            --page: #080808;
            --surface: #111111;
            --surface-raised: #171717;
            --border: #282828;
            --text: #f5f5f5;
            --muted: #a3a3a3;
            --quiet: #737373;
        }

        html, body, [data-testid="stAppViewContainer"], .stApp {
            background: var(--page);
            color: var(--text);
            font-family: Inter, "Segoe UI", sans-serif;
        }

        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stAppViewContainer"] > .main { background: var(--page); }
        [data-testid="stMainBlockContainer"] {
            max-width: 1480px;
            padding: 2rem 3rem 4rem;
        }
        [data-testid="stSidebar"] {
            background: #0d0d0d;
            border-right: 1px solid var(--border);
        }
        [data-testid="stSidebar"] > div:first-child { padding-top: 1.3rem; }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            color: var(--muted);
        }
        [data-testid="stSidebar"] div[role="radiogroup"] { gap: 0.2rem; }
        [data-testid="stSidebar"] div[role="radiogroup"] label {
            min-height: 2.55rem;
            border-radius: 6px;
            padding: 0.38rem 0.65rem;
            color: var(--muted);
            transition: background 160ms ease, color 160ms ease;
        }
        [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
            background: #1b1b1b;
            color: white;
        }
        [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
            background: #f5f5f5;
            color: #080808;
        }
        [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
            color: #080808;
        }
        [data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
            display: none;
        }

        h1, h2, h3, h4 { color: var(--text); letter-spacing: 0; }
        h1 { font-size: 2.25rem; font-weight: 650; }
        h2 { font-size: 1.45rem; font-weight: 600; }
        p, li, label, [data-testid="stCaptionContainer"] { color: var(--muted); }
        hr { border-color: var(--border); }
        [data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 7px;
            padding: 1rem 1.15rem;
        }
        [data-testid="stMetricLabel"] p { color: var(--muted); font-size: 0.82rem; }
        [data-testid="stMetricValue"] { color: var(--text); font-size: 1.8rem; }

        .stButton > button, [data-testid="stFormSubmitButton"] > button {
            min-height: 2.65rem;
            background: #f5f5f5;
            color: #080808;
            border: 1px solid #f5f5f5;
            border-radius: 5px;
            font-weight: 600;
            transition: transform 150ms ease, background 150ms ease;
        }
        .stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
            background: #d4d4d4;
            border-color: #d4d4d4;
            color: #080808;
            transform: translateY(-1px);
        }
        .stButton > button[kind="secondary"] {
            background: transparent;
            color: var(--text);
            border-color: #383838;
        }
        input, textarea, [data-baseweb="select"] > div {
            background: #111111 !important;
            border-color: #303030 !important;
            border-radius: 5px !important;
        }
        [data-testid="stDataFrame"], [data-testid="stTable"] {
            border: 1px solid var(--border);
            border-radius: 6px;
            overflow: hidden;
        }
        .metric-card, .tech-card, .panel-card {
            border-radius: 7px;
            padding: 1.25rem;
            background: var(--surface);
            border: 1px solid var(--border);
            margin-bottom: 1rem;
        }
        .metric-title { color: var(--muted); font-size: 0.85rem; margin-bottom: 0.45rem; }
        .metric-value { color: var(--text); font-size: 1.8rem; font-weight: 650; margin-bottom: 0.3rem; }
        .metric-subtitle { color: var(--quiet); font-size: 0.82rem; }
        .page-title { color: var(--text); font-size: 2.3rem; font-weight: 650; }
        .page-subtitle { color: var(--muted); font-size: 1rem; margin-top: 0.2rem; }
        .section-banner {
            border-radius: 7px;
            padding: 1.1rem 1.25rem;
            background: var(--surface);
            border: 1px solid var(--border);
            margin: 1rem 0 1.4rem;
        }
        .tech-card { min-height: 112px; }
        .tech-title { color: var(--text); font-size: 1rem; font-weight: 600; margin-bottom: 0.35rem; }
        .tech-description { color: var(--muted); line-height: 1.55; }
        [data-testid="stPlotlyChart"] { border: 1px solid var(--border); border-radius: 6px; }
        @media (max-width: 760px) {
            [data-testid="stMainBlockContainer"] { padding: 1.25rem 1rem 3rem; }
            .page-title, h1 { font-size: 1.8rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def metric_card(title, value, subtitle=""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def tech_card(title, description):
    st.markdown(
        f"""
        <div class="tech-card">
            <div class="tech-title">{title}</div>
            <div class="tech-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_card(content):
    st.markdown(
        f"""
        <div class="panel-card">
            {content}
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_number(value):
    try:
        return f"{int(value):,}"
    except Exception:
        return str(value)


def format_percentage(value):
    try:
        if isinstance(value, float) and value <= 1:
            return f"{value * 100:.2f}%"
        return f"{value:.2f}%"
    except Exception:
        return str(value)


def safe_timestamp(value):
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return value