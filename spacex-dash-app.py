# SpaceX Launch Records Dashboard (Plotly Dash)


import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# ---- Load Data ---------------------------------------------------------
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# ---- App Initialization ------------------------------------------------
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center'}),

    # TASK 1 — Launch Site Dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=([{'label': 'All Sites', 'value': 'ALL'}] +
                 [{'label': s, 'value': s}
                  for s in sorted(spacex_df['Launch Site'].unique())]),
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True,
        style={'width': '80%', 'margin': '0 auto'}
    ),

    html.Br(),

    # Pie Chart (success count)
    dcc.Graph(id='success-pie-chart'),

    html.Br(),
    html.P("Payload range (Kg):", style={'textAlign': 'center'}),

    # TASK 3 — Payload Range Slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks={i: str(i) for i in range(0, 10001, 2500)},
        value=[min_payload, max_payload],
        tooltip={"placement": "bottom", "always_visible": True}
    ),

    html.Br(),

    # Scatter Plot (Payload vs Outcome)
    dcc.Graph(id='success-payload-scatter-chart'),
], style={'maxWidth': 1100, 'margin': '0 auto'})

# TASK 2 — Callback for Pie Chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie(selected_site):
    if selected_site == 'ALL':
        # Success counts by site
        fig = px.pie(spacex_df,
                     values='class',
                     names='Launch Site',
                     title='Total Successful Launches by Site')
    else:
        df_site = spacex_df[spacex_df['Launch Site'] == selected_site]
        counts = (df_site['class']
                  .value_counts()
                  .rename(index={0: 'Failure', 1: 'Success'})
                  .reset_index())
        counts.columns = ['Outcome', 'Count']
        fig = px.pie(counts,
                     values='Count',
                     names='Outcome',
                     title=f'Total Launch Outcomes for {selected_site}')
    return fig

# TASK 4 — Callback for Scatter Plot
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & \
           (spacex_df['Payload Mass (kg)'] <= high)
    df = spacex_df[mask]
    if selected_site != 'ALL':
        df = df[df['Launch Site'] == selected_site]

    fig = px.scatter(
        df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Launch Site'],
        labels={'class': 'Launch Outcome (1=Success, 0=Failure)'},
        title=('Correlation between Payload and Success for All Sites'
               if selected_site == 'ALL'
               else f'Correlation between Payload and Success for {selected_site}')
    )
    return fig

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=False)