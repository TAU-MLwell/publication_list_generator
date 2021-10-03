from scholarly import scholarly
import urllib.request, json
import jellyfish
import pandas as pd
import sys


class WoS:
    def __init__(self, file_name):
        self.df = pd.read_csv(file_name, skiprows=[0, 1, 2])

    def count(self, title):
        flag = [
            jellyfish.levenshtein_distance(title, x) < 10
            for x in self.df["Title"]
        ]
        t = self.df[flag]
        if len(t) > 0:
            return str(t["Total Citations"].max())
        return "?"
