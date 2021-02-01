from bs4 import BeautifulSoup
import requests
import time

class Tfr:
    def __init__(self, date, url, tfrId):
        self.date = date
        self.url = url
        self.id = tfrId

class TfrNotifier:
    tfrUrl = "https://tfr.faa.gov/tfr2/list.jsp?type=SPACE+OPERATIONS"

    def __init__(self, webhookUrl):
        self.discordWebhookUrl = webhookUrl

    def getPageContent(self):
        req = requests.get(self.tfrUrl)
        return req.content

    def getTfrTable(self, soup):
        table = soup.findChildren("table")[4]
        return table

    def getTfrRows(self, soup):
        tfrTable = self.getTfrTable(soup)

        tableRows = tfrTable.findChildren("tr")
        tfrs = []

        for i in range(4, len(tableRows) - 3):
            tfrs.append(tableRows[i])

        return tfrs

    def getCurrentTfrs(self, soup):
        tfrRows = self.getTfrRows(soup)
        spacexTfrs = []

        for row in tfrRows:
            cols = row.findChildren("td")

            facility = cols[2]
            if facility.find("a").text == "ZHU":
                spacexTfrs.append(row)

        return spacexTfrs

    def parseTfrs(self, tfrs):
        #List to store parsed objects
        parsedTfrs = []

        #Iterate over all unparsed TFRs
        for tfr in tfrs:
            #Split into columns
            cols = tfr.findChildren("td")
            #Tag that contains the url to the TFR
            aTag = cols[0].find_all('a', href=True)[0]

            #Grabs the date and url from the unparsed tfr
            date = cols[0]
            url = "https://tfr.faa.gov" + aTag['href'][2:]
            tfrId = cols[1].text.strip()

            #Adds a new Tfr object to the 'parsedTfrs' list
            parsedTfrs.append(Tfr(date, url, tfrId))
        
        #Returns the parsed list
        return parsedTfrs
    
    prevTfrs = []

    def getDifferences(self, currentTfrs):
        differences = []

        if not self.prevTfrs:
            self.prevTfrs = currentTfrs
            self.prevTfrs.append(Tfr("rape", "me", "please"))
        else:
            #Checks if there are any differing TFRs
            difference = False
            if len(self.prevTfrs) != len(currentTfrs):
                difference = True
            else:
                for i in range(0, len(currentTfrs)):
                    if currentTfrs[i].url != self.prevTfrs[i].url:
                        difference = True
            
            #If there are differing TFRs, add them all to a list
            if difference:
                differences.append(self.prevTfrs)
                differences.append(currentTfrs)

                self.prevTfrs = currentTfrs
                return differences

        self.prevTfrs = currentTfrs
        return differences

    def notifyDiscord(self, webhookUrl, differences):
        
        print(len(differences))
        prevTfrs = ""
        for diff in differences[0]:
            prevTfrs = prevTfrs + "["+ diff.id + "](" + diff.url + ")\n"

        currTfrs = ""
        for diff in differences[1]:
            currTfrs = currTfrs + "["+ diff.id + "](" + diff.url + ")\n"

        requests.post(webhookUrl, json=
            {
                "content": None,
                "embeds": [
                    {
                    "title": "TFR Update",
                    "description": "There has been a change to the SpaceX TFR notices.",
                    "fields": [
                            {
                            "name": "Previous",
                            "value": prevTfrs,
                            "inline": True
                            },
                            {
                            "name": "Current",
                            "value": currTfrs,
                            "inline": True
                            }
                        ],
                    "url": "https://tfr.faa.gov/tfr2/list.jsp?type=SPACE+OPERATIONS",
                    "color": 5814783,
                    "author": {
                        "name": "FAA",
                        "icon_url": "https://i.bunnyslippers.dev/5fe47ebl.png"
                    }
                    }
                ],
                "username": "TFR Update",
                "avatar_url": "https://i.bunnyslippers.dev/5fe47ebl.png"
            })

    def run(self):
        print("--TFRs Start--")
        #Obtains the TFR page content for use in the BeautifulSoup instance

        pageContent = self.getPageContent()
        soup = BeautifulSoup(pageContent, 'html.parser')

        #Obtains unparsed TFRs
        tfrs = self.getCurrentTfrs(soup)

        #Parses the TFRs inside the 'tfrs' list
        parsedTfrs = self.parseTfrs(tfrs)

        differences = self.getDifferences(parsedTfrs)

        if len(differences) > 0:
            self.notifyDiscord(self.discordWebhookUrl, differences)

        print("--TFRs Done--")