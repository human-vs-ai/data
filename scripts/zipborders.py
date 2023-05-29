import json
from typing import List
import uszipcode

# Create an instance of the SearchEngine
search = uszipcode.SearchEngine(
    simple_or_comprehensive=uszipcode.SearchEngine.SimpleOrComprehensiveArgEnum.comprehensive)


def get_zipcode_bounds(zipcode: str) -> List[str]:
    """
    Get the polygon coordinates for a ZIP code.
    Comprehensive database from uszipcode is used.

    Args:
        zipcode (str): the zipcode, e.g. 85255

    Returns:
        List[str]: polygon coordinates, e.g. ['33.687861,-111.809705', '33.687861,-111.809705', ...]
    """

    # Search for the ZIP code
    result: uszipcode.model.ComprehensiveZipcode = search.by_zipcode(zipcode)

    # Retrieve the polygon latitude and longitude values
    polygon = result.polygon

    # Print the polygon coordinates
    points = []
    for lat, lng in polygon:
        points.append(f"{lat},{lng}")

    return points