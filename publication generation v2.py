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
wos_file_name = r'WOS_JAN_2024_RGB.txt'

# the impact factor and ranking file-name
if_file_name = r'scimagojr 2022.csv'

# the file name where the results will be stored
output_file = r"publications_rani_JAN_2024.txt"

# you are all set and ready to go ...




#%%
import pandas as pd
from scholarly import scholarly
import urllib.request, json 
import jellyfish
import sys

#%%
def get_publications_from_scholar(author_name):
    # Search for the author
    search_query = scholarly.search_author(author_name)
    try:
        # Fetch the author
        author = next(search_query)
        scholarly.fill(author, sections=['publications'])

        # List of publications
        publications = author['publications']

        # Create a list to hold publication data
        publication_data = []

        # Extract data for each publication
        for pub in publications:
            scholarly.fill(pub)
            title = pub['bib'].get('title', '')
            authors = pub['bib'].get('author', '')
            num_citations = pub.get('num_citations', 0)
            pub_url = pub.get('pub_url', '')
            author_pub_id = pub.get('author_pub_id', '')
            bib = pub.get('bib', {})
            journal = pub['bib'].get('journal', '')
            conference = pub['bib'].get('conference', '')
            pub_year = pub['bib'].get('pub_year', '')
            volume = pub['bib'].get('volume', '')
            issue = pub['bib'].get('issue', '')
            pages = pub['bib'].get('pages', '')
            doi = pub['bib'].get('doi', '')
            book_title = pub['bib'].get('book_title', '')

            publication_data.append([title, authors, num_citations, pub_url, author_pub_id, bib, 
                                     journal, conference, pub_year, volume, issue, pages, doi, book_title])
            print(f"{len(publication_data)}: {title}")

        # Create a DataFrame
        df = pd.DataFrame(publication_data, columns=['Title', 'Authors', 'Citations', 'Pub URL', 'Author Pub ID', 'Bib', 
                                                     'Journal', 'Conference', 'Pub Year', 'Volume', 'Issue', 'Pages', 'DOI', 'Book Title'])

        return df

    except StopIteration:
        print(f"No author found for {author_name}")
        return pd.DataFrame()


#%%
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
        try:
            venue = info['venue']
        except:
            venue = '???'    
        authors = info['authors']['author']
        try:
            names = " and ".join([x['text'] for x in authors])
        except:
            names = str(authors)



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

#%% main
df = get_publications_from_scholar(author_name)
df.to_pickle('pubs.pkl')
print("done downloading from google scholar")
#%% read df from pickle
#df = pd.read_pickle('pubs.pkl')
# %%
db = dblp(author_name)
ws = WoS(wos_file_name)

# %%
additional_data = []
for r in df.iterrows():
    title = r[1]['Title']
    tp, id, year, desc, venue = db.venue_type(title)
    impact, Q, _, _ = ifct.stats(venue)
    ws_count = ws.count(title)
    additional_data.append([id, tp, year, desc, venue, Q, impact, ws_count])
df_additional = pd.DataFrame(additional_data, columns=['id', 'type', 'year', 'desc', 'venue', 'Q', 'impact-factor', 'wos'])
#%%
df_merge = pd.concat([df, df_additional], axis = 1)
#%%
# merge two rows if they have the same title. When merging, make the citations the sum of orginal citations
# and the citations of the merged row.
# make the groupby case insensitive
df_merge['lower Title'] = df_merge['Title'].str.lower() 
df_merge = df_merge.groupby(['lower Title'], as_index=False).agg({'Citations':'max', 'wos':'max', 'Q':'max', 'impact-factor':'max', 'Pub URL':'max', 'id':'max', 'type':'max', 'year':'max', 'desc':'max', 'venue':'max', 'Title':'max', 'Authors':'max'})
#%% 
df_merge.loc[(df_merge['Pub URL'].str.contains('patents')) & (df_merge['type'] == 'unknown'), 'type'] = 'Patents'
# %%
with open(output_file, "w") as f:
    groups = df_merge.groupby("type")
    for g in groups:
        print(g[0], file=f)
        print(file=f)
        for r in g[1].sort_values(by=["year"]).iterrows():
            desc = f'{r[1]["Authors"]}, "{r[1]["Title"]}", {r[1]["venue"]} ({r[1]["year"]})'
            s = f"{desc} [g-scholar: {r[1]['Citations']} wos: {r[1]['wos']}{r[1]['Q']}{r[1]['impact-factor']}]"
            #remove special characters from s
            s = s.encode('ascii', 'ignore').decode('ascii')
            print(s, file=f)
        print("-------------------", file=f)


# %%
