import os
import pandas as pd
import numpy as np 
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import plotly.io as pio
import folium
from folium.plugins import FastMarkerCluster
from folium.plugins import MarkerCluster
import inflection
from streamlit_folium import folium_static, st_folium
from datetime import datetime
from PIL import Image


# If is needed constantly update on the list of currencies used on this dataset, this API can do it easily (free limit of 300 requests)

# import currencyapicom

# client = currencyapicom.Client('YOUR_API_KEY')
# result = client.latest('USD',currencies=['BWP','BRL','AED','INR','IDR','NZD','GBP','QAR','ZAR','LKR','TRY','USD'])
# exchange = result['data'] --> dictionary with currency code and value 

# Formating columns to snakecase

def rename_columns(dataframe):
    df = dataframe.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(' ', '')
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df.columns = cols_new

    return df

# Country code to country name dict 

COUNTRIES = {
1: "India",
14: "Australia",
30: "Brazil",
37: "Canada",
94: "Indonesia",
148: "New Zeland",
162: "Philippines",
166: "Qatar",
184: "Singapure",
189: "South Africa",
191: "Sri Lanka",
208: "Turkey",
214: "United Arab Emirates",
215: "England",
216: "United States of America",
}
def country_name(country_id):
    return COUNTRIES[country_id]


# Color code to color name dict

COLORS = {
"3F7E00": "darkgreen",
"5BA829": "green",
"9ACD32": "lightgreen",
"CDD614": "orange",
"FFBA00": "red",
"CBCBC8": "darkred",
"FF7800": "darkred",
}
def color_name(color_code):
    return COLORS[color_code]


# Creating price tags

