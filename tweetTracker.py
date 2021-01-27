import tweepy
import requests
import time

class TweetNotifier:
    #Bearer Token AAAAAAAAAAAAAAAAAAAAAJkILwEAAAAAzxJirUwxP%2B27yMFSXnzGSYm4pFM%3Df25Q7kGjjEPjkU6upvpOGv772B2eHpsBJpJylSrZ6kgNLZM36J
    auth = None
    api = None

    def __init__(self, webhookUrl, tweepyKeys):
        self.discordWebhookUrl = webhookUrl
        self.auth = tweepy.AppAuthHandler(tweepyKeys[0], tweepyKeys[1])
        self.api = tweepy.API(self.auth)

    def notifyDiscord(self, webhookUrl, tweet):

        requests.post(webhookUrl, json=
            {
                "content": "https://twitter.com/twitter/statuses/" + str(tweet.id),
                "username": "SpaceX Tweet",
                "avatar_url": "https://i.bunnyslippers.dev/pye3c828.png"
            })

    lastTweet = None

    def run(self):
        print("--Tweet Tracker--")
        
        print("Grabbing Last Tweet...")
        for tweet in self.api.user_timeline(screen_name = "elonmusk", count = 1):
            if not self.lastTweet:
                print("Last Tweet loaded.")
                self.lastTweet = tweet
            elif self.lastTweet.id != tweet.id:
                print("Current Tweet differs from previous Tweet.")
                self.lastTweet = tweet
                self.notifyDiscord(self.discordWebhookUrl, tweet)
            else:
                print("Last Tweet Identical")
            print(tweet.id)
        #time.sleep(30)
        print("Done.\n")