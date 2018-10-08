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
  username="YOUR-NLU-USERNAME",
  password="YOUR-PASSWORD",
  version="2017-02-27")

natural_language_classifier = NaturalLanguageClassifierV1(
  username='YOUR_NLC_USERNAME',
  password='YOUR-PASSWORD'
)

consumer_key = 'TWITTER-CONSUMER-KEY'
consumer_secret = 'TWITTER-CONSUMER-SECRET-KEY'
access_token = 'TWITTER-APP-ACCESS-TOKEN'
access_secret = 'TWITTER-APP-ACCESS-SECRET'
 
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
      disgust = ""+json.dumps(response["emotion"]["targets"][0]["emotion"]["disgust"])
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
        host='0.0.0.0', port=port, debug=True
    )
