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
from Utils import code_cleaning, bar_chart_v1, bar_chart_v2, bar_chart_v3, bar_chart_v4, bar_chart_v5

#======================================================================
# Page configuration
#======================================================================

st.set_page_config(
    page_title= 'City View 🌆',
    page_icon= '🌆',
    layout= 'wide'
)

pio.templates.default = 'plotly'

# Import dataset

df = pd.read_csv('../dataset/zomato.csv')

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

st.header('City View 🌆', divider=True)

with st.container():
    col1, col2, col3 = st.columns(3)

    with col1: 
        city_unique = df1['city'].nunique()
        col1.metric('Registered Cities', city_unique)
    with col2:
        price_range_city = df1.loc[df1['price_range'] == 'gourmet', ['price_range','city']].groupby('city').count().sort_values('price_range', ascending= False).reset_index()
        price_range_top = price_range_city.loc[0,'price_range']
        st.markdown('City With The Most Gourmet Restaurants')
        col2.metric('São Paulo', price_range_top)
    with col3:
        price_range_city = df1.loc[df1['price_range'] == 'cheap', ['price_range','city']].groupby('city').count().sort_values('price_range', ascending= False).reset_index()
        price_range_top = price_range_city.loc[0,'price_range']
        st.markdown('City With The Most Cheap Restaurants')
        col3.metric('Ludhiana', price_range_top)

st.markdown('---')

with st.container():
        st.markdown('## Top 10 Cities With The Most Restaurant Registered')
        fig = bar_chart_v3(df1)
        st.plotly_chart(fig, use_container_width= True)

st.markdown('---')

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('### Top 10 Cities With Rating Greater Then 4 ⭐')
        fig = bar_chart_v4(df1, greater= True)
        st.plotly_chart(fig, use_container_width= True)
    with col2:
        st.markdown('### Top 10 Cities With Rating Lower Then 2.5 ⭐')
        fig = bar_chart_v4(df1, greater= False)
        st.plotly_chart(fig, use_container_width= True)

st.markdown('---')

with st.container():
     st.markdown('### Top 10 Cities With The Most Distint Cuisines')
     fig = bar_chart_v5(df1)
     st.plotly_chart(fig, use_container_width= True)
