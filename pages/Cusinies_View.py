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
from Utils import code_cleaning, pie_chart_v1

#======================================================================
# Page configuration
#======================================================================

st.set_page_config(
    page_title= 'Cuisines View 🍴',
    page_icon= '🍴',
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

st.header('Cuisine View 🍴', divider= True)

with st.container():
    st.markdown('## Top 5 Best Restaurants')
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown("#### Kuma's Corner - Belmont")
        st.markdown('## 4.9 / 5.0 ⭐')
    with col2:
        st.markdown("#### Barbeque Nation")
        st.markdown(" ")
        st.markdown(" ")
        st.markdown('## 4.9 / 5.0 ⭐')
    with col3:
        st.markdown("#### The Parlor Pizzeria")
        st.markdown(" ")
        st.markdown(" ")
        st.markdown('## 4.9 / 5.0 ⭐')
    with col4:
        st.markdown("#### Xoco")
        st.markdown(" ")
        st.markdown(" ")
        st.markdown('## 4.9 / 5.0 ⭐')
    with col5:
        st.markdown("#### Portillo's Hot Dogs")
        st.markdown(" ")
        st.markdown(" ")
        st.markdown('## 4.9 / 5.0 ⭐')

st.markdown('---')

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('## Top 20 Restaurants')
        grouped = (df1.loc[:,['restaurant_name', 'aggregate_rating', 'votes']]
                .groupby(['restaurant_name'])
                .mean()
                .sort_values(['aggregate_rating','votes'], ascending=False)
                .reset_index()
                .head(20))
        grouped.columns = ['Restaurant name','Avg. rating','Avg. votes']
        st.dataframe(grouped, use_container_width= True, hide_index= True)
    with col2:
        st.markdown('## Top 10 Most Popular Cuisines')
        grouped = df1.loc[:, ['cuisines', 'aggregate_rating']].sort_values('aggregate_rating', ascending=False).head(10)
        grouped.columns = ['Cuisines','Avg. rating']
        st.dataframe(grouped, use_container_width= True, hide_index= True)

st.markdown('---')

with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### Restaurants That Has Booking Service")
        fig = pie_chart_v1(df1, 'booking')
        st.plotly_chart(fig, use_container_width= True)
    with col2: 
        st.markdown("### Restaurants That Has Online Delivering Service")
        fig = pie_chart_v1(df1, 'online')
        st.plotly_chart(fig, use_container_width= True)
    with col3:
        st.markdown("### Restaurants That Has Delivering Service")
        fig = pie_chart_v1(df1, 'delivering')
        st.plotly_chart(fig, use_container_width= True)




