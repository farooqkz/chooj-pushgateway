from flask import Flask # <3?
from flask import request
from flask import abort
from flask import g
import requests
import sys

app = Flask(__name__)

def send_request(pushkey, data=None):
    if not pushkey.startswith("https://push.kaiostech.com:8443/wpush"):
        return False
    try:
        response = requests.post(pushkey, data=data)
    except:
        return False
    if not response.ok:
        print(response.text, file=sys.stderr)
    return False if response.ok else pushkey

@app.route("/notify", methods=("POST", ))
def notify():
    if not request.is_json:
        abort(404)
    pushkeys = map(
        lambda device: device["pushkey"],
        request.json["notification"]["devices"]
    )
    rejected = filter(None, map(send_request, zip(pushkeys, request.json))
    return {"rejected": list(rejected)}