def categorize_prices(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"
    

# Creating option tags

def categorize_options(column_name):
    if column_name == 1:
        return 'Yes'
    else:
        return 'No'
    

# Currency names to currency code dict 

CODES = {
'Botswana Pula(P)' : 'BWP',
'Brazilian Real(R$)' : 'BRL',
'Dollar($)' : 'USD',
'Emirati Diram(AED)' : 'AED',
'Indian Rupees(Rs.)' : 'INR',
'Indonesian Rupiah(IDR)' : 'IDR',
'NewZealand($)' : 'NZD',
'Pounds(£)' : 'GBP',
'Qatari Rial(QR)' : 'QAR',
'Rand(R)' : 'ZAR',
'Sri Lankan Rupee(LKR)' : 'LKR',
'Turkish Lira(TL)' : 'TRY'
}
def currency_code(currency):
    return CODES[currency]

# Currency values in USD dollar

VALUES = {    
'BWP' : 0.07346,
'BRL' : 0.17196,
'USD' : 1.0,
'AED' : 0.27229,
'INR' : 0.01182,
'IDR' : 0.000062795,
'NZD' : 0.58599,
'GBP' : 1.25916,
'QAR' : 0.27472,
'ZAR' : 0.05520,
'LKR' : 0.00343,
'TRY' : 0.02894   
}

def usd_value(currency_value):
    return VALUES[currency_value]



def code_cleaning(df1):

    df1 = rename_columns(df1)

    df1['country_code'] = df1['country_code'].apply(lambda x: country_name(x))
    df1['rating_color'] = df1['rating_color'].apply(lambda x: color_name(x))
    df1['price_range'] = df1['price_range'].apply(lambda x: categorize_prices(x))
    df1['has_table_booking'] = df1['has_table_booking'].apply(lambda x: categorize_options(x))
    df1['has_online_delivery'] = df1['has_online_delivery'].apply(lambda x: categorize_options(x))
    df1['is_delivering_now'] = df1['is_delivering_now'].apply(lambda x: categorize_options(x))
    df1['currency'] = df1['currency'].apply(lambda x: currency_code(x))
    
    df1.rename(columns={'country_code': 'country'}, inplace=True)
    df1.rename(columns= {'currency' : 'currency_codes'}, inplace=True)

    df1['currency_values'] = df1['currency_codes'].apply(lambda x: usd_value(x))

    df1 = df1.drop('switch_to_order_menu', axis=1)

    df1['cuisines'] = df1['cuisines'].fillna('Not informed')

    df1['cuisines'] = df1['cuisines'].apply(lambda x: x.split(",")[0])

    df1.drop_duplicates(subset='restaurant_id', keep='first', inplace=True)

    df1 = df1.loc[df1['average_cost_for_two'] != 25000017, :]

    to_usd = lambda x: (x['average_cost_for_two'] * x['currency_values'])
    df1['currency_in_usd'] = df1.apply(to_usd, axis = 1)
    
    df1 = df1.reindex(['restaurant_id', 'restaurant_name', 'country', 'city', 'address',
       'locality', 'locality_verbose', 'longitude', 'latitude', 'cuisines',
       'average_cost_for_two', 'currency_codes', 'currency_in_usd', 
       'has_table_booking', 'has_online_delivery', 'is_delivering_now', 'price_range',
       'aggregate_rating', 'rating_color', 'rating_text', 'votes'], axis=1)
   
    return df1

# Map chart:

# Slow version

def map_chart(df1):

    m1 = folium.Map()

    mark_cluster = MarkerCluster().add_to(m1)

    df1.apply(lambda x: folium.Marker(location = [x['latitude'], 
                        x['longitude']],
                        popup = x[['city','restaurant_name']],
                        icon=folium.Icon(color=x['rating_color']),
                        ).add_to(mark_cluster), axis= 1)
    
    folium.LayerControl().add_to(m1)

    st_folium(m1, use_container_width=True)

# Fast version

def fast_map_chart(df1):

    df_aux = df1.loc[:,['longitude','latitude', 'city', 'restaurant_name', 'rating_color']]

    callback = """\
        function (row) {
        var icon, marker;
        icon = L.AwesomeMarkers.icon({
        icon: "map-marker", markerColor: 'red'});
        marker = L.marker(new L.LatLng(row[0], row[1]));
        marker.setIcon(icon);
        return marker;
    };
    """

    m2 = folium.Map()

    FastMarkerCluster(data=list(zip(df_aux['latitude'], df_aux['longitude'])), callback = callback).add_to(m2)

    st_folium(m2, use_container_width=True)

# vertical bars:

def bar_chart_v1(df1: pd.DataFrame, op_column: str, xaxis_label: str, yaxis_label: str, op: str):

    grouped = np.round(df1.loc[:, [op_column, 'country']].groupby('country').agg({op_column: op}).sort_values(op_column, ascending=False).reset_index(), 2)

    fig = go.Figure()

    fig.add_trace(go.Bar(name='placeholder', 
                        x= grouped['country'], 
                        y= grouped[op_column]))

    fig.update_layout(autosize = False, width= 1200, height= 500)
    fig.update_yaxes(automargin = True)
    fig.update_layout(xaxis_title= xaxis_label , yaxis_title= yaxis_label)
    fig.update_traces(text= grouped[op_column])
    fig.update_traces(textposition= 'outside')

    return fig

# horizontal bars 

def bar_chart_v2(df1: pd.DataFrame, op_column: str, xaxis_label: str, yaxis_label: str):

    grouped = np.round(df1.loc[:,[op_column, 'country']].groupby('country').mean().sort_values(op_column, ascending=True).reset_index(), 2).head(10)

    colors1 = ['#636efa'] * 7 + ['#c7c704', '#878901', '#4d4f00'] 

    fig = go.Figure()

    fig.add_trace(go.Bar(name='placeholder', 
                        x= grouped[op_column], 
                        y= grouped['country'],
                        orientation= 'h',
                        marker_color = colors1))

    fig.update_layout(autosize = False, width= 1200, height= 500)
    fig.update_yaxes(automargin= True)
    fig.update_layout(xaxis_title= xaxis_label, yaxis_title= yaxis_label)
    fig.update_traces(text= grouped[op_column])
    fig.update_traces(textposition = 'outside')

    return fig

# Bar chart of the top 10 cities with the most restaurant registered  

def bar_chart_v3(df1):
    grouped = df1.loc[:, ['restaurant_id','city', 'country']].groupby(['country','city']).count().sort_values('restaurant_id', ascending=False).reset_index().head(10)

    fig = px.bar(grouped, x= 'city', y= 'restaurant_id', color= 'country', text_auto= True)
    fig.update_layout(xaxis_title= 'Cities', yaxis_title= 'Restaurant count')
    fig.update_layout(xaxis={'categoryorder':'total descending'})

    return fig

# Bar chart top 10 cities with rating greater then 4 or lower then 2.5

def bar_chart_v4(df1: pd.DataFrame, greater: bool ):
    if greater == True:
        city_rating_above = df1.loc[df1['aggregate_rating'] > 4.0 , ['city', 'restaurant_id', 'country']].groupby(['city', 'country']).count().sort_values('restaurant_id', ascending=False).reset_index().head(10)

        fig = px.bar(city_rating_above, x= 'city', y= 'restaurant_id', color= 'country', text_auto=True)
        fig.update_traces(textposition= 'inside')
        fig.update_layout(xaxis={'categoryorder':'total descending'})
        fig.update_layout(xaxis_title= 'Cities', yaxis_title= 'Restaurant count')

        return fig
    else:
        city_rating_above = df1.loc[df1['aggregate_rating'] < 2.5 , ['city', 'restaurant_id', 'country']].groupby(['city', 'country']).count().sort_values('restaurant_id', ascending=False).reset_index().head(10)

        fig = px.bar(city_rating_above, x= 'city', y= 'restaurant_id', color= 'country', text_auto=True)
        fig.update_traces(textposition= 'inside')
        fig.update_layout(xaxis={'categoryorder':'total descending'})
        fig.update_layout(xaxis_title= 'Cities', yaxis_title= 'Restaurant count')

        return fig
    
# Top 10 cities with the most distint cuisines 

def bar_chart_v5(df1):
    grouped = df1.loc[:,['cuisines','city', 'country']].groupby(['city','country']).nunique().sort_values('cuisines', ascending=False).reset_index().head(10)

    fig = px.bar(grouped, x= 'city', y= 'cuisines', color= 'country', text_auto=True)
    fig.update_traces(textposition= 'outside')
    fig.update_layout(xaxis={'categoryorder':'total descending'})
    fig.update_layout(xaxis_title= 'Cities', yaxis_title= 'Restaurant count')

    return fig

# Pie charts

def pie_chart_v1(df1: pd.DataFrame, option: str):

    if option == 'booking':
        df_aux = df1.loc[:, ['has_table_booking', 'restaurant_id']].groupby('has_table_booking').count().reset_index()
        df_aux['booking_percent'] = (df_aux['restaurant_id'] / df_aux['restaurant_id'].sum()) * 100
        fig = go.Figure(data=[go.Pie(labels= df_aux['has_table_booking'], values= df_aux['booking_percent'], pull= [0, 0.1, 0])])
    elif option == 'online':
        df_aux = df1.loc[:, ['has_online_delivery', 'restaurant_id']].groupby('has_online_delivery').count().reset_index()
        df_aux['booking_percent'] = (df_aux['restaurant_id'] / df_aux['restaurant_id'].sum()) * 100
        fig = go.Figure(data=[go.Pie(labels= df_aux['has_online_delivery'], values= df_aux['booking_percent'], pull= [0, 0.08, 0])])
    elif option == 'delivering':
        df_aux = df1.loc[:, ['is_delivering_now', 'restaurant_id']].groupby('is_delivering_now').count().reset_index()
        df_aux['booking_percent'] = (df_aux['restaurant_id'] / df_aux['restaurant_id'].sum()) * 100
        fig = go.Figure(data=[go.Pie(labels= df_aux['is_delivering_now'], values= df_aux['booking_percent'], pull= [0, 0.08, 0])])

    return fig