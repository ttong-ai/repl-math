import aiohttp
import json
from utils import create_logger, serializable

logger = create_logger(__name__, "debug")


def get_weather(city: str, state: str = None, country: str = None):
  """Get weather from WeatherMap API"""

  if not isinstance(city, str) or not city:
    print("'city' needs to be non-empty string")
    return

  if not state:
    state = "California"
  if not country:
    country = "USA"

  async with aiohttp.ClientSession() as session:
    try:
      url = "https://community-open-weather-map.p.rapidapi.com/forecast"
      headers = {
        "X-RapidAPI-Host": "community-open-weather-map.p.rapidapi.com",
        "X-RapidAPI-Key": "507107586amshfe9f08df085254ap12c25bjsn701289ee7b56",
      }
      params = {"q": ",".join([city, state, country])}
      async with session.get(url=url, params=params, headers=headers) as resp:
        status_code = resp.status
        r = await resp.read()
        logger.debug(json.dumps(serializable(r), indent=2))
        if 200 <= status_code < 300:
            try:
                results = json.loads(r)
            except TypeError:
                logger.error(f"None response received. Check service health at: {url}")
            except json.decoder.JSONDecodeError as e:
                logger.error(f"JSON decoder error: {e}")
                raise json.decoder.JSONDecodeError(e)
            return results
        else:
            logger.error(f"Error response from weather map API - Status Code: {status_code}")
    except aiohttp.ClientConnectorError as e:
      logger.error(f"Connection error from weather map API: {e}")
    except Exception as e:
      logger.error(f"Other exception during weather map query: {e}")
