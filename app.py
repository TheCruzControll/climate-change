import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
from pytrends.request import TrendReq
import json

# INITIAL RENDERING OF DATA
# ==========

'''
Hard Coded Searchterm
'''
search_term = 'Climate Change'

'''
Build pytrends
'''
pytrends = TrendReq(hl='en-US', tz=360)
pytrends.build_payload(['Climate Change'], cat=0,
                       timeframe='today 5-y', geo='US', gprop='')


'''
Build age data frame
'''
age_df = pd.read_csv("data/med_age.csv", header=None).set_index(0)
age_df.index.rename("State", inplace=True)
age_df.columns = ["Median Age"]


'''
Build incone data frame
'''
inc_df = pd.read_csv(
    "data/median_income.csv").set_index("State").drop("2013.1", axis=1)
inc_df["2017"] = inc_df["2017"].str.replace(',', "").astype(float)


'''
Build political data frame
'''
political_df = pd.read_csv(
    "data/political.csv")
political_df.columns = ["State", "Democrat",
                        "Republican", "Dem Adv", "N", "Classification"]
political_df.set_index("State", inplace=True)


'''
Build lat and long data frame
'''
state_loc = pd.read_html(
    "https://www.latlong.net/category/states-236-14.html")[0]
state_loc["Place Name"] = state_loc["Place Name"].str.split(",").str[0]
state_loc["Place Name"] = state_loc["Place Name"].replace(
    "Missouri State", "Missouri")
state_loc.set_index("Place Name", inplace=True)


'''
Build temperature data frame
'''
temp_df = pd.read_csv(
    "data/avg_temp.csv").set_index("State")


'''
Build state data frame
'''
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


'''
Build solutions data frame
'''
solutions_df = pd.read_csv('data/solutions.csv')

'''
Load prose
'''
with open('data/prose.json', 'r') as JSON:
    prose = json.load(JSON)

# DATA INTERACTION
# ==========

'''
 Solutions Interation
'''
total_reduction = solutions_df['total_atmospheric_reduction'].dropna().sum(
    axis=0)
top_solution_reduction = solutions_df.iloc[0]["total_atmospheric_reduction"]


def solution_interaction():
    return dbc.Row(
        [
            dbc.Col(
                [
                    dcc.Dropdown(
                        id='solutions-dropdown',
                        options=[{'label': i, 'value': i}
                                 for i in solutions_df['name']],
                        placeholder='Select a solution'
                    ),
                ], md=5
            ), dbc.Col(
                [
                    html.Div(id='solutions-output')
                ], md=7
            )
        ], align="center"
    )


# APP COMPONENTS
# ==========

''' 
State map component
'''

map_fig = go.Figure(data=go.Choropleth(
    locations=state_df['abbrev'],  # Spatial coordinates
    z=state_df[search_term].astype(float),  # Data to be color-coded
    locationmode='USA-states',  # set of locations match entries in `locations`
    colorscale='Blues',
    colorbar_title="Search Popularity",
))

map_fig.update_layout(
    title_text='"%s" Search Popularity by State' % search_term,
    geo_scope='usa',  # limit map scope to USA
)


# scatter = go.Scatter(
#     x=state_df[characteristic_term], y=state_df[new_search_term], mode="markers", hoverinfo="text", hovertext=state_df["abbrev"])
# correlation = go.Scatter(
#     x=np.unique(state_df[characteristic_term]),
#     y=np.poly1d(np.polyfit(state_df[characteristic_term], state_df[new_search_term], 1))(
#         np.unique(state_df[characteristic_term]))
# )
# fig = go.Figure(data=[scatter, correlation])
# fig.update_layout(
#     title_text=new_search_term + ' Search Popularity by %s of State' % characteristic_term,
#     xaxis_title=characteristic_term,
#     yaxis_title=new_search_term + ' Search Popularity',
# )
'''
Climate Change Search Popularity by Average Temperature
'''

scatter = go.Scatter(x=state_df["AvgTemp"], y=state_df[search_term],
                     mode="markers", hoverinfo="text", hovertext=state_df["abbrev"])
avg_temp_fig = go.Figure(data=scatter)
avg_temp_fig.update_layout(
    title_text='"Climate Change" Search Popularity by Average Temperature',
    xaxis_title="Avg Temperature",
    yaxis_title='"Climate Change" Search Popularity'
)

'''
Makes graph based on figure passed in
'''


def make_graph(fig):
    return dcc.Graph(
        figure=fig
    )


