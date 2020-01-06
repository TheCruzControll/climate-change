import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
from plotly import tools
from pytrends.request import TrendReq
from bs4 import BeautifulSoup
from datetime import date
import requests
import time
import re
from dash.dependencies import Input, Output, State
import numpy as np
import json

# INITIAL RENDERING OF DATA
# ==========
pytrends = TrendReq(hl='en-US', tz=360)
pytrends.build_payload(['Climate Change'], cat=0,
                       timeframe='today 5-y', geo='US', gprop='')
state_df = pytrends.interest_by_region()
age_df = pd.read_csv("data/med_age.csv", header=None).set_index(0)
age_df.index.rename("State", inplace=True)
age_df.columns = ["Median Age"]

inc_df = pd.read_csv(
    "data/median_income.csv").set_index("State").drop("2013.1", axis=1)
inc_df["2017"] = inc_df["2017"].str.replace(',', "").astype(float)

political_df = pd.read_csv(
    "data/political.csv")
political_df.columns = ["State", "Democrat",
                        "Republican", "Dem Adv", "N", "Classification"]
political_df.set_index("State", inplace=True)

state_loc = pd.read_html(
    "https://www.latlong.net/category/states-236-14.html")[0]
state_loc["Place Name"] = state_loc["Place Name"].str.split(",").str[0]
state_loc["Place Name"] = state_loc["Place Name"].replace(
    "Missouri State", "Missouri")
state_loc.set_index("Place Name", inplace=True)
temp_df = pd.read_csv(
    "data/avg_temp.csv").set_index("State")

state_df["Median Age"] = state_df.index.map(age_df["Median Age"].to_dict())
state_df["Median Income"] = state_df.index.map(inc_df["2017"].to_dict())
state_df["Percent Democrat"] = state_df.index.map(
    political_df["Democrat"].to_dict())
state_df = state_df.merge(
    temp_df, how="inner", left_on=state_df.index, right_on=temp_df.index).set_index("key_0")
state_df = state_df.merge(state_loc, how="inner",
                          left_on=state_df.index, right_on=state_loc.index)
state_df.set_index("key_0", inplace=True)

with open('data/prose.json', 'r') as JSON:
    prose = json.load(JSON)

# DATA INTERACTION
# ==========
'''
Steps for data interaction:
    1. Choose type of graph object. (go.Scatter/go.Bar etc)
    2. Input x data, and y data and store into variable
    3. Group plots into an arrays for easy access
'''


# fig = go.Figure(data=go.scatter())
# APP COMPONENTS
# ==========
'''
Makes a jumbotron-ish component 
'''
def make_j():
    return dbc.Row(
    [
        dbc.Col(
            [
                html.H1(prose["intro"]["title"])
            ],md=8,
        )
    ], justify="center", className="hero"
)

'''
Makes a header component
'''
def make_h():
    return dbc.Row(
    [
        dbc.Col(
            [
                html.H2(prose["intro"]["p1"]),
                html.P(prose["intro"]["p2"])
            ],md=8,
        )
    ], justify="center", className="hero"
)

'''
Makes an analysis component with respective paragraphs, 
given the analysis number (e.g. 1 for "a1")
'''
def make_a(a_num):
    return dbc.Row(
    [
        dbc.Col(
           [html.P(prose["a" + str(a_num)][p]) for p in prose["a" + str(a_num)]], md=8,
        )
    ], justify="center"
)

# fig = go.Figure(data=go.Scatter(
#     x=state_df["AvgTemp"], y=state_df["Climate Change"], mode="markers"))

# APP LAYOUT
# ==========

