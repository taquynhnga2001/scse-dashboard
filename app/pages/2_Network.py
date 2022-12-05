import streamlit as st
import networkx as nx
from pyvis.network import Network
import pickle
import pandas as pd
import itertools
import streamlit.components.v1 as components

RED = '#FB0303'
ORANGE = '#FB8E03'

st.title("Network of SCSE Collaborations")
G = Network(height='1000px', bgcolor='#222222', font_color='white')

df = pd.read_csv('df_dblp_name.csv')

scse_authors = set()
with open(f'scse_authors.pkl', 'rb') as f:
    scse_authors = pickle.load(f)

def create_graph():
    global G
    for i, row in df.iterrows():
        prof_name = row['DBLP Name']
        with open(f'publication_set/publications_{i}.pkl', 'rb') as f:
            publications = pickle.load(f)
        for pub in publications:
            authors = pub['authors']
            G.add_node(prof_name, label=prof_name)
            for author in authors:
                if author in df['DBLP Name'].tolist():
                    G.add_node(author, label=author)
            for edge in itertools.combinations(list(scse_authors), 2):
                G.add_edge(edge[0], edge[1])

# create_graph()
prof = st.selectbox('Choose a member', ['All'] + list(scse_authors))

with open(f'graph_scse.pkl', 'rb') as f:
    G = pickle.load(f)

if prof != 'All':
    for node in G.nodes:
        if node['label'] == prof:
            node['color'] = RED

    connect_nodes = []
    for edges in G.edges:
        if edges['from'] == prof:
            connect_nodes.append(edges['to'])
        elif edges['to'] == prof:
            connect_nodes.append(edges['from'])

    for node in G.nodes:
        if node['label'] in connect_nodes:
            node['color'] = ORANGE
# with open(f'graph_scse.pkl', 'wb') as f:
#     pickle.dump(G, f)
    
G.save_graph(f'html_files/pyvis_graph.html')
HtmlFile = open(f'html_files/pyvis_graph.html', 'r', encoding='utf-8')
components.html(HtmlFile.read(), height=800)
