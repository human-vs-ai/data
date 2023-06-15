import json
import math
import os
from typing import Tuple

import pandas as pd


__RESPONSES_FOLDER = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "data", "responses")

__RESULTS_FILE = os.path.join(__RESPONSES_FOLDER, "Results_stage2_pool2.xls")

__OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "data", "results")

__OUTPUT_FILENAME = "stage_2_output.json"


def post_process_results(filename: str = __OUTPUT_FILENAME):
    """
    Post-processes the results of the second stage of the experiment.
    The results are stored in a JSON file.

    Args:
        filename (str, optional): Custom filename to store date in. Defaults to __OUTPUT_FILENAME.
    """

    # File checks
    if not os.path.exists(__OUTPUT_FOLDER):
        os.makedirs(__OUTPUT_FOLDER)

    if not os.path.exists(__RESULTS_FILE):
        print("Results file not found: {}".format(__RESULTS_FILE))
        return

    # Read results
    id_counter = dict()
    results = dict()
    df = pd.read_excel(__RESULTS_FILE)
    for _, row in df.iterrows():
        # House info
        house_id: int = row['INPUT:id']
        house_price: int = row['INPUT:price']
        house_bedrooms: int = row['INPUT:n_bedrooms']
        house_bathrooms: int = row['INPUT:n_bathrooms']
        house_area_m2: int = row['INPUT:surface_area_m2']
        house_area_sq_ft: int = row['INPUT:surface_area_sq_ft']

        # Predictions
        prediction_human: str = row['INPUT:human_price']
        prediction_ai: str = row['INPUT:ai_price']

        # Rationales
        rationale_human: str = row['INPUT:human_advice']
        rationale_ai: str = row['INPUT:ai_advice']

        # Quality
        prediction_ai_quality: int = row['INPUT:ai_advice_quality']

        # Responses
        response_ai = row['OUTPUT:ai_rating']
        response_human = row['OUTPUT:human_rating']
        response_verdict = row['OUTPUT:choice']

        # Check if house ID is already in the results
        if house_id not in id_counter:
            id_counter[house_id] = 1
        else:
            id_counter[house_id] += 1

        # Create a unique ID for each house
        house_id_unique = "{}_{}".format(house_id, id_counter[house_id])

        # Create a new entry for the house in the results
        print("Processing house {} - Response #{}"
              .format(house_id, id_counter[house_id]))

        results[house_id_unique] = {
            'id': house_id,
            'price': house_price,
            'bedrooms': house_bedrooms,
            'bathrooms': house_bathrooms,
            'area': {
                'm2': house_area_m2,
                'sq_ft': house_area_sq_ft
            },
            'predictions': {
                'human': _parse_price_prediction(prediction_human),
                'ai': _parse_price_prediction(prediction_ai)
            },
            'rationales': {
                'human': True if type(rationale_human) == 'str' else False,
                'ai': True if type(rationale_ai) == 'str' else False,
                'human_rationale': rationale_human if type(rationale_human) == 'str' else "",
                'ai_rationale': rationale_ai if type(rationale_ai) == 'str' else ""
            },
            'quality_ai': int(prediction_ai_quality),
            'responses': {
                'ai': response_ai,
                'human': response_human,
                'verdict': response_verdict
            }
        }

    # Save results
    output_file = os.path.join(__OUTPUT_FOLDER, filename)
    with open(output_file, 'w') as f:
        json.dump(results, f)


def _parse_price_prediction(prediction: str) -> Tuple[int, int]:
    """
    Parse the price prediction string.

    Example: "$100,000 - $200,000" -> (100000, 200000)

    :param prediction: Price prediction string.
    :return: Tuple of lower and upper bound of the price prediction.
    """

    # Parse the prediction string
    bounds_split = prediction.split("-")
    lower_bound = int(bounds_split[0]
                      .strip()
                      .replace("$", "")
                      .replace(",", ""))
    upper_bound = int(bounds_split[1]
                      .strip()
                      .replace("$", "")
                      .replace(",", ""))

    return lower_bound, upper_bound


if __name__ == "__main__":
    post_process_results()
