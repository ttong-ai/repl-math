import datetime
from flask import Flask, request
import json
import pytz


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
    num1 = float(intent_info.get('parameters').get('number1').get("resolvedValue"))
    num2 = float(intent_info.get('parameters').get('number2').get("resolvedValue"))
    sum = str(num1 + num2)
    print('here num1 = {0}'.format(num1))
    print('here num2 = {0}'.format(num2))
    return {
      "fulfillmentResponse": {
        "messages": [
          {
            "text": {
              "text": ["I got the total as " + sum]
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
