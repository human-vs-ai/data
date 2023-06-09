from enum import Enum
import json
import os
from typing import Union

# Plotting
import seaborn as sns
import matplotlib.pyplot as plt

from pyparsing import Dict

__OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "data", "results")

__OUTPUT_FILENAME = "stage_2_output.json"


class Verdict(Enum):
    HUMAN = 1
    AI = 2
    EQUAL = 3


def analyze_results(filename: str = __OUTPUT_FILENAME):
    """
    Analyzes the results of the second stage of the experiment.

    Format of stored results: {
            'id': int,
            'price': int,
            'bedrooms': int,
            'bathrooms': int,
            'area': {
                'm2': int,
                'sq_ft': int
            },
            'predictions': {
                'human': (int, int),
                'ai': (int, int)
            },
            'rationales': {
                'human': bool,
                'ai': bool,
                'human_rationale': str,
                'ai_rationale': str
            },
            'quality_ai': int,
            'responses': {
                'ai': int,
                'human': int,
                'verdict': str
            }
        }

    Args:
        filename (str, optional): Custom filename to retrieve data from. Defaults to __OUTPUT_FILENAME. Needs to confirm to post_process_data.py's output format.
    """

    # Read results
    results = dict()
    with open(os.path.join(__OUTPUT_FOLDER, filename), "r") as f:
        results = json.load(f)

    # Analyze results
    yes_yes = __compare_dict_template()  # Human and AI rationale shown
    # Human rationale shown, AI rationale not shown
    yes_no = __compare_dict_template()
    # Human rationale not shown, AI rationale shown
    no_yes = __compare_dict_template()
    no_no = __compare_dict_template()   # Human and AI rationale both not shown

    for result in results.values():
        human_rationale_shown: bool = result['rationales']['human']
        ai_rationale_shown: bool = result['rationales']['ai']

        if human_rationale_shown and ai_rationale_shown:
            _add_ratings(human=result['responses']['human'],
                         ai=result['responses']['ai'], comparison_dict=yes_yes)
            _add_verdict(verdict=__parse_verdict_to_enum(
                result['responses']['verdict']), comparison_dict=yes_yes)
        elif human_rationale_shown and not ai_rationale_shown:
            _add_ratings(human=result['responses']['human'],
                         ai=result['responses']['ai'], comparison_dict=yes_no)
            _add_verdict(verdict=__parse_verdict_to_enum(
                result['responses']['verdict']), comparison_dict=yes_no)
        elif not human_rationale_shown and ai_rationale_shown:
            _add_ratings(human=result['responses']['human'],
                         ai=result['responses']['ai'], comparison_dict=no_yes)
            _add_verdict(verdict=__parse_verdict_to_enum(
                result['responses']['verdict']), comparison_dict=no_yes)
        else:
            _add_ratings(human=result['responses']['human'],
                         ai=result['responses']['ai'], comparison_dict=no_no)
            _add_verdict(verdict=__parse_verdict_to_enum(
                result['responses']['verdict']), comparison_dict=no_no)

    # Print results
    print("Yes-Yes: {}".format(yes_yes))
    print("Yes-No: {}".format(yes_no))
    print("No-Yes: {}".format(no_yes))
    print("No-No: {}".format(no_no))

    # Plot results in a 2x2 grid of bar charts of the binary ratings: Human, Equal, AI
    _, axs = plt.subplots(2, 2, figsize=(8, 6))
    sns.barplot(x=['Human', 'Equal', 'AI'], y=[yes_yes['binary']['human'], yes_yes['binary']['equal'], yes_yes['binary']['ai']],
                ax=axs[1, 1]).set_title("Both rationales shown")
    sns.barplot(x=['Human', 'Equal', 'AI'], y=[yes_no['binary']['human'], yes_no['binary']['equal'], yes_no['binary']['ai']],
                ax=axs[1, 0]).set_title("Only human rationale shown")
    sns.barplot(x=['Human', 'Equal', 'AI'], y=[no_yes['binary']['human'], no_yes['binary']['equal'], no_yes['binary']['ai']],
                ax=axs[0, 1]).set_title("Only AI rationale shown")
    sns.barplot(x=['Human', 'Equal', 'AI'], y=[no_no['binary']['human'], no_no['binary']['equal'], no_no['binary']['ai']],
                ax=axs[0, 0]).set_title("No rationales shown")

    # Set the color of Human to green, equal to yellow and AI to red
    for ax in axs.flat:
        ax.patches[0].set_color('#a044ff')
        ax.patches[1].set_color('#FFC371')
        ax.patches[2].set_color('#FF5F6D')

    plt.tight_layout()
    plt.show()

    # Plot results in a 2x2 grid of bar charts of the normalized ratings: Human, AI
    _, axs = plt.subplots(2, 2, figsize=(8, 6))
    sns.barplot(x=['Human', 'AI'], y=[yes_yes['normalized']['human'], yes_yes['normalized']['ai']],
                ax=axs[1, 1]).set_title("Both rationales shown")
    sns.barplot(x=['Human', 'AI'], y=[yes_no['normalized']['human'], yes_no['normalized']['ai']],
                ax=axs[1, 0]).set_title("Only human rationale shown")
    sns.barplot(x=['Human', 'AI'], y=[no_yes['normalized']['human'], no_yes['normalized']['ai']],
                ax=axs[0, 1]).set_title("Only AI rationale shown")
    sns.barplot(x=['Human', 'AI'], y=[no_no['normalized']['human'], no_no['normalized']['ai']],
                ax=axs[0, 0]).set_title("No rationales shown")

    # Set the color of Human to green and AI to red
    for ax in axs.flat:
        ax.patches[0].set_color('#a044ff')
        ax.patches[1].set_color('#FF5F6D')

    plt.tight_layout()
    plt.show()


def _add_ratings(human: int, ai: int, comparison_dict: dict, scale: float = 5.0):
    comparison_dict['normalized']['human'] += float(human) / scale
    comparison_dict['normalized']['ai'] += float(ai) / scale


def _add_verdict(verdict: Verdict, comparison_dict: dict):
    if verdict == Verdict.HUMAN:
        comparison_dict['binary']['human'] += 1
    elif verdict == Verdict.AI:
        comparison_dict['binary']['ai'] += 1
    elif verdict == Verdict.EQUAL:
        comparison_dict['binary']['equal'] += 1


def __compare_dict_template() -> dict:
    return {
        "binary": {
            "human": 0,
            "ai": 0,
            "equal": 0,
        },
        "normalized": {
            "human": 0.0,
            "ai": 0.0,
        }
    }


def __parse_verdict_to_enum(verdict: str) -> Verdict:
    if verdict == 'Human':
        return Verdict.HUMAN
    elif verdict == 'AI':
        return Verdict.AI
    elif verdict == 'No preference':
        return Verdict.EQUAL
    else:
        raise ValueError("Unknown verdict: {}".format(verdict))


if __name__ == "__main__":
    analyze_results()
