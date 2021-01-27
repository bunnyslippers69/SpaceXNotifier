from bs4 import BeautifulSoup
import requests
import time

class ClosureNotifier:
    url = "https://www.cameroncounty.us/spacex"

    def __init__(self, webhookUrl):
        self.discordWebhookUrl = webhookUrl

    def getPageContent(self):
        req = requests.get(self.url)

        return req.content

    def extractTable(self, soup):
        return soup.find("div", {"class": "gem-table"})

    def extractRows(self, table, soup):
        return soup.find_all("td")

    def getInfo(self):
        page = self.getPageContent()

        soup = BeautifulSoup(page, 'html.parser')

        table = self.extractTable(soup)
        rows = self.extractRows(table, soup)

        info = []
        for i in range(int(len(rows) / 4)):
            baseIndex = i * 4
            info.append(rows[baseIndex].text + ": " + rows[baseIndex + 1].text + " " + rows[baseIndex + 2].text + " " + rows[baseIndex + 3].text)

        return info
    
    def notifyDiscord(self, webhookUrl, differences, previous, current):
        numOfDifferences = int(len(differences) / 2)
        desc = "There " + ("has" if numOfDifferences == 1 else "have") + " been " + str(numOfDifferences) + " road closure " + ("change" if numOfDifferences == 1 else "changes")

        prevContent = ""
        for closure in previous:
            prevContent = prevContent + closure + "\n\n"

        currContent = ""
        for closure in current:
                currContent = currContent + closure + "\n\n"

        diff = ""
        for difference in differences:
            diff = diff + difference + "\n\n"

        requests.post(webhookUrl, json=
            {
                "content": None,
                "embeds": [
                    {
                        "title": "Road Closure Update",
                        "description": desc,
                        "url": "https://cameroncounty.us/spacex",
                        "color": 65525,
                        "fields": [
                            {
                            "name": "Previous",
                            "value": prevContent,
                            "inline": True
                            },
                            {
                            "name": "Current",
                            "value": currContent,
                            "inline": True
                            },
                            {
                            "name": "Differences",
                            "value": diff,
                            "inline": True
                            }
                        ],
                        "author": {
                            "name": "SpaceX",
                            "icon_url": "https://i.bunnyslippers.dev/ywppicsh.png"
                        }
                    }
                ],
                "username": "Road Closure",
                "avatar_url": "https://i.bunnyslippers.dev/ywppicsh.png"
            })

    def saveToArchive(self):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'url':'https://cameroncounty.us/spacex/',
            'capture_all':'on'
        }

        requests.post("https://web.archive.org/save/https://cameroncounty.us/spacex", headers=headers, data=data)

    prevClosures = []

    def run(self):
        print("--Road Closures--")
        print("Started...")
        #prevClosures = []

        info = self.getInfo()
        differences = []

        print("Finding Differences...")
        if not self.prevClosures:
            self.prevClosures = info

            #Saves the current page to the web archive
            print("Saving page to web archive...")
            self.saveToArchive()
        else:
            if len(self.prevClosures) >= len(info):
                differences = list(set(self.prevClosures) ^ set(info))
            elif len(info) > len(self.prevClosures):
                differences = list(set(info) ^ set(self.prevClosures))

        
        if len(differences) > 0:
            for diff in differences:
                print(diff)
            requests.post("https://maker.ifttt.com/trigger/road_closures_changed/with/key/daL1yvnd0s3Uu3pXaCOXA36JaSFzJtxJ57Nb3lr_TY", json={"value1": int(len(differences)/2)} )

            if self.discordWebhookUrl != None:
                self.notifyDiscord(self.discordWebhookUrl, differences, self.prevClosures, info)
            
            #Saves the current page to the web archive
            print("Saving page to web archive...")
            self.saveToArchive()
        else:
            print("No Differences Found.")

        self.prevClosures = info
        print("Done.\n")
        #time.sleep(30)