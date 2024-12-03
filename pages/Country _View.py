import os
import pandas as pd
import numpy as np 
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import plotly.io as pio
import folium
from folium.plugins import MarkerCluster
from folium.plugins import FastMarkerCluster
import inflection
from streamlit_folium import folium_static, st_folium
from datetime import datetime
from PIL import Image
from Utils import code_cleaning, bar_chart_v1, bar_chart_v2

#======================================================================
# Page configuration
#======================================================================

st.set_page_config(
    page_title= 'Country View 🌎',
    page_icon= '🌎',
    layout= 'wide'
)

pio.templates.default = 'plotly'

# Import dataset

df = pd.read_csv('dataset\zomato.csv')

# Data cleaning

df1 = code_cleaning(df)

#======================================================================
# Sidebar layout
#======================================================================

image = Image.open('zomato_icon.png')
st.sidebar.image(image, width= 120)
st.sidebar.markdown('### :gray[*"Better food for more people."*]')

st.logo('zomato_logo.png', size="large", icon_image= image)


st.sidebar.markdown('---')

# Multiselect Filter

country_options = st.sidebar.multiselect(
    'Select the countries',
    ["India","Australia","Brazil","Canada",
     "Indonesia","New Zeland","Philippines",
     "Qatar","Singapure","South Africa","Sri Lanka",
     "Turkey","United Arab Emirates","England","United States of America"],
     default= ["India", "United States of America", "Brazil"]
)

filtered_df = df1['country'].isin(country_options)
df1 = df1.loc[filtered_df,:]


st.sidebar.markdown('---')
st.sidebar.markdown('**Powered by Iury Martins Silva ©**')

#======================================================================
# Streamlit page layout
#======================================================================

st.header('Country View 🌎', divider=True)

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('### Top 3 Best Rating')
        best_rating = np.round(df1.loc[:,['aggregate_rating', 'country']].groupby('country').mean().sort_values('aggregate_rating', ascending=False).reset_index().head(3),2)
        st.dataframe(best_rating, hide_index= True, 
                     use_container_width= True, 
                     column_config={'country': 'Country ✅',
                                    'aggregate_rating': st.column_config.NumberColumn('Rating',format='%f ⭐')})
    with col2:
        st.markdown('### Top 3 Worst Rating')
        worst_rating = np.round(df1.loc[:,['aggregate_rating', 'country']].groupby('country').mean().sort_values('aggregate_rating', ascending=True).reset_index().head(3),2)
        st.dataframe(worst_rating, 
                     hide_index= True, 
                     use_container_width= True,
                     column_config={'country': 'Country ❌',
                                    'aggregate_rating': st.column_config.NumberColumn('Rating',format='%f ⭐')})
        
st.markdown('---')

with st.container():
    st.markdown('## Average Cost For Two (USD) By Country')
    fig = bar_chart_v1(df1, 
                       op_column = 'currency_in_usd',  
                       xaxis_label= 'Countries', 
                       yaxis_label= 'Avg. cost for two (USD)',
                       op= 'mean')
    st.plotly_chart(fig, use_container_width= True)

    st.markdown('---')

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('## Top 10 Highest Rated Countries')
        fig = bar_chart_v2(df1, 'aggregate_rating', 'Countries', 'Avg. Ratings')
        st.plotly_chart(fig, use_container_width= True)
    with col2:
        st.markdown('## Top 10 Countries With Most Votes')
        fig = bar_chart_v2(df1, 'votes', 'Countries', 'Avg. Votes')
        st.plotly_chart(fig, use_container_width= True)

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('## Restaurant Count by Country')
        fig = bar_chart_v1(df1, 'restaurant_id', xaxis_label='Countries', yaxis_label= 'Restaurant count', op= 'count')
        st.plotly_chart(fig, use_container_width= True)
    with col2:
        st.markdown('## City Count by Country')
        fig = bar_chart_v1(df1, 'city', xaxis_label='Countries', yaxis_label= 'City count', op= 'nunique')
        st.plotly_chart(fig, use_container_width= True)