'''
Makes component based on components passed in
'''


def make_interaction(component):
    return dbc.Row(
        [
            dbc.Col(
                children=[
                    component
                ], md=8,
            )
        ], justify="center",
    )


'''
Makes a jumbotron-ish component 
'''


def make_j():
    return dbc.Row(
        [
            dbc.Col(
                [
                    html.H1(prose["intro"]["title"])
                ], md=8,
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
                ], md=8,
            )
        ], justify="center",
    )


'''
Makes an analysis component with respective paragraphs
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


def make_t(title):
    return dbc.Row(
        [
            dbc.Col(
                [
                    html.H2(title)
                ], md=8
            )
        ], justify="center",
    )


def quote_block():
    return dbc.Row(
        [
            dbc.Col(
                [
                    html.Blockquote(children=[
                        html.P("116th congress. 1st session s. 1426. to amend the endangered species act of 1973. to establish a procedure for approval of certain settlements. in the senate of the united states may 13, 2019 mr. cornyn (for himself, mr. boozman, mr. crapo, mr. cruz, mr. enzi, mr. lankford, mr. risch, mr. sullivan, and mr. wicker) introduced the following bill; which was read twice and referred to the committee on environment and public works a bill to amend the endangered species act of 1973 to establish a procedure for approval of certain settlements.\n")
                    ])
                ], md=8
            )
        ], justify="center"
    )
# APP LAYOUT
# ==========


app = dash.Dash(__name__, external_scripts=['https://raw.githubusercontent.com/robin-dela/hover-effect/master/example/js/three.min.js', 'https://raw.githubusercontent.com/robin-dela/hover-effect/master/example/js/TweenMax.min.js',
                                            'https://raw.githubusercontent.com/robin-dela/hover-effect/master/dist/hover-effect.umd.js'], external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

app.layout = html.Div(children=[
    make_j(),
    make_h(),
    make_a(1),
    make_t("So, what is the most crucial solution to reversing our emissions?"),
    make_interaction(solution_interaction()),
    make_a(2),
    make_a(3),
    make_interaction(make_graph(map_fig)),
    make_a(4),
    make_interaction(make_graph(avg_temp_fig)),
    make_a(5),
    make_t("Inviting Change Through Policy"),
    make_a(6),
    quote_block(),
    make_a(7)

    # dcc.Input(id='new_search_term', type='text', value='Climate Change'),
    # html.Button(id='submit_button', n_clicks=0, children='Submit'),
    # dcc.Dropdown(
    #     id='state_characteristic',
    #     options=[{'label': i, 'value': i} for i in state_df.columns[1:]],
    #     value='Median Age'
    # ),
    # dbc.Row(
    #     [
    #         dbc.Col(
    #             [dcc.Graph(id='us_graph')], md=6
    #         ),
    #         dbc.Col(
    #             [dcc.Graph(id='state_characteristic_graph')], md=6
    #         )
    #     ]
    # ),
])


'''
    Handles user interaction for the state graph. 
    Updates graph depending on submitted search term
'''
# @app.callback(
#     Output('us_graph', 'figure'),
#     [Input('submit_button', 'n_clicks')],
#     [State('new_search_term', 'value')])
# def update_graph(n_clicks, new_search_term):
#     pytrends.build_payload([new_search_term], cat=0,
#                            timeframe='today 5-y', geo='US', gprop='')
#     state_df = pytrends.interest_by_region()

#     abbrvs = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI",
#               "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN",
#               "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH",
#               "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA",
#               "WV", "WI", "WY"]

#     state_df["abbrev"] = abbrvs
#     state_df["Median Age"] = state_df.index.map(age_df["Median Age"].to_dict())
#     state_df["Median Income"] = state_df.index.map(inc_df["2017"].to_dict())
#     state_df["Percent Democrat"] = state_df.index.map(
#         political_df["Democrat"].to_dict())
#     state_df = state_df.merge(
#         temp_df, how="inner", left_on=state_df.index, right_on=temp_df.index).set_index("key_0")
#     state_df = state_df.merge(state_loc, how="inner",
#                               left_on=state_df.index, right_on=state_loc.index)
#     state_df.set_index("key_0", inplace=True)

#     state_df["text"] = 'Median Age: ' + state_df["Median Age"].astype(str) + '<br>' + \
#         'Median Income: ' + state_df["Median Income"].astype(str) + '<br>' + \
#         'Percent Democrat: %' + state_df["Percent Democrat"].astype(str) + '<br>' + \
#         'Avg Temp: ' + state_df["AvgTemp"].astype(str) + '<br>' + \
#         'Latitude: ' + state_df["Latitude"].astype(str) + '<br>' + \
#         'Longitude: ' + state_df["Longitude"].astype(str) + '<br>'

#     new_fig = go.Figure(data=go.Choropleth(
#         locations=state_df['abbrev'],  # Spatial coordinates
#         z=state_df[new_search_term].astype(float),  # Data to be color-coded
#         locationmode='USA-states',  # set of locations match entries in `locations`
#         colorscale='Reds',
#         colorbar_title="Search Popularity",
#         text=state_df["text"]
#     ))

#     new_fig.update_layout(
#         title_text='"%s" Search Popularity by State' % new_search_term,
#         geo_scope='usa',  # limit map scope to USA
#     )
#     return new_fig


# '''
#     Handles user interaction for state characteristcs graph
#     Changes output on dropdown value change or if a new term is submitted
# '''


