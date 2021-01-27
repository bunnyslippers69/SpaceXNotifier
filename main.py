import importlib
import threading
import time
import requests

discordWebhookUrl = ""
tweepyKeys = []

with open("config/discordWebhook.conf") as f:
    discordWebhookUrl = f.read()

with open("config/tweepyKeys.conf") as f:
    content = f.readlines()
    content = [x.strip() for x in content] 
    tweepyKeys = content

#Import modules'
rc = importlib.import_module("roadClosures")
tn = importlib.import_module("tweetTracker")
tfr = importlib.import_module("tfrTracker")

#Time to sleep between actions
sleep = 15

closureNotifier = rc.ClosureNotifier(discordWebhookUrl)
tweetNotifier = tn.TweetNotifier(discordWebhookUrl, tweepyKeys)
tfrNotifier = tfr.TfrNotifier(discordWebhookUrl)

#Road Closures - https://reqbin.com/kroamhug
#Tweet Notification - https://reqbin.com/ydkyw5k2

while True:
    print("\n" + str(time.ctime()))
    closureNotifier.run()
    tweetNotifier.run()
    tfrNotifier.run()
    print("--End Cycle--")
    time.sleep(sleep)