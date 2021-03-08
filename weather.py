import json
import requests
from utils import create_logger, serializable

logger = create_logger(__name__, "info")


def get_weather(city: str, state: str = None, country: str = None):
  """Get weather from WeatherMap API"""

  if not isinstance(city, str) or not city:
    logger.error("'city' needs to be non-empty string")
    return

  if not state:
    state = "California"
  if not country:
    country = "USA"

  url = "https://community-open-weather-map.p.rapidapi.com/forecast"
  headers = {
    "X-RapidAPI-Host": "community-open-weather-map.p.rapidapi.com",
    "X-RapidAPI-Key": "507107586amshfe9f08df085254ap12c25bjsn701289ee7b56",
  }
  params = {"q": ",".join([city, state, country])}
  r = requests.get(url, params=params, headers=headers)
  try:
    # logger.debug(json.dumps(serializable(r), indent=2))
    res = r.json()
    print(json.dumps(res, indent=2))
  except TypeError:
      logger.error(f"None response received. Check service health at: {url}")
  except json.decoder.JSONDecodeError as e:
      logger.error(f"JSON decoder error: {e}")
      raise json.decoder.JSONDecodeError(e)
  return res