# @app.callback(Output('state_characteristic_graph', 'figure'),
#               [Input('submit_button', 'n_clicks'),
#                Input('state_characteristic', 'value')],
#               [State('new_search_term', 'value')])
# def update_characteristics_graph(n_clicks, characteristic_term, new_search_term):
#     pytrends.build_payload([new_search_term], cat=0,
#                            timeframe='today 5-y', geo='US', gprop='')
#     state_df = pytrends.interest_by_region()

#     abbrvs = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI",
#               "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN",
#               "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH",
#               "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA",
#               "WV", "WI", "WY"]

#     state_df["abbrev"] = abbrvs
#     state_df["Median Age"] = state_df.index.map(age_df["Median Age"].to_dict())
#     state_df["Median Income"] = state_df.index.map(inc_df["2017"].to_dict())
#     state_df["Percent Democrat"] = state_df.index.map(
#         political_df["Democrat"].to_dict())
#     state_df = state_df.merge(
#         temp_df, how="inner", left_on=state_df.index, right_on=temp_df.index).set_index("key_0")
#     state_df = state_df.merge(state_loc, how="inner",
#                               left_on=state_df.index, right_on=state_loc.index)
#     state_df.set_index("key_0", inplace=True)

#     scatter = go.Scatter(
#         x=state_df[characteristic_term], y=state_df[new_search_term], mode="markers", hoverinfo="text", hovertext=state_df["abbrev"])
#     '''
#         ADD CORRELATION LINE
#     '''
#     correlation = go.Scatter(
#         x=np.unique(state_df[characteristic_term]),
#         y=np.poly1d(np.polyfit(state_df[characteristic_term], state_df[new_search_term], 1))(
#             np.unique(state_df[characteristic_term]))
#     )
#     fig = go.Figure(data=[scatter, correlation])
#     fig.update_layout(
#         title_text=new_search_term + ' Search Popularity by %s of State' % characteristic_term,
#         xaxis_title=characteristic_term,
#         yaxis_title=new_search_term + ' Search Popularity',
#     )
#     return fig


@app.callback(
    dash.dependencies.Output('solutions-output', 'children'),
    [dash.dependencies.Input('solutions-dropdown', 'value')])
def update_output(user_input):
    if(user_input is None):
        return "Pick an option from the dropdown to see what is the most critical solution"
    else:
        user_solution_reduction = (
            solutions_df.loc[solutions_df['name'] == user_input]).iloc[0]["total_atmospheric_reduction"]
        user_percent = str(
            round((user_solution_reduction / total_reduction) * 100, 2)) + "%"

        heuristic_text = {
            0: "You're right! You're very informed about climate change.",
            1: "You're pretty close.",
            2: "Surprised that there were more impactful solutions?"
        }

        guess_index = (
            solutions_df.loc[solutions_df['name'] == user_input]).index.tolist()[0]
        if guess_index == 0:
            close_heuristic = heuristic_text[0]
        elif guess_index <= 10:
            close_heuristic = heuristic_text[1]
        else:
            close_heuristic = heuristic_text[2]
        additional_prose = " It turns out, the most impactful solution is Refrigerant Management. Out of the total 1034 billions of dollars that the proposed solutions save, the top solution accounts for 8.67% of that total."

        # return 'You have selected {}'.format(user_input) + "which reduces " + user_percent + " of the total atmospheric reduction"
        return close_heuristic + additional_prose


if __name__ == '__main__':
    app.run_server(debug=True)
