from flask import Flask # <3?
from flask import request
from flask import abort
from flask import g
import requests
import sys

app = Flask(__name__)

LOG_FILE = open("log", "at")

def send_request(pushkey, data=None):
    if not pushkey.startswith("https://push.kaiostech.com:8443/wpush"):
        print("pushkey is", pushkey, "ignoring...", file=LOG_FILE)
        return False
    try:
        response = requests.post(pushkey, data=data)
    except:
        return False
    if not response.ok:
        print(response.text, file=LOG_FILE)
    return False if response.ok else pushkey

@app.route("/_matrix/push/v1/notify", methods=("POST", ))
def notify():
    if not request.is_json:
        print("Request is not JSON:", request, file=LOGFILE)
        abort(404)
    pushkeys = tuple(map(
        lambda device: device["pushkey"],
        request.json["notification"]["devices"]
    ))
    rejected = filter(None, map(send_request, pushkeys, (request.json, ) * len(pushkeys)))
    return {"rejected": list(rejected)}
