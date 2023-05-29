import json
import math
import os
from typing import List
import zip2latlong

__DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "data", "HousesInfo.txt")

__PROMPT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "data", "prompts", "1st_stage")

house_description: str = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."


def generate_prompts():

    # if __PROMPT_FOLDER does not exist, create it
    if not os.path.exists(__PROMPT_FOLDER):
        os.makedirs(__PROMPT_FOLDER)

    with open(__DATA_FILE, "r") as f:
        house_nr: int = 1
        for line in f:
            values: List[str] = line.strip().split()

            # only process lines with 5 columns
            if len(values) == 5:
                bedrooms: str = values[0]
                bathrooms: str = values[1]
                sq_ft_str: str = values[2]
                zipcode: str = values[3]

                lat, long = zip2latlong.convert_zip_to_latlong(zipcode)

                # skip if no latitude/longitude data is available
                if lat is not None and not math.isnan(lat) and long is not None and not math.isnan(long):
                    prompt = create_json_prompt(
                        house_nr, lat, long, bedrooms, bathrooms, sq_ft_str)

                    # save prompt to .json file in __PROMPT_FOLDER with name <house_nr>.json
                    with open(os.path.join(__PROMPT_FOLDER, str(house_nr) + ".json"), "w") as f:
                        json.dump(prompt, f, indent=2)

            house_nr += 1


def create_json_prompt(house_nr: int, lat: float, long: float, bedrooms: str, bathrooms: str, sq_ft: str, house_description: str = house_description):

    prompt_template = {
        "view": {
            "type": "view.list",
            "items": [
                {
                    "type": "view.markdown",
                    "content": "# House price estimating"
                },
                {
                    "type": "view.text",
                    "label": "House description:",
                    "content": house_description
                },
                {
                    "type": "view.labeled-list",
                    "items": [
                        {
                            "label": "Number of bedrooms:",
                            "content": {
                                "type": "view.text",
                                "content": bedrooms,
                            }
                        },
                        {
                            "label": "Number of bathrooms:",
                            "content": {
                                "type": "view.text",
                                "content": bathrooms,
                            }
                        },
                        {
                            "label": "Surface area (in sq. ft):",
                            "content": {
                                "type": "view.text",
                                "content": sq_ft,
                            }
                        }
                    ]
                },
                {
                    "type": "view.image",
                    "url": "https://raw.githubusercontent.com/emanhamed/Houses-dataset/master/Houses%20Dataset/" + str(house_nr) + "_frontal.jpg",
                    "label": "Frontal view:",
                    "noBorder": True,
                    "maxWidth": 500
                },
                {
                    "type": "view.image",
                    "url": "https://raw.githubusercontent.com/emanhamed/Houses-dataset/master/Houses%20Dataset/" + str(house_nr) + "_kitchen.jpg",
                    "label": "Kitchen:",
                    "noBorder": True,
                    "maxWidth": 500
                },
                {
                    "type": "view.image",
                    "url": "https://raw.githubusercontent.com/emanhamed/Houses-dataset/master/Houses%20Dataset/" + str(house_nr) + "_bedroom.jpg",
                    "label": "Bedroom:",
                    "noBorder": True,
                    "maxWidth": 500
                },
                {
                    "type": "view.image",
                    "url": "https://raw.githubusercontent.com/emanhamed/Houses-dataset/master/Houses%20Dataset/" + str(house_nr) + "_bathroom.jpg",
                    "label": "Bathroom:",
                    "noBorder": True,
                    "maxWidth": 500
                },
                {
                    "type": "view.map",
                    "label": "Map of the area (zipcode 85255):",
                    "center": str(lat) + "," + str(long),
                    "zoom": 14
                },
                {
                    "type": "view.markdown",
                    "content": "### 1. How much would you estimate this house to cost?"
                },
                {
                    "type": "field.radio-group",
                    "options": [
                        {
                            "label": "$0 - $100K",
                            "value": "0-100"
                        },
                        {
                            "label": "$100K - $200K",
                            "value": "100-200"
                        },
                        {
                            "label": "$200K - $300K",
                            "value": "200-300"
                        },
                        {
                            "label": "$300K - $400K",
                            "value": "300-400"
                        },
                        {
                            "label": "$400K - $500K",
                            "value": "400-500"
                        },
                        {
                            "label": "$500K - $600K",
                            "value": "500-600"
                        },
                        {
                            "label": "$600K - $700K",
                            "value": "600-700"
                        },
                        {
                            "label": "$700K - $850K",
                            "value": "700-850"
                        },
                        {
                            "label": "$850K - $1M",
                            "value": "850-1"
                        },
                        {
                            "label": "$1M - $1.25M",
                            "value": "1-1.25"
                        },
                        {
                            "label": "$1.25M - $1.5M",
                            "value": "1.25-1.5"
                        },
                        {
                            "label": "$1.5M - $1.75M",
                            "value": "1.5-1.75"
                        },
                        {
                            "label": "$1.75M - $2M",
                            "value": "1.75-2"
                        },
                        {
                            "label": "$2M+",
                            "value": "2+"
                        }
                    ],
                    "data": {
                        "type": "data.output",
                        "path": "price"
                    },
                    "validation": {
                        "hint": "Please, choose a price range",
                        "type": "condition.required"
                    }
                },
                {
                    "type": "view.markdown",
                    "content": "### 2. Provide a 2-3 sentence rationale on why you chose this price."
                },
                {
                    "type": "field.textarea",
                    "rows": 3,
                    "placeholder": "Enter your text here",
                    "data": {
                        "type": "data.output",
                        "path": "rationale"
                    },
                    "validation": {
                        "hint": "Please, provide your rationale",
                        "type": "condition.required"
                    }
                },
                {
                    "type": "view.markdown",
                    "content": "### 3. How accurate do you think your prediction is?"
                },
                {
                    "type": "field.radio-group",
                    "label": "Choose one answer",
                    "options": [
                        {
                            "label": "Not at all",
                            "value": "Not at all"
                        },
                        {
                            "label": "A little",
                            "value": "A little"
                        },
                        {
                            "label": "Very",
                            "value": "Very"
                        },
                        {
                            "label": "Extremely",
                            "value": "Extremely"
                        }
                    ],
                    "data": {
                        "type": "data.output",
                        "path": "accuracy"
                    },
                    "validation": {
                        "hint": "Please, choose an accuracy",
                        "type": "condition.required"
                    }
                }
            ]
        },
        "plugins": []
    }

    return prompt_template


if __name__ == '__main__':
    generate_prompts()
