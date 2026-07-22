import csv
import os
from datetime import datetime

import joblib
import pandas as pd
import streamlit as st

from dashboard_utils import load_json, load_dataframe, section_card


def show():
    st.markdown("<div class='page-title'>🔮 Prediction</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Generate predictions using the deployed model and log production results.</div>", unsafe_allow_html=True)

    model_path = "models/best_model.pkl"
    feature_path = "models/feature_names.json"

    if not os.path.exists(model_path):
        st.error("Trained model not found. Run src/train.py to generate models/best_model.pkl.")
        return

    model = joblib.load(model_path)
    feature_names = load_json(feature_path)

    if not feature_names:
        df = load_dataframe("data/processed/train.csv")
        if df.empty:
            st.error("Feature metadata not found and dataset is unavailable.")
            return
        feature_names = [col for col in df.columns if col != "decision"]

    st.markdown("---")

    with st.form(key="prediction_form"):
        st.subheader("Input Features")
        user_inputs = {}
        for feature in feature_names:
            user_inputs[feature] = st.number_input(
                label=feature.replace("_", " ").title(),
                value=0.0,
                step=0.1,
                format="%.4f",
            )

        submit_prediction = st.form_submit_button(label="🚀 Predict")

        if submit_prediction:
            try:
                input_df = pd.DataFrame([user_inputs])
                prediction = model.predict(input_df)
                prediction_value = prediction[0]

                st.success(f"Prediction Result: **{prediction_value}**")
                st.info("The prediction has been logged for monitoring.")

                os.makedirs("monitoring", exist_ok=True)
                log_file = "monitoring/logs.csv"
                file_exists = os.path.exists(log_file)

                with open(log_file, "a", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    if not file_exists:
                        writer.writerow([
                            "timestamp",
                            *feature_names,
                            "prediction",
                            "status",
                        ])
                    writer.writerow([
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        *[user_inputs[f] for f in feature_names],
                        prediction_value,
                        "Success",
                    ])

            except Exception as err:
                st.error(f"Prediction failed: {err}")
                with open("monitoring/logs.csv", "a", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    if not os.path.exists("monitoring/logs.csv"):
                        writer.writerow([
                            "timestamp",
                            *feature_names,
                            "prediction",
                            "status",
                        ])
                    writer.writerow([
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        *[user_inputs.get(f, 0) for f in feature_names],
                        "ERROR",
                        "Failed",
                    ])

    st.markdown("---")
    section_card(
        """
        <p>Use this form to run a single inference request and capture the prediction output for monitoring and analysis.</p>
        """
    )
