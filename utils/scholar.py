from scholarly import scholarly
import urllib.request, json
import jellyfish
import pandas as pd
import sys


class Scholar:
    def __init__(self, author_name):
        search_query = scholarly.search_author(author_name)
        self.data = scholarly.fill(
            next(search_query), sections=["publications"]
        )

    def publications(self):
        return self.data["publications"]

    def get_details(self, p):
        q = scholarly.fill(p)
        tp = "unknow"
        if "pub_url" in q:
            if "patents.google.com" in q["pub_url"]:
                tp = "patent"
        id = q["author_pub_id"]
        bib = q["bib"]
        if "pub_year" in bib:
            year = str(bib["pub_year"])
        else:
            year = "????"
        venue = ""
        if "journal" in bib:
            venue = bib["journal"]
            tp = "Journal Articles"
        if "conference" in bib:
            venue = bib["conference"]
            tp = "conference"

        desc = "%s, %s %s (%s)" % (bib["author"], bib["title"], venue, year)
        return tp, id, year, desc
