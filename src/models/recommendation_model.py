import pandas as pd


class RecommendationModel:
    """
    AI Shopping Planner Recommendation Model
    """

    def __init__(self, dataset_path):
        self.dataset = pd.read_csv(dataset_path)

    def recommend(
        self,
        budget,
        purpose,
        priority,
        family_size=1,
    ):
        """
        Generate shopping recommendations.

        Returns:
            DataFrame,
            total_cost,
            remaining_budget,
            summary
        """

        df = self.dataset.copy()

        # Filter by purpose
        df = df[df["Purpose"] == purpose]

        # Filter by priority
        if priority != "Daily Use":
            df = df[
                (df["Priority"] == priority)
                | (df["Priority"] == "Daily Use")
            ]

        # Highest-rated products first
        df = df.sort_values(
            by="Rating",
            ascending=False,
        )

        recommendations = []
        total_cost = 0

        for _, row in df.iterrows():

            product = row["Product"]
            price = float(row["Price"])
            rating = float(row["Rating"])

            # Recommendation Logic
            if total_cost + price <= budget:
                recommendation = "Buy Now"
                total_cost += price

            elif price <= budget * 0.20:
                recommendation = "Wait"

            else:
                recommendation = "Avoid"

            recommendations.append(
                {
                    "Product": product,
                    "Price": price,
                    "Rating": rating,
                    "Recommendation": recommendation,
                }
            )

        result = pd.DataFrame(recommendations)

        remaining_budget = budget - total_cost

        buy_now = len(
            result[result["Recommendation"] == "Buy Now"]
        )

        wait = len(
            result[result["Recommendation"] == "Wait"]
        )

        avoid = len(
            result[result["Recommendation"] == "Avoid"]
        )

        summary = f"""
AI Shopping Summary

Budget : ₹{budget:,.0f}
Purpose : {purpose}
Priority : {priority}
Family Size : {family_size}

Recommended Products : {buy_now}

Products to Buy Later : {wait}

Products to Avoid : {avoid}

Estimated Cost : ₹{total_cost:,.0f}

Remaining Budget : ₹{remaining_budget:,.0f}
"""

        return (
            result,
            total_cost,
            remaining_budget,
            summary,
        )