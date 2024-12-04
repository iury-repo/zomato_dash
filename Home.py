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
from Utils import code_cleaning, map_chart, fast_map_chart

#======================================================================
# Page configuration
#======================================================================

st.set_page_config(
    page_title= 'Home :house:',
    page_icon= ':bar_chart:',
    layout= 'wide'
)

pio.templates.default = 'plotly'

# Import dataset

df = pd.read_csv('\dataset\zomato.csv')

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

st.header('Home Page :house:', divider=True)
# st.title('Home :house: ')

with st.container():    
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        unique_restaurants = df1['restaurant_id'].count()
        col1.metric('Total Restaurants:',unique_restaurants)
    with col2:
        unique_countries = df1['country'].nunique()
        col2.metric('Total Countries:', unique_countries)
    with col3:
        city_unique = df1['city'].nunique()
        col3.metric('Total Cities:',city_unique)
    with col4:
        total_votes = df1['votes'].sum()
        col4.metric('Total reviews:',total_votes)
    with col5:
        cuisines_count = df1['cuisines'].nunique()
        col5.metric('Total Cuisines:',cuisines_count)
    
with st.container():

    map_option = st.selectbox('Select the map chart mode:', ('Fast mode ( Lose popup and color rating upon markers but improve considerably load speed ).','Detailed mode ( Full detailed markers, but with significaly slow load speed )'), 
                              placeholder= "Choose an map option.",
                              help= "Because of the sheer amount of points, the point marker generation can suffer frequent reloads an slow update time. Choose the loading modes who's serves you well.")

    if map_option == 'Fast mode ( Lose popup and color rating upon markers but improve considerably loading speed ).':
        fast_map_chart(df1) 

        st.markdown('')
    elif map_option == 'Detailed mode ( Full detailed markers but with significantly slow loading speed )': 
        map_chart(df1)  
