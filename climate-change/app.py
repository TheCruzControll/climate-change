import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
import datetime
from plotly import tools



# USE ONLY FOR EXAMPLE. DELETE WHEN ADDING OWN DATA
import numpy as np
N = 100
random_x = np.linspace(0, 1, N)
random_y0 = np.random.randn(N) 
random_y1 = np.random.randn(N)
random_y2 = np.random.randn(N)

# LOAD DATA
# ==========
prose_df = prose_df = pd.read_json("data/prose.json").T

# DATA INTERACTION
# ==========
'''
Steps for data interaction:
    1. Choose type of graph object. (go.Scatter/go.Bar etc)
    2. Input x data, and y data and store into variable
    3. Group plots into an arrays for easy access
'''
example_scatter1 = go.Scatter(x=random_x, y=random_y0,
                    mode='lines',
                    name='lines',
                    line = dict(color = '#90DAB5'),
                    opacity = 0.8)

example_scatter2 = go.Scatter(x=random_x, y=random_y1,
                    mode='lines+markers',
                    name='lines+markers',
                    line = dict(color = '#3F94AB'),
                    opacity = 0.8)

example_scatter3 = go.Scatter(x=random_x, y=random_y2,
                    mode='lines', 
                    name='lines',
                    line = dict(color = '#6285B2'),
                    opacity = 0.8)

examplelayout = go.Layout(
    hovermode = "x",
    title = "Example Title",
    xaxis = dict(
        range = [0,1]
    ),
    yaxis = dict(
        autorange = True
    )
)

examples = [example_scatter1, example_scatter2, example_scatter3]

# APP COMPONENTS
# ==========
header = dbc.Jumbotron(
    [
        html.H1("climate-change", className="display-3"),
        html.P(
            "article subtitle"
        )
    ],
    className = 'my-div text-center',
)


examplefig = go.Figure(data=examples, layout=examplelayout)

# APP LAYOUT
# ==========

app = dash.Dash(__name__, external_scripts=['https://raw.githubusercontent.com/robin-dela/hover-effect/master/example/js/three.min.js','https://raw.githubusercontent.com/robin-dela/hover-effect/master/example/js/TweenMax.min.js','https://raw.githubusercontent.com/robin-dela/hover-effect/master/dist/hover-effect.umd.js'], external_stylesheets=[dbc.themes.BOOTSTRAP
])

server = app.server

app.layout = html.Div(children=[
    header,
    
    dbc.Container(children =[ 
        html.H2(prose_df.loc["intro", "title"]),

        html.P(prose_df.loc["intro", "prose_1"]),

        dcc.Graph(
            figure = examplefig
        ),
        html.P(prose_df.loc["data explanation", "prose_1"]),
        html.P(prose_df.loc["data explanation", "prose_2"]),
        html.P(prose_df.loc["data explanation", "prose_3"]),

    ]
)])

if __name__ == '__main__':
    app.run_server(debug=True)