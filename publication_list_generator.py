import sys
import pandas as pd

from utils.dblp import Dblp
from utils.impact_factor import ImpactFactor
from utils.scholar import Scholar
from utils.wos import WoS
from utils.user_properties import *

ifct = ImpactFactor(if_file_name)

sc = Scholar(author_name)
db = Dblp(author_name)
df = pd.DataFrame(
    columns=[
        "title",
        "type",
        "scholar",
        "year",
        "desc",
        "wos",
        "Q",
        "impact-factor",
    ]
)
ws = WoS(wos_file_name)
for p in sc.publications():
    title = p["bib"]["title"]
    tp, id, year, desc, venue = db.venue_type(title)
    impact, Q, _, _ = ifct.stats(venue)

    if tp == "unknown":
        tp, id, year, desc = sc.get_details(p)
    df.loc[id] = [
        title,
        tp,
        p["num_citations"],
        year,
        desc,
        ws.count(title),
        Q,
        impact,
    ]


with open(output_file, "w") as f:
    tmp = sys.stdout
    sys.stdout = f
    groups = df.groupby("type")
    for g in groups:
        print(g[0])
        print()
        for r in g[1].sort_values(by=["year"]).iterrows():
            print(
                "%s [g-scholar: %s wos: %s%s%s]"
                % (
                    r[1]["desc"],
                    r[1]["scholar"],
                    r[1]["wos"],
                    r[1]["Q"],
                    r[1]["impact-factor"],
                )
            )
        print("-------------------")
    sys.stdout = tmp
