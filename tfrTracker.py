from bs4 import BeautifulSoup
import requests
import time
import json
import jsondiff as jsondiff
import re

class TfrNotifier:
    url = "https://api.bunnyslippers.dev/tfrs/detailed/"

    def __init__(self, webhookUrl):
        self.discordWebhookUrl = webhookUrl

    def getTfrJson(self):
        req = requests.get(self.url)

        return json.loads(req.content)
    
    def notifyDiscord(self, webhookUrl, parsedDifferences):
        chgList = parsedDifferences[0]
        delList = parsedDifferences[1]
        insList = parsedDifferences[2]

        numOfDifferences = len(chgList) + len(delList) + len(insList)

        desc = "There " + ("has" if numOfDifferences == 1 else "have") + " been " + str(numOfDifferences) + " TFR " + ("change" if numOfDifferences == 1 else "changes")

        changes = ""
        if len(chgList) < 1:
            changes = "No TFRs were edited."
        else:
            for change in chgList:
                chgString = change["notamNumber"] + "\nAltitude: " + self.getAltitude(change["traditionalMessage"]) + "\n" + change["startDate"] + " to " + change["endDate"] + "\n\n"
                changes = changes + chgString

        deletes = ""
        if len(delList) < 1:
            deletes = "No TFRs were removed."
        else:
            for change in delList:
                chgString = change["notamNumber"] + "\nAltitude: " + self.getAltitude(change["traditionalMessage"]) + "\n" + change["startDate"] + " to " + change["endDate"] + "\n\n"
                deletes = deletes + chgString

        inserts = ""
        if len(insList) < 1:
            inserts = "No TFRs were added."
        else:
            for change in insList:
                chgString = change["notamNumber"] + "\nAltitude: " + self.getAltitude(change["traditionalMessage"]) + "\n" + change["startDate"] + " to " + change["endDate"] + "\n\n"
                inserts = inserts + chgString

        requests.post(webhookUrl, json=
            {
                "content": None,
                "embeds": [
                    {
                        "title": "TFR Update",
                        "description": desc,
                        "url": "https://tfr.faa.gov/",
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
                            "name": "FAA",
                            "icon_url": "https://cdn.discordapp.com/avatars/800817161495904277/575c9555b6d1884d7bbbb3f521a1f859.webp"
                        }
                    }
                ],
                "username": "TFR Update",
                "avatar_url": "https://cdn.discordapp.com/avatars/800817161495904277/575c9555b6d1884d7bbbb3f521a1f859.webp"
            })

    prevTfrs = []

    def getAltitude(self, traditionalMessage):
        result = re.search("(POINT OF ORIGIN )(.*)(?= TO PROVIDE)", traditionalMessage.replace("\n", " "))
        return result[2]

    def extractDifferences(self, currJson):
        return jsondiff.diff(self.prevTfrs, currJson)

    def parseDifferences(self, differences, tfrJson):
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
                    chgList.append(tfrJson[key])

            if deleted:
                for delete in deleted:
                    delList.append(self.prevTfrs[delete])

            if inserted:
                for insert in inserted:
                    insList.append(insert[1])

            return [chgList, delList, insList]

    def run(self):
        print("--TFRs Start--")
        tfrJson = self.getTfrJson()

        if not self.prevTfrs:
            self.prevTfrs = tfrJson
        else:
            if self.prevTfrs != tfrJson:
                differences = self.extractDifferences(tfrJson)
                parsedDifferences = self.parseDifferences(differences, tfrJson)

                if parsedDifferences:
                    self.notifyDiscord(self.discordWebhookUrl, parsedDifferences)
                    self.prevTfrs = tfrJson