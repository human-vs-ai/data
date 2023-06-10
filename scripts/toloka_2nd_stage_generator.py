import itertools
import json
import math
import pandas as pd
import os
import zip2latlong
import zipborders
import copy

__RESPONSES_FOLDER = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "data", "responses")

__HUMAN_DATA_FILE = os.path.join(
    __RESPONSES_FOLDER, "filtered-stage-1-pool-2-06-06-2023.xls")

__AI_DATA_FILE = os.path.join(
    __RESPONSES_FOLDER, "filtered_prompts_AI_1st_stage.json")

__OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "data", "prompts", "2st_stage")


def generate_prompts():
    all_prompts = []

    if not os.path.exists(__OUTPUT_FOLDER):
        os.makedirs(__OUTPUT_FOLDER)

    if not os.path.exists(__HUMAN_DATA_FILE):
        print("Human data file not found: {}".format(__HUMAN_DATA_FILE))
        return

    if not os.path.exists(__AI_DATA_FILE):
        print("AI data file not found: {}".format(__AI_DATA_FILE))
        return

    ai_responses = dict()
    matching_ids = set()
    distinct_ids = set()

    # Load AI data
    with open(__AI_DATA_FILE, 'r') as f:
        ai_data = json.load(f)

        # Create a dictionary of identifiable AI responses such that IDs can easily be matched with human responses
        for ai_response in ai_data:
            ai_responses[ai_response['id']] = ai_response

    # Load human data
    df = pd.read_excel(__HUMAN_DATA_FILE)
    for _, row in df.iterrows():
        input_id = row['INPUT:id']
        input_price = row['INPUT:price']
        input_image_urls = row['INPUT:image_urls']
        input_n_bedrooms = row['INPUT:n_bedrooms']
        input_n_bathrooms = row['INPUT:n_bathrooms']
        input_surface_area_m2 = row['INPUT:surface_area_m2']
        input_surface_area_sq_ft = row['INPUT:surface_area_sq_ft']
        output_price = row['OUTPUT:price']
        output_rationale = row['OUTPUT:rationale']

        if input_id in ai_responses:
            matching_ids.add(input_id)

            # Generate a summmative prompt for the 2nd stage on both human and AI data
            print("Generating prompt for ID {}...".format(input_id))

            zipcode = ai_responses[input_id]["zipcode"]
            lat, long = zip2latlong.convert_zip_to_latlong(zipcode)
            coordinates = {
                "center": str(lat) + "," + str(long)
            }

            # skip if no latitude/longitude data is available
            if lat is not None and not math.isnan(lat) and long is not None and not math.isnan(long):
                # get the bounds of the zip code
                bounds = zipborders.get_zipcode_bounds(zipcode)

                # only process if bounds are available, at least more than 2 points (else it is a point or line)
                if bounds is not None and len(bounds) > 2:
                    coordinates["polygon"] = bounds
            else:
                print("\nNo latitude/longitude data available for zipcode {}".format(
                    zipcode))
                print("Could not generate prompt for ID {}\n".format(input_id))
                continue

            # TODO: Map prices to a more readable format (e.g. 1000 -> 1k, 1000000 -> 1M, etc.)
            # TODO: Map rationales to a complete markdown text of the whole section such that empty string means no advice and also properly shows no headers etc.
            prompt_data = {
                "input_values": {
                    "id": input_id,
                    "price": input_price,
                    "ai_price": format_price(str(ai_responses[input_id]["price_prediction_lower_bound"]) + " - " + str(ai_responses[input_id]["price_prediction_upper_bound"])),
                    "ai_advice": ai_responses[input_id]["rationale"],
                    "ai_advice_quality": ai_responses[input_id]["rationale_quality"],
                    "image_urls": json.loads(input_image_urls.replace('"{', '{').replace('}"', '}')),
                    "n_bedrooms": input_n_bedrooms,
                    "coordinates": coordinates,
                    "human_price": format_price(output_price),
                    "n_bathrooms": input_n_bathrooms,
                    "human_advice": output_rationale,
                    "surface_area_m2": input_surface_area_m2,
                    "surface_area_sq_ft": input_surface_area_sq_ft
                }
            }

            both_prompt = copy.deepcopy(prompt_data)

            ai_prompt = copy.deepcopy(prompt_data)
            ai_prompt["input_values"]["human_advice"] = ""

            human_prompt = copy.deepcopy(prompt_data)
            human_prompt["input_values"]["ai_advice"] = ""

            none_prompt = copy.deepcopy(prompt_data)
            none_prompt["input_values"]["ai_advice"] = ""
            none_prompt["input_values"]["human_advice"] = ""

            prompt = [
                both_prompt,
                ai_prompt,
                human_prompt,
                none_prompt
            ]

            all_prompts.append(prompt)

            # Write to file in JSON format in the output folder
            with open(os.path.join(__OUTPUT_FOLDER, str(input_id) + ".json"), 'w') as f:
                json.dump(prompt, f, indent=2)

            # print("Prompt for ID {} generated:\n{}\n".format(
            #     input_id, json.dumps(prompt, indent=4)))

        else:
            distinct_ids.add(input_id)

    # Write all prompts to a single file
    with open(os.path.join(__OUTPUT_FOLDER, "all_prompts.json"), 'w') as f:
        json.dump(list(itertools.chain(*all_prompts)), f, indent=2)

    print("\nSUMMARY")
    print("----------------------------------------")
    print("Number of matching IDs: {}".format(len(matching_ids)))
    print("Number of distinct IDs: {}".format(len(distinct_ids)))
    print("Total number of IDs: {}".format(
        len(matching_ids) + len(distinct_ids)))
    print("----------------------------------------")
    print("Matching IDs: {}".format(matching_ids))
    print("----------------------------------------")
    print("Distinct IDs: {}\n".format(distinct_ids))


def format_price(price: str) -> str:
    lower, upper = price.split("-")
    lower = lower.strip()
    upper = upper.strip()

    # Convert to float to check range representation of input
    lower_nr = float(lower)
    upper_nr = float(upper)

    # Format: DEFAULT
    lower_formatted = "$" + lower
    upper_formatted = "$" + upper

    # Format: MILLIONS
    if lower_nr <= 10:
        lower_formatted = f"${int(lower_nr * 1000000):,}"

    if upper_nr <= 10:
        upper_formatted = f"${int(upper_nr * 1000000):,}"

    # Format: THOUSANDS
    if lower_nr > 10 and lower_nr <= 1000:
        lower_formatted = f"${int(lower_nr * 1000):,}"

    if upper_nr > 10 and upper_nr <= 1000:
        upper_formatted = f"${int(upper_nr * 1000):,}"

    # Return in range format
    return lower_formatted + " - " + upper_formatted


if __name__ == '__main__':
    generate_prompts()
