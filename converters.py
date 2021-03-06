# Change stuff to other stuff

import json
from google.protobuf.json_format import MessageToJson
from datetime import datetime
import requests
import codecs


# Convert Unix timestamp to US Date Format, if desired
def convert_date(unix_timestamp):
    date = int(unix_timestamp)
    full_date = datetime.utcfromtimestamp(date).strftime('%m-%d-%Y %H:%M:%S')
    return full_date


# Convert gRPC response to json, then from json to dict, if desired.
# This automatically does some encoding and decoding, though.
def response_to_dict(response):
    response = MessageToJson(response)
    response = json.loads(response)
    return response

# Convert satoshis to USD
def btc_to_usd(satoshis):
    api = "https://api.coinbase.com/v2/prices/BTC-USD/buy"
    raw_data = requests.get(api).json()
    price = float(raw_data['data']['amount'])
    btc_amt = int(satoshis) * .00000001
    return(price * btc_amt)
