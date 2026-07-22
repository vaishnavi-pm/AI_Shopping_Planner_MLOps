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
            background: #0b1220;
            color: #e6edf3;
        }

        .css-1d391kg {
            background-color: #0b1220 !important;
        }

        .reportview-container,
        .main,
        .block-container {
            background-color: #0b1220;
            color: #e6edf3;
        }

        .stButton > button {
            background: linear-gradient(135deg, #5b8de1 0%, #4737ff 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.75rem 1rem;
            box-shadow: 0 10px 20px rgba(14, 68, 171, 0.22);
        }

        .stButton > button:hover {
            opacity: 0.9;
        }

        .metric-card,
        .tech-card,
        .panel-card {
            border-radius: 18px;
            padding: 20px;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 10px 30px rgba(0,0,0,0.25);
            margin-bottom: 18px;
        }

        .metric-title {
            font-size: 0.9rem;
            color: #8ca0c1;
            margin-bottom: 0.5rem;
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 0.35rem;
        }

        .metric-subtitle {
            font-size: 0.85rem;
            color: #a1b0d1;
        }

        .page-title {
            font-size: 2.75rem;
            font-weight: 800;
            letter-spacing: -0.06rem;
        }

        .page-subtitle {
            font-size: 1.05rem;
            color: #a4b3cf;
            margin-top: 0.15rem;
        }

        .section-banner {
            border-radius: 18px;
            padding: 22px;
            background: linear-gradient(
                135deg,
                rgba(56, 64, 106, 0.9),
                rgba(34, 40, 76, 0.9)
            );
            border: 1px solid rgba(255,255,255,0.08);
            margin-bottom: 24px;
        }

        .tech-card {
            min-height: 120px;
        }

        .tech-title {
            font-size: 1rem;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 0.35rem;
        }

        .tech-description {
            color: #c7d2f1;
            line-height: 1.55;
        }

        .sidebar .sidebar-content {
            background: linear-gradient(
                180deg,
                #09101d 0%,
                #131c34 100%
            );
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