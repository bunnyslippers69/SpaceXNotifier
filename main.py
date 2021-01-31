import importlib
import threading
import time
import requests
from concurrent.futures import ThreadPoolExecutor

discordWebhookUrl = ""
tweepyKeys = []

with open("config/discordWebhook.conf") as f:
    discordWebhookUrl = f.read().strip()

with open("config/tweepyKeys.conf") as f:
    content = f.readlines()
    content = [x.strip() for x in content] 
    tweepyKeys = content

#Import modules
rc = importlib.import_module("roadClosures")
tn = importlib.import_module("tweetTracker")
tfr = importlib.import_module("tfrTracker")
sn = importlib.import_module("siteChanges")

#Time to sleep between actions
sleep = 35

closureNotifier = rc.ClosureNotifier(discordWebhookUrl)
tweetNotifier = tn.TweetNotifier(discordWebhookUrl, tweepyKeys)
tfrNotifier = tfr.TfrNotifier(discordWebhookUrl)
siteNotifier = sn.SiteNotifier("https://www.spacex.com/vehicles/starship/", discordWebhookUrl)

def run_io_tasks_in_parallel(tasks):
    with ThreadPoolExecutor() as executor:
        running_tasks = [executor.submit(task) for task in tasks]
        for running_task in running_tasks:
            running_task.result()

#Road Closures - https://reqbin.com/kroamhug
#Tweet Notification - https://reqbin.com/ydkyw5k2
while True:
    try:
        print("\n" + str(time.ctime()))

        run_io_tasks_in_parallel([
            lambda: closureNotifier.run(),
            lambda: tweetNotifier.run(),
            lambda: tfrNotifier.run(),
            lambda: siteNotifier.run()
        ])

        print("--End Cycle--")
        time.sleep(sleep)
    except:
        print("An exception occurred. Skipping")