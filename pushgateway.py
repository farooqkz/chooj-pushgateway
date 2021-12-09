from flask import Flask  # <3?
from flask import request
from flask import abort
from flask import g
from pywebpush import webpush
from pywebpush import WebPushException
from py_vapid import Vapid01
import requests
import json

app = Flask(__name__)

def get_vapid():
    vapid = getattr(g, "vapid", None)
    if vapid is None:
        pub = None
        priv = None
        with open(".vapid") as fp:
            pub = fp.readline()
            priv = fp.readline()
        priv = Vapid01.from_string(priv)
        vapid = dict(pub=pub, priv=priv)
        setattr(g, "vapid", vapid)
    return vapid

def push(subscription, data):
    endpoint = subscription.get("endpoint", "")
    if not endpoint.startswith("https://push.kaiostech.com:8443/wpush"):
        print("Invalid endpoint:", endpoint)
        return False
    privkey = get_vapid()["priv"]
    vapid_claims = dict(sub="mailto:fk" + "z" + "@riseup.net")
    try:
        webpush(
            subscription_info=subscription,
            data=json.dumps(data),
            vapid_private_key=privkey,
            vapid_claims=vapid_claims,
            content_encoding="aesgcm",
            ttl=120,
        )
    except WebPushException as e:
        print(e)
        if e.response and e.response.json():
            print(e.response.json())
        return False
    except Exception as e:
        print(e)
        return False
    return True

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
        try:
            subscr = json.loads(pushkey)
            if not push(subscr, request.json["notification"]):
                rejected.append(pushkey)
        except:
            rejected.append(pushkey)
    print("REJECTED:", rejected)
    return {"rejected": rejected}
