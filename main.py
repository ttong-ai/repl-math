import datetime
from flask import Flask, request
import json
import pytz
from weather import get_weather


app = Flask(__name__)


@app.route('/')
def hello_world():
  return "Hello world!"


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
    try:
      city = float(intent_info.get('parameters').get('geo-city').get("resolvedValue"))
    except Exception:
      try:
        city = float(intent_info.get('parameters').get('geo-city').get("originalValue"))
      except Exception:
        city = "Santa Clara"
        exception_city = True
    try:
      state = float(intent_info.get('parameters').get('geo-state').get("resolvedValue"))
    except Exception:
      try:
        state = float(intent_info.get('parameters').get('geo-state').get("originalValue"))
      except Exception:
        state = "California"
        exception_state = True
    try:
      country = float(intent_info.get('parameters').get('geo-country').get("resolvedValue"))
    except Exception:
      try:
        country = float(intent_info.get('parameters').get('geo-country').get("originalValue"))
      except Exception:
        country = "USA"
        exception_country = True
    res = get_weather(city, state, country)
    message =[]
    message.append(f"In {city}, " if not exception_city else f"If you meant {city}, ")
    message.append(f"{state}, " if not exception_state else f"{state} (I suppose), ")
    if country != "USA":
      message.append(f"{country}, " if not exception_country else f"{country} (I suppose), ")
    try:
      message.append(f"it has now {res['list'][0]['weather']['description']}. ")
    except Exception:
      print(json.dumps(res, indent=2))
    try:
      message.append(
        f"The current temperature is {res['list'][0]['main']['temp']-273.15}."
      )
    except Exception:
      print(json.dumps(res, indent=2))

    return {
      "fulfillmentResponse": {
        "messages": [
          {
            "text": {
              "text": message
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
