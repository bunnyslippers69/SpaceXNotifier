from bs4 import BeautifulSoup
import requests
import time
import json
import jsondiff as jsondiff

class ClosureNotifier:
    url = "https://api.bunnyslippers.dev/closures"

    def __init__(self, webhookUrl):
        self.discordWebhookUrl = webhookUrl

    def getClosureJson(self):
        req = requests.get(self.url)

        return json.loads(req.content)
    
    def notifyDiscord(self, webhookUrl, parsedDifferences):
        chgList = parsedDifferences[0]
        delList = parsedDifferences[1]
        insList = parsedDifferences[2]

        numOfDifferences = len(chgList) + len(delList) + len(insList)

        desc = "There " + ("has" if numOfDifferences == 1 else "have") + " been " + str(numOfDifferences) + " road closure " + ("change" if numOfDifferences == 1 else "changes")

        # prevContent = ""
        # for closure in previous:
        #     prevContent = prevContent + closure + "\n\n"

        # currContent = ""
        # for closure in current:
        #         currContent = currContent + closure + "\n\n"

        # diff = ""
        # for difference in differences:
        #     diff = diff + difference + "\n\n"

        changes = ""
        if len(chgList) < 1:
            changes = "No closures were removed."
        else:
            for change in chgList:
                chgString = change["type"] + ": " + change["date"] + ", " + change["time"] + " " + change["status"] + "\n\n"
                changes = changes + chgString

        deletes = ""
        if len(delList) < 1:
            deletes = "No closures were removed."
        else:
            for change in delList:
                chgString = change["type"] + ": " + change["date"] + ", " + change["time"] + " " + change["status"] + "\n\n"
                deletes = deletes + chgString

        inserts = ""
        if len(insList) < 1:
            inserts = "No closures were removed."
        else:
            for change in insList:
                chgString = change["type"] + ": " + change["date"] + ", " + change["time"] + " " + change["status"] + "\n\n"
                inserts = inserts + chgString

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
                            "name": "Edited",
                            "value": changes,
                            "inline": True
                            },
                            {
                            "name": "Removed",
                            "value": deletes,
                            "inline": True
                            },
                            {
                            "name": "Added",
                            "value": inserts,
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

    def extractDifferences(self, currJson):
        return jsondiff.diff(self.prevClosures, currJson)

    def parseDifferences(self, differences):
        if len(differences) < 1:
            return None
        else:
            changed = differences.keys()
            deleted = differences.get(jsondiff.delete)
            inserted = differences.get(jsondiff.insert)

            chgList = []
            delList = []
            insList = []

            for key in changed:
                if isinstance(key, int):
                    chgList.append(self.prevClosures[key])

            if deleted:
                for delete in deleted:
                    delList.append(self.prevClosures[delete])

            if inserted:
                for insert in inserted:
                    insList.append(insert[1])

            return [chgList, delList, insList]

    def run(self):
        print("--Road Closures Start--")
        closureJson = self.getClosureJson()

        if not self.prevClosures:
            self.prevClosures = closureJson
        else:
            differences = self.extractDifferences(closureJson)
            parsedDifferences = self.parseDifferences(differences)

            if parsedDifferences:
                self.notifyDiscord(self.discordWebhookUrl, parsedDifferences)