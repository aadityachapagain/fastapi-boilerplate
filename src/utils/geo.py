import logging
import httpx
from typing import Dict, Tuple, Optional

from src.config import settings
from src.db.models.items import Direction

logger = logging.getLogger(__name__)


async def fetch_zipcode_data(postcode: str) -> Optional[Dict]:
    """Fetch location data for a US zipcode from external API.
    
    Args:
        postcode: The US postal code to lookup
        
    Returns:
        dict: Location data including latitude and longitude
        None: If the request fails or postcode is invalid
    """
    url = f"{settings.ZIP_API_BASE_URL}/{postcode}"
    logger.info(f"Fetching zipcode data from: {url}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch zipcode data: {response.status_code}")
                return None
            
            data = response.json()
            logger.debug(f"Received zipcode data: {data}")
            
            # Extract coordinates from the response
            # The API returns data in a specific format we need to parse
            places = data.get("places", [])
            if not places:
                logger.warning(f"No location data found for postcode: {postcode}")
                return None
            
            place = places[0]
            
            return {
                "latitude": float(place.get("latitude")),
                "longitude": float(place.get("longitude")),
                "place_name": place.get("place name"),
                "state": place.get("state"),
                "state_abbreviation": place.get("state abbreviation")
            }
    except Exception as e:
        logger.error(f"Error fetching zipcode data: {str(e)}")
        return None


def calculate_direction(lat: float, lon: float) -> Direction:
    """Calculate direction from New York based on coordinates.
    
    Args:
        lat: Latitude of the location
        lon: Longitude of the location
        
    Returns:
        Direction: Direction enum value (NE, NW, SE, SW)
    """
    ny_lat = settings.NY_LATITUDE
    ny_lon = settings.NY_LONGITUDE
    
    # Determine north/south component
    ns = "N" if lat >= ny_lat else "S"
    
    # Determine east/west component
    ew = "E" if lon >= ny_lon else "W"
    
    direction = f"{ns}{ew}"
    
    logger.debug(f"Calculated direction from NY: {direction}")
    
    direction_map = {
        "NE": Direction.NORTHEAST,
        "NW": Direction.NORTHWEST,
        "SE": Direction.SOUTHEAST,
        "SW": Direction.SOUTHWEST
    }
    
    return direction_map[direction].value