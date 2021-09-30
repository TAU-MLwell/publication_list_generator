
#%%

# prerequisits:
# install required libraries using:
#
# pip install jellyfish pandas scholarly
#
# download citations from WOS (I was too lazy to automate this, but it is pretty easy to do):
#
# 1. Go to https://www.webofscience.com/wos/author/search
# 2. Search for your name
# 3. On the right pane click "view citation report"
# 4. Click "Export Full Report"
# 5. Save to file in text format
#
# download journal impact-factor and ranking:
# 1. Go to https://www.scimagojr.com/journalrank.php
# 2. Click on download data
#
# Set the proper value in the following variables

# your name (used in google scholar and dblp)
author_name = "Ran Gilad-Bachrach"

# the file name of the web-of-science citation report
wos_file_name = r"/mnt/c/temp/savedrecs.txt"

# the impact factor and ranking file-name
if_file_name = r"scimagojr 2020.csv"

# the file name where the results will be stored
output_file = r"/mnt/c/temp/publications.txt"

# you are all set and ready to go ...


#%%
from scholarly import scholarly
import urllib.request, json 
import jellyfish
import pandas as pd
import sys




#%%
class scholar:
    def __init__(self, author_name):
        search_query = scholarly.search_author(author_name)
        self.data = scholarly.fill(next(search_query), sections=['publications'])
        
    def publications(self):
        return self.data['publications']

    def get_details(self, p):
        q = scholarly.fill(p)
        tp = "unknow"
        if ('pub_url' in q):
            if ('patents.google.com' in q['pub_url']):
                tp = "patent"
        id = q['author_pub_id']
        bib = q['bib']
        if ('pub_year' in bib):
            year = str(bib['pub_year'])
        else:
            year = "????"
        venue = ""
        if ('journal' in bib):
            venue = bib['journal']
            tp = 'Journal Articles'
        if ('conference' in bib):
            venue = bib['conference']
            tp = 'conference'


        desc = "%s, %s %s (%s)" %(bib['author'], bib['title'], venue, year)
        return tp, id, year, desc


class dblp:
    def __init__(self, author_name):
        n = (urllib.parse.quote(author_name, safe=''))
        with urllib.request.urlopen("http://dblp.org/search/publ/api?format=json&h=100&q=" + n) as url:
            data = json.loads(url.read().decode())
        self.publ = data['result']['hits']['hit']

    def publications(self):
        return self.publ

    def find(self, title):
        title = title.lower()
        return([x for x in self.publ if (jellyfish.levenshtein_distance(title,x['info']['title'].lower()) < 10)] )
        
    def venue_type(self, title):
        t = self.find(title)
        if (len(t) < 1):
            return('unknown', 0, 0, "", "")
        info = t[0]['info']
        year = str(info['year'])
        tp = info['type']
        id = t[0]['@id']
        tit = info['title']
        venue = info['venue']
        authors = info['authors']['author']
        names = " and ".join([x['text'] for x in authors])



        desc = "%s, %s. %s (%s)" %(names, tit, venue, year)
        return(tp,id,year, desc, venue)

class WoS:
    def __init__(self, file_name):
        self.df = pd.read_csv(file_name, skiprows=[0,1,2])

    def count(self, title):
        flag = [jellyfish.levenshtein_distance(title, x) < 10 for x in self.df['Title']]
        t = self.df[flag]
        if (len(t) > 0):
            return(str(t["Total Citations"].max()))
        return("?")

#%% 
class impact_factor:
    def __init__(self, file_name):
        self.df = pd.read_csv(file_name, delimiter=';')
        self.df["impact-factor"] = self.df["Cites / Doc. (2years)"]

    def stats(self, journal):
        journal = journal.lower()
        flag = [jellyfish.jaro_winkler_similarity(journal, x) > 0.8 for x in self.df['Title']]
        t = self.df[flag]
        impact = ""
        Q = ""
        tp = "unknown"
        title = ""
        if (len(t) > 0):
            print(t)
            score = [jellyfish.jaro_winkler_similarity(journal, x) for x in t['Title']]
            t["match"] = score
            top = t.iloc[0]
            impact = " IF:" + str(top["impact-factor"])
            Q = top["SJR Best Quartile"]
            if (len(Q) > 0):
                Q = " " +Q
            tp = top["Type"]
            title = top["Title"]
        return(impact, Q, tp, title)

ifct = impact_factor(if_file_name)

#%%
sc = scholar(author_name)
db = dblp(author_name)
df = pd.DataFrame(columns=['title', 'type', 'scholar', 'year', 'desc', 'wos', 'Q', 'impact-factor'])
ws = WoS(wos_file_name)
for p in sc.publications():
    title = p['bib']['title']
    tp, id, year, desc, venue = db.venue_type(title)
    impact, Q, _, _ = ifct.stats(venue)

    if (tp == "unknown"):
        tp, id, year, desc = sc.get_details(p)
    df.loc[id]= [title, tp, p['num_citations'], year, desc, ws.count(title), Q, impact]



# %%
with open(output_file, "w") as f:
    tmp = sys.stdout
    sys.stdout = f
    groups = df.groupby("type")
    for g in groups:
        print(g[0])
        print()
        for r in g[1].sort_values(by=["year"]).iterrows():
            print("%s [g-scholar: %s wos: %s%s%s]" % (r[1]["desc"], r[1]["scholar"], r[1]["wos"], r[1]["Q"], r[1]["impact-factor"]))
        print("-------------------")
    sys.stdout = tmp
#%%
# %%
