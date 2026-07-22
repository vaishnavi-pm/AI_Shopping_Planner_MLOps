import json
import os
import subprocess

import streamlit as st

from dashboard_utils import load_json, section_card


def show():
    st.markdown("<div class='page-title'>♻️ Retraining</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Run model retraining and refresh metrics automatically.</div>", unsafe_allow_html=True)

    metrics = load_json("models/metrics.json")
    training_info = load_json("models/training_info.json")

    st.markdown("---")
    st.subheader("Current Model Snapshot")

    st.write(f"**Model:** {training_info.get('model_name', 'Unknown')}")
    st.write(f"**Training Date:** {training_info.get('training_date', 'N/A')}")
    st.write(f"**Training Samples:** {training_info.get('training_samples', 'N/A')}")
    st.write(f"**Testing Samples:** {training_info.get('testing_samples', 'N/A')}")
    st.write(f"**Current Accuracy:** {metrics.get('Accuracy', 0):.2%}" if metrics else "**Current Accuracy:** N/A")

    st.markdown("---")

    if st.button("🚀 Retrain Model"):
        with st.spinner("Running retraining pipeline..."):
            process = subprocess.run(
                ["python", "src/train.py"],
                capture_output=True,
                text=True,
            )

        if process.returncode == 0:
            st.success("✅ Model retraining completed successfully.")
            st.code(process.stdout)
            st.markdown("---")
            new_metrics = load_json("models/metrics.json")
            new_training_info = load_json("models/training_info.json")
            st.write("### Updated Metrics")
            if new_metrics:
                st.write(f"- Accuracy: {new_metrics.get('Accuracy', 0):.2%}")
                st.write(f"- Precision: {new_metrics.get('Precision', 0):.2%}")
                st.write(f"- Recall: {new_metrics.get('Recall', 0):.2%}")
                st.write(f"- F1 Score: {new_metrics.get('F1 Score', 0):.2%}")
            else:
                st.warning("Updated metrics could not be loaded.")
        else:
            st.error("❌ Retraining failed. Check the logs below.")
            st.code(process.stderr)

    st.markdown("---")
    section_card(
        """
        <p>Retraining uses the latest processed dataset and updates model artifacts in the models directory.
        Use this control to refresh performance after data drift or new feature updates.</p>
        """
    )
