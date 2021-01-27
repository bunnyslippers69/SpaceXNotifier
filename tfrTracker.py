from bs4 import BeautifulSoup
import requests
import time

class Tfr:
    def __init__(self, date, url):
        self.date = date
        self.url = url

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

            #Adds a new Tfr object to the 'parsedTfrs' list
            parsedTfrs.append(Tfr(date, url))
        
        #Returns the parsed list
        return parsedTfrs
    
    prevTfrs = []

    def getDifference(self, currentTfrs):
        if not self.prevTfrs:
            self.prevTfrs = currentTfrs
        else:
            if len(self.prevTfrs) != len(currentTfrs):
                self.prevTfrs = currentTfrs
                return True
            else:
                for i in range(0, len(currentTfrs)):
                    if currentTfrs[i].url != self.prevTfrs[i].url:
                        self.prevTfrs = currentTfrs
                        return True
        self.prevTfrs = currentTfrs
        return False

    def notifyDiscord(self, webhookUrl):

        requests.post(webhookUrl, json=
            {
                "content": None,
                "embeds": [
                    {
                    "title": "TFR Update",
                    "description": "There has been a change to the SpaceX TFR notices.",
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
        print("--TFRs--")
        print("Started...")
        #Obtains the TFR page content for use in the BeautifulSoup instance
        print("Grabbing page...")
        pageContent = self.getPageContent()
        soup = BeautifulSoup(pageContent, 'html.parser')

        #Obtains unparsed TFRs
        tfrs = self.getCurrentTfrs(soup)

        print("Parsing TFRs...")
        #Parses the TFRs inside the 'tfrs' list
        parsedTfrs = self.parseTfrs(tfrs)

        print("Finding differences...")
        different = self.getDifference(parsedTfrs)

        if different:
            print("Difference found!")
            self.notifyDiscord(self.discordWebhookUrl)
        else:
            print("No differences!")
        print("Done.\n")