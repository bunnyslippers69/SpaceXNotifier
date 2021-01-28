from bs4 import BeautifulSoup
import requests
import time

class SiteNotifier():
    def __init__(self, pageUrl, webhookUrl):
        self.pageUrl = pageUrl
        self.webhookUrl = webhookUrl

    def getPage(self):
        return str(requests.get(self.pageUrl).content)

    prevPage = None
    def getDifference(self, currentPage):
        if self.prevPage == None:
            self.prevPage = currentPage
            return False
        else:
            if self.prevPage != currentPage:
                self.prevPage = currentPage
                return True
            else:
                self.prevPage = currentPage
                return False
    
    def notifyDiscord(self, webhookUrl):
        requests.post(webhookUrl, json=
            {
                "content": None,
                "embeds": [
                    {
                    "title": "Starship Site Updated",
                    "description": "There has been a change to the Starship site.",
                    "url": "https://www.spacex.com/vehicles/starship/",
                    "color": 5814783,
                    "author": {
                        "name": "SpaceX",
                        "icon_url": "https://i.bunnyslippers.dev/sks354w2.png"
                    }
                    }
                ],
                "username": "Starship Site",
                "avatar_url": "https://i.bunnyslippers.dev/sks354w2.png"
            })

    def run(self):
        print("--Site Notifier--")
        print("Grabbing page...")
        different = self.getDifference(self.getPage())
        print("Comparing pages...")

        if different:
            print("Difference detected...")
            self.notifyDiscord(self.webhookUrl)
        else:
            print("No differences detected...")
        
        print("Done.")