import csv
import os
from datetime import datetime

import pandas as pd
import streamlit as st

from dashboard_utils import section_card


def show():
    st.markdown("<div class='page-title'>🛒 AI Shopping Planner</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-subtitle'>Plan your shopping intelligently based on your budget and needs.</div>",
        unsafe_allow_html=True,
    )

    dataset_path = "data/Amazon_Products.csv"

    if not os.path.exists(dataset_path):
        st.error("Dataset not found.")
        return

    df = pd.read_csv(dataset_path)

    st.markdown("---")

    with st.form("shopping_form"):

        st.subheader("Enter Your Requirements")

        budget = st.number_input(
            "Budget (₹)",
            min_value=1000,
            value=50000,
            step=1000,
        )

        purpose = st.selectbox(
            "Purpose",
            [
                "Hostel",
                "Home",
                "Office",
                "Gaming",
                "Travel",
            ],
        )

        priority = st.selectbox(
            "Priority",
            [
                "Study",
                "Work",
                "Entertainment",
                "Daily Use",
            ],
        )

        family_size = st.number_input(
            "Family Size",
            min_value=1,
            max_value=10,
            value=1,
        )

        submit = st.form_submit_button("🚀 Generate Shopping Plan")

    if submit:

        data = df.copy()

        data = data[data["Purpose"] == purpose]

        if priority != "Daily Use":
            data = data[
                (data["Priority"] == priority)
                | (data["Priority"] == "Daily Use")
            ]

        recommendations = []

        total_cost = 0

        for _, row in data.iterrows():

            price = row["Price"]

            if total_cost + price <= budget:

                recommendation = "Buy Now"
                total_cost += price

            elif price <= budget * 0.20:

                recommendation = "Wait"

            else:

                recommendation = "Avoid"

            recommendations.append(
                {
                    "Product": row["Product"],
                    "Price": price,
                    "Rating": row["Rating"],
                    "Recommendation": recommendation,
                }
            )

        result = pd.DataFrame(recommendations)

        st.success("Shopping Plan Generated Successfully")

        st.dataframe(
            result,
            use_container_width=True,
        )

        remaining = budget - total_cost

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Cost", f"₹{total_cost:,.0f}")

        with col2:
            st.metric("Remaining Budget", f"₹{remaining:,.0f}")

        st.markdown("---")

        buy_items = result[result["Recommendation"] == "Buy Now"]

        summary = f"""
### 🤖 AI Shopping Summary

Budget : ₹{budget:,.0f}

Purpose : {purpose}

Priority : {priority}

Family Size : {family_size}

You can purchase **{len(buy_items)} products**
within your budget.

The estimated spending is **₹{total_cost:,.0f}**
and your remaining budget will be
**₹{remaining:,.0f}**.

Products marked **Wait**
can be purchased later.

Products marked **Avoid**
are currently not recommended based
on your selected budget and priority.
"""

        st.markdown(summary)

        os.makedirs("monitoring", exist_ok=True)

        log_file = "monitoring/logs.csv"

        file_exists = os.path.exists(log_file)

        with open(log_file, "a", newline="", encoding="utf-8") as file:

            writer = csv.writer(file)

            if not file_exists:

                writer.writerow(
                    [
                        "Timestamp",
                        "Budget",
                        "Purpose",
                        "Priority",
                        "Family Size",
                        "Total Cost",
                        "Remaining Budget",
                    ]
                )

            writer.writerow(
                [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    budget,
                    purpose,
                    priority,
                    family_size,
                    total_cost,
                    remaining,
                ]
            )

        st.success("Monitoring log updated successfully.")

    st.markdown("---")

    section_card(
        """
<h4>About AI Shopping Planner</h4>

<p>

The AI Shopping Planner recommends products according to the user's
budget, purpose, priority, and family size.

It intelligently categorizes each product into
<b>Buy Now</b>,
<b>Wait</b>, or
<b>Avoid</b>,
calculates the total cost, remaining budget,
generates an AI shopping summary,
and records every prediction for monitoring.

</p>
"""
    )