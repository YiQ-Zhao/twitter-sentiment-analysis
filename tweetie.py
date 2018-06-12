import sys
import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import time


def loadkeys(filename):
    """"
    load twitter api keys/tokens from CSV file with form
    consumer_key, consumer_secret, access_token, access_token_secret
    """
    with open(filename) as f:
        items = f.readline().strip().split(', ')
        return items


def authenticate(twitter_auth_filename):
    """
    Given a file name containing the Twitter keys and tokens,
    create and return a tweepy API object.
    """
    keys = loadkeys(twitter_auth_filename)
    auth = tweepy.OAuthHandler(keys[0],keys[1])
    auth.set_access_token(keys[2], keys[3])

    api = tweepy.API(auth)
    return api


def fetch_tweets(api,name):
    """
    Given a tweepy API object and the screen name of the Twitter user,
    create a list of tweets where each tweet is a dictionary with the
    following keys:

       id: tweet ID
       created: tweet creation date
       retweeted: number of retweets
       text: text of the tweet
       hashtags: list of hashtags mentioned in the tweet
       urls: list of URLs mentioned in the tweet
       mentions: list of screen names mentioned in the tweet
       score: the "compound" polarity score from vader's polarity_scores()

    Return a dictionary containing keys-value pairs:

       user: user's screen name
       count: number of tweets
       tweets: list of tweets, each tweet is a dictionary

    For efficiency, create a single Vader SentimentIntensityAnalyzer()
    per call to this function, not per tweet.
    """
    # user.statuses.count
    user = api.get_user(name)
    total_info = {}
    total_info['user'] = name
    total_info['count'] = user.statuses_count

    tweet_list = []
    for status in tweepy.Cursor(api.user_timeline, id=name).items(100): # what's the amount here?
        sid = SentimentIntensityAnalyzer()
        score = sid.polarity_scores(status._json['text'])
        tweet_list.append({'id': status._json['id'],
                           'created': status._json['created_at'],
                           'retweeted': status._json['retweet_count'],
                           'text': status._json['text'],
                           'hashtags': status._json['entities']['hashtags'],
                           'urls': status._json['entities']['urls'],
                           'mentions': status._json['entities']['user_mentions'],
                           'score': score['compound']})
    total_info['tweets'] = tweet_list

    return total_info

def fetch_following(api,name):
    """
    Given a tweepy API object and the screen name of the Twitter user,
    return a a list of dictionaries containing the followed user info
    with keys-value pairs:

       name: real name
       screen_name: Twitter screen name
       followers: number of followers
       created: created date (no time info)
       image: the URL of the profile's image

    To collect data: get a list of "friends IDs" then get
    the list of users for each of those.
    """

    friend_info = []
    for friend in tweepy.Cursor(api.friends, id  = name).items():
        friend_info.append({'name': friend._json['name'],
                            'screen_name': friend._json['screen_name'],
                            'followers': friend._json['followers_count'],
                            'created': time.strftime('%Y-%m-%d', time.strptime(friend._json['created_at'],'%a %b %d %H:%M:%S +0000 %Y')),
                            'image': friend._json['profile_image_url']})
    return friend_info
