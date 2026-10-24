# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Load the SpaceX launch data
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create the Dash application
app = dash.Dash(__name__)

# Page layout: what appears on the screen
app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={
            'textAlign': 'center',
            'color': '#503D36',
            'font-size': 40
        }
    ),

    # TASK 1: Launch-site dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] + [
            {'label': site, 'value': site}
            for site in sorted(spacex_df['Launch Site'].dropna().unique())
        ],
        value='ALL',
        placeholder='Select a Launch Site',
        searchable=True
    ),
    html.Br(),

    # TASK 2: The pie chart's place on the page
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Range slider will go here
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        value=[min_payload, max_payload],
        marks={0: '0', 2500: '2,500', 5000: '5,000',
           7500: '7,500', 10000: '10,000'}
    ),
    # TASK 4: Scatter chart's place on the page
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Tell the pie chart how to react to the dropdown
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        counts = (
            spacex_df.loc[spacex_df['class'] == 1, 'Launch Site']
            .value_counts()
            .rename_axis('Launch Site')
            .reset_index(name='Successes')
        )
        return px.pie(
            counts,
            names='Launch Site',
            values='Successes',
            title='Successful landings by launch site'
        )

    counts = (
        spacex_df.loc[spacex_df['Launch Site'] == entered_site, 'class']
        .map({0: 'Did not land', 1: 'Landed'})
        .value_counts()
        .rename_axis('Outcome')
        .reset_index(name='Launches')
    )
    return px.pie(
        counts,
        names='Outcome',
        values='Launches',
        title=f'Landing outcomes at {entered_site}'
    )

# TASK 4: Scatter-chart callback will go here later
# TASK 4: Update the scatter plot when either input changes
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    Input('site-dropdown', 'value'),
    Input('payload-slider', 'value')
)
def get_scatter_chart(entered_site, payload_range):
    filtered_df = spacex_df[
        spacex_df['Payload Mass (kg)'].between(
            payload_range[0], payload_range[1]
        )
    ]

    if entered_site != 'ALL':
        filtered_df = filtered_df[
            filtered_df['Launch Site'] == entered_site
        ]

    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Launch Site'],
        title='Landing outcome by payload mass'
    )
    fig.update_yaxes(
        tickvals=[0, 1],
        ticktext=['Did not land', 'Landed']
    )
    return fig
# Run the app
if __name__ == '__main__':
    app.run()