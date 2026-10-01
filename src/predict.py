import pandas as pd


def generate_shopping_plan(
    dataset_path,
    budget,
    purpose,
    priority,
    family_size,
):
    """
    Generate an AI Shopping Plan based on user inputs.

    Returns:
        result_df : DataFrame
        total_cost : float
        remaining_budget : float
        summary : str
    """

    # Load dataset
    df = pd.read_csv(dataset_path)

    # Filter by purpose
    filtered = df[df["Purpose"] == purpose].copy()

    # Filter by priority
    if priority != "Daily Use":
        filtered = filtered[
            (filtered["Priority"] == priority)
            | (filtered["Priority"] == "Daily Use")
        ]

    # Sort by rating (highest first)
    filtered = filtered.sort_values(
        by="Rating",
        ascending=False,
    )

    recommendations = []
    total_cost = 0

    for _, row in filtered.iterrows():

        product = row["Product"]
        price = float(row["Price"])
        rating = float(row["Rating"])

        # AI Recommendation Logic
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

    result_df = pd.DataFrame(recommendations)

    remaining_budget = budget - total_cost

    buy_count = len(
        result_df[result_df["Recommendation"] == "Buy Now"]
    )

    summary = f"""
AI Shopping Summary

Budget: ₹{budget:,.0f}
Purpose: {purpose}
Priority: {priority}
Family Size: {family_size}

Recommended to buy {buy_count} products.

Total Cost: ₹{total_cost:,.0f}

Remaining Budget: ₹{remaining_budget:,.0f}

Products marked 'Wait' can be purchased later.

Products marked 'Avoid' are not recommended
based on your selected budget and priority.
"""

    return (
        result_df,
        total_cost,
        remaining_budget,
        summary,
    )


if __name__ == "__main__":

    result, total, remaining, summary = generate_shopping_plan(
        dataset_path="data/Amazon_Products.csv",
        budget=150000,
        purpose="Hostel",
        priority="Study",
        family_size=1,
    )

    print(result)

    print("\nTotal Cost:", total)

    print("Remaining Budget:", remaining)

    print(summary)