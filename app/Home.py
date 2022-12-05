import streamlit as st
import pandas as pd
import numpy as np
import pickle

SCREEN_SIZE = (2560, 1664)

st.title('NTU SCSE Faculty Member Dashboard')

df = pd.read_csv('Ta_Quynh_Nga.csv')

col1, col2 = st.columns([1, 4])


# # Sort dataframe
# sort_by = col1.selectbox('Sort by', df.columns)
# if sort_by == 'Citations (All)':
#     df = df.sort_values(sort_by, ascending=False).reset_index().drop(columns=['index'])
# else:
#     df = df.sort_values(sort_by).reset_index().drop(columns=['index'])

with open(f'subtopics.pkl', 'rb') as f:
    subtopics = pickle.load(f)
areas = [k for k, v in subtopics.items()]

def load_subtopics(selected_subtopics):
    if selected_subtopics == 'All':
        return list(range(82))
    indices = set()
    for i in range(82):
        filename = f'publication_set/publications_{i}.pkl'
        with open(filename, 'rb') as f:
            publications = pickle.load(f)
        for pub in publications:
            if pub['subtopic'] in selected_subtopics:
                indices.add(i)
                break
    return list(indices)

# Filter dataframe
filter_form = col1.form("filter_form")
filters = filter_form.radio('Filter by research area', ['All'] + areas)
if filter_form.form_submit_button('Filter'):
     indices = load_subtopics(filters)
     col1.write(f'Total members after filtered: {len(indices)}')
     col2.dataframe(df.iloc[indices], height=SCREEN_SIZE[1])