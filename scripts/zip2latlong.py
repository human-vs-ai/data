
import math
import pandas as pd
import pgeocode
import os
from typing import Dict, List, Tuple

__DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "data", "HousesInfo.txt")
__nomi = pgeocode.Nominatim('us')


def convert_zip_to_latlong(zipcode: str, display: bool = False) -> Tuple[float, float]:
    """
    Convert a zipcode to a latitude/longitude pair using pgeocode.

    Args:
        zipcode (str): zipcode to convert
        display (bool, optional): displays the data -> by default disabled (False)

    Returns:
        Tuple[float, float]: _description_
    """
    nomi = pgeocode.Nominatim('us')
    df: pd.DataFrame = nomi.query_postal_code(zipcode)

    if display:
        print('Zipcode: ', df.postal_code)
        print('Latitude: ', df.latitude)
        print('Longitude: ', df.longitude)

    return (df.latitude, df.longitude)


def get_lat_long_data_from_zipcodes() -> Dict[int, Tuple[float, float]]:
    """
    Get latitude/longitude data from zipcodes in the data file.
    Uses pgeocode to convert zipcodes to latitude/longitude pairs.

    Returns:
        Dict[int, Tuple[float, float]]: House number mapped to latitude/longitude pair
    """
    lat_long_data: Dict[int, Tuple[float, float]] = {}

    with open(__DATA_FILE, "r") as f:
        house_nr: int = 1
        for line in f:
            values: List[str] = line.strip().split()

            # only process lines with 5 columns
            if len(values) == 5:
                # zipcodes are in the 4th column
                zipcode: str = values[3]

                df: pd.DataFrame = __nomi.query_postal_code(zipcode)

                # skip if no latitude/longitude data is available
                if df.latitude is not None and not math.isnan(df.latitude) and df.longitude is not None and not math.isnan(df.longitude):
                    lat_long_data[house_nr] = (df.latitude, df.longitude)

            house_nr += 1

    return lat_long_data


if __name__ == '__main__':
    print(get_lat_long_data_from_zipcodes())
