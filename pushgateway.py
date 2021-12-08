from flask import Flask  # <3?
from flask import request
from flask import abort
import requests

app = Flask(__name__)


def send_request(pushkey, data=None):
    if not pushkey.startswith("https://push.kaiostech.com:8443/wpush"):
        return False
    try:
        response = requests.post(pushkey, data=data)
    except:
        return False
    return False if response.ok else pushkey


@app.route("/_matrix/push/v1/notify", methods=("POST",))
def notify():
    if not request.is_json:
        abort(404)
    if not isinstance(request.json.get("notification"), dict):
        abort(400)

    pushkeys = map(
        lambda device: device["pushkey"],
        request.json["notification"]["devices"],
    )
    request.json["notification"].pop("devices")
    rejected = list()
    for pushkey in pushkeys:
        if not send_request(pushkey, request.json["notification"]):
            rejected.append(pushkey)
    return {"rejected": rejected}
