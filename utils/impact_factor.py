from scholarly import scholarly
import urllib.request, json
import jellyfish
import pandas as pd
import sys


class ImpactFactor:
    def __init__(self, file_name):
        self.df = pd.read_csv(file_name, delimiter=";")
        self.df["impact-factor"] = self.df["Cites / Doc. (2years)"]

    def stats(self, journal):
        journal = journal.lower()
        flag = [
            jellyfish.jaro_winkler_similarity(journal, x) > 0.8
            for x in self.df["Title"]
        ]
        t = self.df[flag]
        impact = ""
        Q = ""
        tp = "unknown"
        title = ""
        if len(t) > 0:
            print(t)
            score = [
                jellyfish.jaro_winkler_similarity(journal, x)
                for x in t["Title"]
            ]
            t["match"] = score
            top = t.iloc[0]
            impact = " IF:" + str(top["impact-factor"])
            Q = top["SJR Best Quartile"]
            if len(Q) > 0:
                Q = " " + Q
            tp = top["Type"]
            title = top["Title"]
        return (impact, Q, tp, title)
