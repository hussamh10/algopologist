# create a streamlit app to display the dataframe df

import pandas as pd
import pickle as pkl
import streamlit as st

def create_html(obs):
    source = obs.get('source', 'Unknown')
    secondary_source = obs.get('secondary_source', '')
    if secondary_source == None:
        secondary_source = ''
    else:
        secondary_source = f'• {secondary_source}'
    title = obs.get('title', 'No title')
    description = obs.get('description', 'No description')
    description = description.replace('\n', ' ')
    date = obs.get('created_at', 'No date')
    # if date is a epoch time convert it to a human readable date
    if isinstance(date, float):
        date = pd.to_datetime(int(date), unit='s').strftime('%Y-%m-%d %H:%M:%S')


    likes = obs.get('likes', '')
    comments = obs.get('comments', '')
    shares = obs.get('shares', '')
    views = obs.get('views', '')
    # if views shares likes comments are None set them to •
    if likes == None:
        likes = ''
    if comments == None:
        comments = ''
    if shares == None:
        shares = ''
    if views == None:
        views = ''
   
    is_ad = obs.get('is_ad', False)
    card = f""" <div style="border: 1px solid #ccc; border-radius: 8px;
        margin-top:10px; padding: 10px; max-width: 500px; font-size: 0.9em;">
        <p style="margin: 0; font-weight: bold; color: #007bff;">{source} {"• ad" if
        is_ad else secondary_source}</p>
        <h3 style="font-size: 1.2em; font-weight: bold; margin: 5px 0;">{title}</h3>
        <p style="margin: 5px 0;">{description[:100]}</p>
        <hr style="margin: 5px 0;">
        <p style="font-size: 0.75em; color: #666; margin: 5px 0;">{date}</p>
        <div style="display: flex; justify-content: space-between; font-size: 0.75em; color: #666; margin-top: 5px;">
            <span>👍 {likes}</span>
            <span>💬 {comments}</span>
            <span>🔄 {shares}</span>
            <span>👀 {views}</span>
        </div>
    </div>
    """

    return card
    



st.set_page_config(layout="wide")

observations = pd.read_pickle('observations.pkl')
observations.keys()

cols = st.columns(8)

for col in cols:
    index = cols.index(col)
    with col:
        st.write(f"Column {index}")
        time = st.selectbox('time', ['pre', 'post'], key=f'time{index}')
        user = st.selectbox('User', list(observations.keys()), key=f'user{index}')
        platform = st.selectbox('Platform', list(observations[user].keys()), key=f'platform{index}')

        obs = observations[user][platform][time][:20]
        observations_html = [create_html(obs) for obs in obs]

        for obs in observations_html:
            st.write(obs, unsafe_allow_html=True)