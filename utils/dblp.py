from scholarly import scholarly
import urllib.request, json
import jellyfish
import pandas as pd
import sys


class Dblp:
    def __init__(self, author_name):
        n = urllib.parse.quote(author_name, safe="")
        with urllib.request.urlopen(
            "http://dblp.org/search/publ/api?format=json&h=100&q=" + n
        ) as url:
            data = json.loads(url.read().decode())
        self.publ = data["result"]["hits"]["hit"]

    def publications(self):
        return self.publ

    def find(self, title):
        title = title.lower()
        return [
            x
            for x in self.publ
            if (
                jellyfish.levenshtein_distance(
                    title, x["info"]["title"].lower()
                )
                < 10
            )
        ]

    def venue_type(self, title):
        t = self.find(title)
        if len(t) < 1:
            return ("unknown", 0, 0, "", "")
        info = t[0]["info"]
        year = str(info["year"])
        tp = info["type"]
        id = t[0]["@id"]
        tit = info["title"]
        venue = info["venue"]
        authors = info["authors"]["author"]
        if isinstance(authors, list):
            if len(authors) > 2:
                names = ", ".join([x["text"] for x in authors[:-1]])
                names = " and ".join([names, authors[-1]["text"]])
            else:
                names = " and ".join([x["text"] for x in authors])
        else:
            names = authors["text"]

        desc = "%s, %s. %s (%s)" % (names, tit, venue, year)
        return (tp, id, year, desc, venue)
