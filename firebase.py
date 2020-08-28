import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import requests
import time
import json
url = ""
headers = {}
currentComments = {}
miroKeyMap = {}
n = 0


def init():
    global url, headers, currentComments, miroKeyMap, n
    cred = credentials.Certificate(
        './yamlab-3f326-firebase-adminsdk-azh23-ab74288e4b.json')

    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://yamlab-3f326.firebaseio.com/',
        'databaseAuthVariableOverride': {
            'uid': 'my-service-worker'
        }
    })
    url = "https://api.miro.com/v1/boards/o9J_km0rXko%3D/widgets"

    headers = {"authorization": "Bearer 894c7ea4-18a7-4d25-b2fa-e6d0f2bf6c5d"}
    heejunComment = db.reference('/heejun').get()
    n = len(heejunComment)
    currentComments = heejunComment
    for i, (key, value) in enumerate(currentComments.items()):
        x = i % 5
        y = (i-i % 5)/5
        mirokey = addComment(value["content"], x, y)
        miroKeyMap.update([(key, mirokey)])
    print(miroKeyMap)


def addComment(text, x, y):
    data = {
        "type": "sticker",
        "x": x*250,
        "y": y*250,
        "scale": 1,
        "height": 228.0,
        "width": 199.0,
        "style": {
            "backgroundColor": "#b384bb",
            "fontFamily": "OpenSans",
            "fontSize": 14,
            "textAlign": "left",
            "textAlignVertical": "middle"
        },
        "text": text
    }
    respond = requests.request("POST", url, headers=headers, json=data)
    return json.loads(respond.text)["id"]


def removeComment(mirokey):
    widgetUrl = "https://api.miro.com/v1/boards/o9J_km0rXko%3D/widgets/"+mirokey
    response = requests.request(
        "DELETE", widgetUrl, headers=headers)
    print(response.text)


init()
while True:
    time.sleep(5)
    newComments = db.reference('/heejun').get()
    commentsToAdd = newComments.keys()-currentComments.keys()
    commentsToRemove = currentComments.keys()-newComments.keys()
    n = n+len(commentsToAdd)
    for i, (key) in enumerate(commentsToAdd):
        x = (n+i) % 5
        y = (n+i-x)/5
        mirokey = addComment(newComments[key]["content"], x, y)
        miroKeyMap.update([(key, mirokey)])
    for i, (key) in enumerate(commentsToRemove):
        removeComment(miroKeyMap[key])
        del miroKeyMap[key]
    currentComments = newComments
