from flask import Flask # <3?
from flask import request
from flask import abort
from flask import g
from datetime import datetime
import requests
import sys

app = Flask(__name__)

def send_request(pushkey):
    now = int(datetime.utcnow().timestamp())
    try:
        response = requests.put(pushkey, data=dict(version=now))
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
    rejected = list(filter(None, map(send_request, pushkeys)))
    return {"rejected": rejected}
