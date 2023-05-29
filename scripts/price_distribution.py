import os
import seaborn as sns
import matplotlib.pyplot as plt
from typing import List

import numpy as np


__DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "data", "HousesInfo.txt")


def get_prices() -> List[float]:
    """
    Get prices from the data file.

    Returns:
        List[float]: _description_
    """
    prices: List[float] = []

    with open(__DATA_FILE, "r") as f:
        for line in f:
            values: List[str] = line.strip().split()

            # only process lines with 5 columns
            if len(values) == 5:
                # prices are in the 5th column
                price: str = values[4]
                prices.append(float(price))

    return prices


def barplot_prices() -> None:
    """
    Plot the prices from the data file.
    Bin width of value range 100000 (price).
    Highest limit for price is set to 6 million.
    On the x-axis are the prices of the hourses.
    """
    prices: List[float] = get_prices()
    max_price: float = max(prices)
    step: int = 100000

    sns.set(style='whitegrid')
    plt.figure(figsize=(12, 6))

    # Plot the bar plot
    ax = sns.histplot(prices, bins=range(
        0, round(max_price + step), step), kde=False)
    ax.set_xlabel("Price (in millions of $)")
    ax.set_ylabel("Number of houses")
    ax.set_title(
        "Price distribution for houses in price ranges of $" + str(step))

    # Add text labels above each bar based on their index
    for _, patch in enumerate(ax.patches):
        height = patch.get_height()
        if height > 0:
            ax.annotate(height, (patch.get_x() + patch.get_width() /
                        2, height), ha='center', va='bottom', fontsize='small', color='steelblue')

    plt.show()

    # Print the mean, median, and the quantiles
    print("Mean: ", np.mean(prices))
    print("Median: ", np.median(prices))
    print("Quantiles: ", np.quantile(prices, [0.25, 0.5, 0.75, 1.0]))
    print("10th percetiles: ", np.quantile(
        prices, [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]))


if __name__ == "__main__":
    barplot_prices()
