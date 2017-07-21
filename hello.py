from flask import Flask, render_template, request, jsonify
from tweepy import Stream
import tweepy
import json
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from watson_developer_cloud import NaturalLanguageClassifierV1
from watson_developer_cloud import NaturalLanguageUnderstandingV1
import watson_developer_cloud.natural_language_understanding.features.v1 as Features
import os

natural_language_understanding = NaturalLanguageUnderstandingV1(
  username="9177bd6a-79ea-4f59-b49c-a72f8c7bed55",
  password="ZxwsHp5p2ghv",
  version="2017-02-27")

natural_language_classifier = NaturalLanguageClassifierV1(
  username='7bf57131-5ef2-465d-a551-2ed9ceeb0b60',
  password='dEPUKBrCDdtd'
)

consumer_key = 'owWHovWf0IWO1Ts48JgOljrmt'
consumer_secret = 'zN9OSph965F3hKstMm8A530dWaHjrQTd7OtPJVmYinEIySHqin'
access_token = '3169194486-gTFZxAfzsMyS6R0g56WUlDB0fPoNScWyi2ojmnH'
access_secret = '4nFFZF52bsQQNXoz2LONX77r6OxudliKPGDt11WCS1UcN'
 
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth, wait_on_rate_limit=True)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tweet')
def tweet():
  a = request.args.get('a', 0, type=str)
  for status in tweepy.Cursor(api.search, q=a).items():
    if "RT @" not in status.text:
      classes = natural_language_classifier.classify("359f3fx202-nlc-149364", status.text)
      response = natural_language_understanding.analyze(
              text=status.text,
              features=[
                Features.Sentiment(
                  targets=[a]
                ),
                Features.Entities(
                  limit=1
                ),
                Features.Emotion(
                  targets=[a]
                )
              ]
            )
      sent = ""+json.dumps(response["sentiment"]["targets"][0]["label"])
      typ = ""+json.dumps(classes['top_class'])
      sad = ""+json.dumps(response["emotion"]["targets"][0]["emotion"]["sadness"])
      joy = ""+json.dumps(response["emotion"]["targets"][0]["emotion"]["joy"])
      fear = ""+json.dumps(response["emotion"]["targets"][0]["emotion"]["fear"])
      disgust = 100*float(json.dumps(response["emotion"]["targets"][0]["emotion"]["disgust"]))
      anger = ""+json.dumps(response["emotion"]["targets"][0]["emotion"]["anger"])
      entity = json.dumps(response["entities"][0]["text"])+"("+json.dumps(response["entities"][0]["type"])+") - "+json.dumps(response["entities"][0]["relevance"])
      return jsonify(result = status.text,
        type = typ,
        sent = sent,
        sad = sad,
        joy = joy,
        fear = fear,
        disgust = disgust,
        anger = anger,
        entity = entity
        )

port = int(os.getenv('PORT', 8080))
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',port=port,debug=True
    )
