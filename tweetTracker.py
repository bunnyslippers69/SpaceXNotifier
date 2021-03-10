import tweepy
import requests
import time

class TweetNotifier:
    #Bearer Token AAAAAAAAAAAAAAAAAAAAAJkILwEAAAAAzxJirUwxP%2B27yMFSXnzGSYm4pFM%3Df25Q7kGjjEPjkU6upvpOGv772B2eHpsBJpJylSrZ6kgNLZM36J
    auth = None
    api = None
    profile = None

    def __init__(self, webhookUrl, tweepyKeys, profile = None):
        self.discordWebhookUrl = webhookUrl
        self.auth = tweepy.AppAuthHandler(tweepyKeys[0], tweepyKeys[1])
        self.api = tweepy.API(self.auth)
        self.profile = profile

    def notifyDiscord(self, webhookUrl, tweet):

        requests.post(webhookUrl, json=
            {
                "content": "https://twitter.com/twitter/statuses/" + str(tweet.id),
                "username": "SpaceX Tweet",
                "avatar_url": "https://i.bunnyslippers.dev/pye3c828.png"
            })

    lastTweet = None

    def run(self):
        print("--Tweet Tracker Start--")
        
        if self.profile != None:
            for tweet in self.api.user_timeline(screen_name = self.profile, count = 1):
                if not self.lastTweet:
                    self.lastTweet = tweet
                    break
                elif self.lastTweet.id != tweet.id:
                    self.lastTweet = tweet
                    self.notifyDiscord(self.discordWebhookUrl, tweet)
                    break
        else:
            for tweet in self.api.list_timeline(list_id = "1360995960860590081", count = 1, include_rts=False):
                if not self.lastTweet:
                    self.lastTweet = tweet
                elif self.lastTweet.id != tweet.id:
                    self.lastTweet = tweet
                    self.notifyDiscord(self.discordWebhookUrl, tweet)

        #time.sleep(30)
        print("--Tweet Tracker Done--")