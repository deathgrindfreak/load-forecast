import plotly.graph_objects as go
import pandas as pd
import numpy as np
import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.figure_factory as ff
import dash_bootstrap_components as dbc
import dash_table
import pyodbc
import os
from dash import no_update

from flask import app

conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                      'SERVER=SV-GEOSCADA\SQLEXPRESS;'
                      'DATABASE=loadForecast;'
                      'Trusted_Connection=yes;')


#############################################################
#                Data Manipulation / Model
#############################################################

def fetch_data(q):
    result = pd.read_sql(
        sql=q,
        con=conn
    )
    return result


def get_items(selected_filter):

    items_query = (
        f'''
        SELECT DISTINCT {selected_filter}
        FROM test
        '''
    )
    items_df = fetch_data(items_query)
    items_list = list(items_df[selected_filter].sort_values(ascending=False))
    return items_list


def get_wids(selected_filter, selected_items):

    table_query = (
        f'''
        SELECT WID
        FROM test
        WHERE {selected_filter} = '{selected_items}'
        '''
    )
    wid_df = fetch_data(table_query)
    wid_ints = wid_df['WID'].tolist()
    wid_list = [str(wid_ints) for wid_ints in wid_ints]
    return wid_list


def get_graphdf(wid_list):

    graph_query = (
        f'''
            SELECT DOFP, Load
            FROM graph
            WHERE WID
            IN ('%s')
            GROUP BY DOFP, Load
            ORDER BY DOFP, Load
            '''
        % ("','".join(wid_list))
    )
    graphdf = fetch_data(graph_query)
    return graphdf


# For calculating summary Table
def calculate_table(wid_list):

    table_query = (
        f'''
        SELECT *
        FROM test
        WHERE WID
        IN ('%s')
        '''
        % ("','".join(wid_list))
    )
    summary_table = fetch_data(table_query)
    return summary_table


def draw_graph(graphdf):

    figure = go.Figure(
        data=[
            go.Scatter(x=graphdf['DOFP'], y=graphdf['Load'], mode='lines+markers')
        ],
        layout=go.Layout(
            title='Amperage',
            showlegend=False
        )
    )
    return figure


def generate_table(dataframe, max_rows=10):

    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


#############################################################
#                Dashboard Components
#############################################################


filter_card = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Card title", className="card-title"),
            dbc.ListGroup(
                [
                    dbc.ListGroupItem(
                        dcc.Dropdown(id='filter-selector',
                                      options=[
                                          {'label': 'Production Area', 'value': 'prodArea'},
                                          {'label': 'Meter', 'value': 'meter'},
                                          {'label': 'Project', 'value': 'project'},
                                      ])
                    ),
                    dbc.ListGroupItem(
                        dcc.Dropdown(id='item-selector')
                    ),
                    dbc.ListGroupItem(
                        dcc.Slider(id='date-slider')
                    )
                ],flush=True
            )
        ]
    )
)

graph_card = dbc.Card(
    dbc.CardBody(
        dcc.Graph(id='item-graph')
    ), color="dark", outline=True,
)


data_table = dash_table.DataTable(id='results-table',
                                  #columns=[{"name": i, "id": i} for i in welldf.columns],
                                  #data=welldf.to_dict('records')
                                  )

#############################################################
#                Dashboard Layout / View
#############################################################


app = dash.Dash(external_stylesheets=[dbc.themes.FLATLY])

app.layout = html.Div([

    # Title Row
    dbc.Row(
        dbc.Col(
                html.H1("CQ Sparky"),
                width=4,
                align="center",
        )
    ),

    # Graph Row
    dbc.Row(
        [
            # Dropdown Card
            dbc.Col(
                filter_card,
                width=4,
            ),
            # Graph Card
            dbc.Col(
                graph_card,
                width=8,
            )
        ]
    ),

    # Table Row
    dbc.Row(
        dbc.Col(
            data_table,
            width=10,
            align="center",
        )
    ),
])


#############################################################
#         Interaction Between Components / Controller
#############################################################


# Load Items in Item Dropdown
@app.callback(
    Output(component_id='item-selector', component_property='options'),
    [Input(component_id='filter-selector', component_property='value')]
)
def populate_item_selector(selected_filter):
    items_list = get_items(selected_filter)
    items_dict = [{'label': items_list, 'value': items_list} for items_list in items_list]
    if selected_filter is None:
        return no_update
    else:
        return items_dict


# Update Graph
@app.callback(
    Output(component_id='item-graph', component_property='figure'),
    [Input(component_id='filter-selector', component_property='value'),
     Input(component_id='item-selector', component_property='value')]
)
def load_item_points_graph(selected_filter, selected_items):
    results = get_wids(selected_filter, selected_items)
    results_df = get_graphdf(results)

    figure = []
    if len(results) > 0:
        figure = draw_graph(results_df)
        return figure
    else:
        return no_update


# start Flask server
if __name__ == '__main__':
    app.run_server(debug=True)