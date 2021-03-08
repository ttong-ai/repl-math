import datetime
from flask import Flask, request
import json
import pytz
from utils import create_logger, ifnone
from weather import get_weather

logger = create_logger(__name__, "info")

app = Flask(__name__)


@app.route('/')
def hello_world():
  return "Hello World!"


@app.route('/webhook', methods=['POST'])
def webhook():
  req = request.get_json(silent=True, force=True)
  print(json.dumps(req, indent=2))

  intent_info = req.get("intentInfo")
  fulfillment_info = req.get("fulfillmentInfo")
  session_info = req.get("sessionInfo")

  intent = intent_info.get("displayName")
  tag = fulfillment_info.get("tag")

  if tag == "add_two_numbers":
    sum = 0
    exception = False

    try:
      num1 = float(intent_info.get('parameters').get('number1').get("resolvedValue"))
    except Exception:
      num1 = 0
      exception = True

    try:
      num2 = float(intent_info.get('parameters').get('number2').get("resolvedValue"))
    except Exception:
      num2 = 0
      exception = True

    sum = str(num1 + num2)
    print('here num1 = {0}'.format(num1))
    print('here num2 = {0}'.format(num2))
    return {
      "fulfillmentResponse": {
        "messages": [
          {
            "text": {
              "text": [
                f"I got the total as {sum}" if not exception 
                else f"I might have missed something, but I got {sum}"]
            }
          }
        ],
      },
      "sessionInfo": session_info
    }

  elif tag == "get_time":
    utc_now = pytz.utc.localize(datetime.datetime.utcnow())
    pst_now = utc_now.astimezone(pytz.timezone("America/Los_Angeles"))
    return {
      "fulfillmentResponse": {
        "messages": [
          {
            "text": {
              "text": [f"It's {pst_now.strftime('%H:%M:%S')} in California."]
            }
          }
        ],
      },
      "sessionInfo": session_info
    }

  elif tag == "get_weather":
    exception_city, exception_state, exception_country = False, False, False
    city = session_info.get('parameters').get('geo-city')
    if isinstance(city, list):
      city = city[0]
    state = session_info.get('parameters').get('geo-state')
    if isinstance(state, list):
      state = state[0]
    country = session_info.get('parameters').get('geo-country')
    if isinstance(country, list):
      country = country[0]

    if not city:
      city = "Santa Clara"
      exception_city = True
    elif not state and not country:
      state, country = "California", "US"
      exception_state, expception_country = True, True
    elif state and not country:
      pass
    elif not state and country:
      pass

    res = get_weather(city, state, country)
    if res.get("city"):
      country = res["city"]["country"]
      exception_country = False
      if country != "US":
        state = None

    message =[]
    message.append(f"In {city}, " if not exception_city else f"If you meant {city}, ")
    if state:
      message.append(f"{state}, " if not exception_state else f"{state} (I suppose), ")
    if country:
      message.append(f"{country}, " if not exception_country else f"{country} (I suppose), ")
    try:
      if "clouds" in res['list'][0]['weather'][0]['description'].lower():
        message.append(f"it has some {res['list'][0]['weather'][0]['description']} and ")
      elif "sky" in res['list'][0]['weather'][0]['description'].lower():
        message.append(f"it has a {res['list'][0]['weather'][0]['description']} and ")
      else:
        message.append(f"it has {res['list'][0]['weather'][0]['description']} and ")
    except Exception:
      logger.debug(json.dumps(res, indent=2))
    try:
      message.append(
        f"the current temperature is {res['list'][0]['main']['temp']-273.15:.1f} °C."
      )
    except Exception:
      logger.debug(json.dumps(res, indent=2))

    return {
      "fulfillmentResponse": {
        "messages": [
          {
            "text": {
              "text": ["".join(message)]
            }
          }
        ],
      },
      "sessionInfo": session_info
    }

  else:
    return {
      "fulfillmentResponse": {
        "messages": [
          {
            "text": {
              "text": ["Sorry, didn't figure that out"]
            }
          }
        ],
      },
      "sessionInfo": session_info
    }
   

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)