app = dash.Dash(__name__, external_scripts=['https://raw.githubusercontent.com/robin-dela/hover-effect/master/example/js/three.min.js', 'https://raw.githubusercontent.com/robin-dela/hover-effect/master/example/js/TweenMax.min.js',
                                            'https://raw.githubusercontent.com/robin-dela/hover-effect/master/dist/hover-effect.umd.js'], external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

app.layout = html.Div(children=[
    make_j(),
    make_h(),
    make_a(1),
    make_a(2),
    dcc.Input(id='new_search_term', type='text', value='Climate Change'),
    html.Button(id='submit_button', n_clicks=0, children='Submit'),
    dcc.Dropdown(
        id='state_characteristic',
        options=[{'label': i, 'value': i} for i in state_df.columns[1:]],
        value='Median Age'
    ),
    dbc.Row(
        [
            dbc.Col(
                [dcc.Graph(id='us_graph')], md=6
            ),
            dbc.Col(
                [dcc.Graph(id='state_characteristic_graph')], md=6
            )
        ]
    ),
    make_a(3)
])


'''
    Handles user interaction for the state graph. 
    Updates graph depending on submitted search term
'''


@app.callback(
    Output('us_graph', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('new_search_term', 'value')])
def update_graph(n_clicks, new_search_term):
    pytrends.build_payload([new_search_term], cat=0,
                           timeframe='today 5-y', geo='US', gprop='')
    state_df = pytrends.interest_by_region()

    abbrvs = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI",
              "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN",
              "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH",
              "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA",
              "WV", "WI", "WY"]

    state_df["abbrev"] = abbrvs
    state_df["Median Age"] = state_df.index.map(age_df["Median Age"].to_dict())
    state_df["Median Income"] = state_df.index.map(inc_df["2017"].to_dict())
    state_df["Percent Democrat"] = state_df.index.map(
        political_df["Democrat"].to_dict())
    state_df = state_df.merge(
        temp_df, how="inner", left_on=state_df.index, right_on=temp_df.index).set_index("key_0")
    state_df = state_df.merge(state_loc, how="inner",
                              left_on=state_df.index, right_on=state_loc.index)
    state_df.set_index("key_0", inplace=True)

    state_df["text"] = 'Median Age: ' + state_df["Median Age"].astype(str) + '<br>' + \
        'Median Income: ' + state_df["Median Income"].astype(str) + '<br>' + \
        'Percent Democrat: %' + state_df["Percent Democrat"].astype(str) + '<br>' + \
        'Avg Temp: ' + state_df["AvgTemp"].astype(str) + '<br>' + \
        'Latitude: ' + state_df["Latitude"].astype(str) + '<br>' + \
        'Longitude: ' + state_df["Longitude"].astype(str) + '<br>'

    new_fig = go.Figure(data=go.Choropleth(
        locations=state_df['abbrev'],  # Spatial coordinates
        z=state_df[new_search_term].astype(float),  # Data to be color-coded
        locationmode='USA-states',  # set of locations match entries in `locations`
        colorscale='Reds',
        colorbar_title="Search Popularity",
        text=state_df["text"]
    ))

    new_fig.update_layout(
        title_text='"%s" Search Popularity by State' % new_search_term,
        geo_scope='usa',  # limit map scope to USA
    )
    return new_fig


'''
    Handles user interaction for state characteristcs graph
    Changes output on dropdown value change or if a new term is submitted
'''


@app.callback(Output('state_characteristic_graph', 'figure'),
              [Input('submit_button', 'n_clicks'),
               Input('state_characteristic', 'value')],
              [State('new_search_term', 'value')])
def update_characteristics_graph(n_clicks, characteristic_term, new_search_term):
    pytrends.build_payload([new_search_term], cat=0,
                           timeframe='today 5-y', geo='US', gprop='')
    state_df = pytrends.interest_by_region()

    abbrvs = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI",
              "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN",
              "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH",
              "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA",
              "WV", "WI", "WY"]

    state_df["abbrev"] = abbrvs
    state_df["Median Age"] = state_df.index.map(age_df["Median Age"].to_dict())
    state_df["Median Income"] = state_df.index.map(inc_df["2017"].to_dict())
    state_df["Percent Democrat"] = state_df.index.map(
        political_df["Democrat"].to_dict())
    state_df = state_df.merge(
        temp_df, how="inner", left_on=state_df.index, right_on=temp_df.index).set_index("key_0")
    state_df = state_df.merge(state_loc, how="inner",
                              left_on=state_df.index, right_on=state_loc.index)
    state_df.set_index("key_0", inplace=True)

    scatter = go.Scatter(
        x=state_df[characteristic_term], y=state_df[new_search_term], mode="markers", hoverinfo="text", hovertext=state_df["abbrev"])
    '''
        ADD CORRELATION LINE
    '''
    correlation = go.Scatter(
        x=np.unique(state_df[characteristic_term]),
        y=np.poly1d(np.polyfit(state_df[characteristic_term], state_df[new_search_term], 1))(
            np.unique(state_df[characteristic_term]))
    )
    fig = go.Figure(data=[scatter, correlation])
    fig.update_layout(
        title_text=new_search_term + ' Search Popularity by %s of State' % characteristic_term,
        xaxis_title=characteristic_term,
        yaxis_title=new_search_term + ' Search Popularity',
    )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
