import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
import requests
import pickle
import re

# @st.cache(allow_output_mutation=True)
def load_profile(prof):
    global df
    df_prof = df.loc[df['Full Name'] == prof, :]
    for i, row in df_prof.iterrows():
        url = row['DR-NTU URL']
        soup_source = requests.get(url).text
        soup = BeautifulSoup(soup_source,'lxml')
        background = soup.find('div', id='biographyDiv').text.strip()
        research_interest = soup.find('div', id='researchinterestsDiv').text.strip()
        no_citations = row['Citations (All)']
        return i, background, research_interest, no_citations

@st.cache(allow_output_mutation=True)
def venue_quality(venue):
    if '(' in venue and venue.split('(')[1].split(')')[0] != '':
        venue = venue.split('(')[1].split(')')[0]
        url = f'http://portal.core.edu.au/conf-ranks/?search={venue.replace(" ", "%20")}&by=all&source=all&sort=atitle&page=1'
    else:
        url = f'http://portal.core.edu.au/conf-ranks/?search={venue.replace(" ", "%20")}&by=all&source=all&sort=atitle&page=1'
    soup_source = requests.get(url).text
    soup = BeautifulSoup(soup_source, 'lxml')
    
    def refine_string(s):
        s = re.sub(r"[()\"#/@;:<>{}`+=~|.!?,]", "", s)
        return s
    
    if len(soup.find_all('table')) == 1:
        for row in soup.find_all('tr')[1:]:
            title = row.find_all('td')[0].text.strip()
            acronym = row.find_all('td')[1].text.strip()
            rank = row.find_all('td')[3].text.strip()
            if venue == title:
                return rank
            elif venue.upper() == acronym:
                return rank
            elif acronym.upper() in [refine_string(v).upper() for v in venue.split()]:
                return rank
            elif venue.upper() in [refine_string(t).upper() for t in title.split()]:
                return rank
    return 'unranked'


df = pd.read_csv('Ta_Quynh_Nga.csv')

prof = st.selectbox('Research Profile:', df['Full Name'])

prof_index, background, research_interest, no_citations = load_profile(prof)

# Display profile
profile_container = st.container()
profile_container.title(prof)

profile_container.header('Biography')
profile_container.write(background)

profile_container.header('Research Interest')
profile_container.write(research_interest)

profile_container.header('Publications')
if not pd.isnull(no_citations):
    profile_container.write(f'Citations (All): {int(no_citations)}')
col1, col2 = profile_container.columns([3, 1])

with open(f'publication_set/publications_{prof_index}.pkl', 'rb') as f:
    publications = pickle.load(f)

# column 2: filter
years = set()
for pub in publications:
    years.add(pub['year'])
start, end = col2.slider('Year', min(years), max(years), value=[min(years), max(years)])

subtopics = set()
for pub in publications:
    subtopics.add(pub['subtopic'])
selected_subtopics = col2.multiselect("Filter by area", ['All'] + list(subtopics))

types = set()
for pub in publications:
    types.add(pub['type'])
type_fullname = {
    'book': 'Books and Theses',
    'incollection': 'Parts in Books or Collections',
    'article': 'Journal Articles',
    'inproceedings': 'Conference and Workshop Papers',
    'editor': 'Editorship',
    'informal': 'Informal Publication',
}
fulltype2type = {v: k for k,v in type_fullname.items()}
selected_types = col2.multiselect("Filter by types", ['All'] + [type_fullname[t] for t in list(types)])
if 'All' in selected_types:
    selected_types.remove('All')
    selected_types = ['All'] + [fulltype2type[t] for t in selected_types]
else:
    selected_types = [fulltype2type[t] for t in selected_types]

total_pubs = 0
total_pubs_ctn = col2.container()
col2.markdown('#### Venue Ranking')
ranking_container = col2.container()
col2.markdown('#### Venues')
venue_container = col2.container().expander('Venues')
# col2.markdown('#### Research Areas')
areas_container = col2.container().expander('Research Areas')

# column 1: profile
# col1.write(len(publications))
prev_year = publications[0]['year'] + 1
venue_count = {}
venue_ranking_count = {}
area_count = {}
for pub in publications:
    if pub['year'] not in list(range(start, end+1)):
        continue
    if pub['subtopic'] not in selected_subtopics and 'All' not in selected_subtopics:
        continue
    if pub['type'] not in selected_types and 'All' not in selected_subtopics:
        continue
    if pub['year'] != prev_year:
        col1.markdown(f"### {pub['year']}")
        prev_year = pub['year']

    if pub['venue'] not in venue_count:
        venue_count[pub['venue']] = 0
    venue_count[pub['venue']] += 1

    if pub['subtopic'] not in area_count:
        area_count[pub['subtopic']] = 0
    area_count[pub['subtopic']] += 1

    venue_ranking = venue_quality(pub['venue'])
    if venue_ranking not in venue_ranking_count:
        venue_ranking_count[venue_ranking] = 0
    venue_ranking_count[venue_ranking] += 1

    cite_html_blocks = pub['cite_html'].split(pub['title'])
    cite_html = f'<span style="color:grey">{cite_html_blocks[0]}</span> **{pub["title"]}** <span style="color:grey">{cite_html_blocks[1]}</span>'
    col1.markdown(f'''- {cite_html}<br>Venue ranking: {venue_ranking}''', unsafe_allow_html=True)
    total_pubs += 1

total_pubs_ctn.write(f'Total publications after filtered: {total_pubs}')
venue_count = dict(sorted(venue_count.items(), key=lambda item: item[1], reverse=True))
for k, v in venue_count.items():
    venue_container.write(f'({v}) {k}')

area_count = dict(sorted(area_count.items(), key=lambda item: item[1], reverse=True))
# for k, v in area_count.items():
#     areas_container.write(f'({v}) {k}')

ranking_order = ['A*', 'A', 'B', 'C', 'D', 'E', 'unranked']
ranking = []
for k in ranking_order:
    if k in venue_ranking_count.keys():
        ranking.append((k, venue_ranking_count[k]))
ranking_container.bar_chart(pd.DataFrame(ranking, columns=['Ranking', 'Count']).set_index('Ranking'))
