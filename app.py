import os
import dash
from dash import dcc
from dash import html
from datetime import datetime
from dash import dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc


df = pd.read_csv("reorg-data.csv")
df_table = df.rename(columns={"slot": "Slot", "cl_client": "CL Client", "validator_id": "Val. ID", "date": "Date", "slot_in_epoch": "Slot Nr. in Epoch"})
df_table.sort_values("Slot", ascending=False, inplace=True)


df_per_sie = df['slot_in_epoch'].value_counts().reset_index()
df_per_sie.set_index('slot_in_epoch', inplace=True)
df_per_sie = df_per_sie.reindex(range(0, 32))
df_per_sie.fillna(0, inplace=True)
df_per_sie.reset_index(inplace=True)
df_per_sie.rename(columns={'index': 'slot_in_epoch'}, inplace=True)

# Create a figure using Plotly Express
fig = px.histogram(df, x='date', title='Number of Missed Blocks Over Date', nbins=100)
fig2 = px.bar(df['cl_client'].value_counts().reset_index(), x='count', y='cl_client', title='Number of Missed Slots per Client', labels={'cl_client': 'Client', 'cl_client': 'Count'})
fig3 = go.Figure(data=go.Bar(x=df_per_sie['slot_in_epoch'], y=df_per_sie['count']))

# Set title and labels
fig3.update_layout(
    title='Number of Missed Slots per Slot Nr. in Epoch',
    xaxis_title='Slot in Epoch',
    yaxis_title='Count'
)

# Set x-axis ticks
fig3.update_xaxes(tickvals=list(range(32)))
# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
#app = JupyterDash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def update_styles(selected_cells, data):
    if selected_cells:
        row = selected_cells[0]['row']
        col = selected_cells[0]['column_id']
        if col == 'slot':
            slot = data[row]['slot']
            link = f"https://beaconcha.in/slot/{slot}"
            webbrowser.open(link, new=2)
            return []
    return []

app.layout = dbc.Container(
    [
        dbc.Row(html.H1("Reorg Dashboard", style={'text-align': 'center'}), className="mb-4"),
        dbc.Row(
            html.H5(
                ['Built with 🖤 by ',
                 html.A('Toni Wahrstätter', href='https://twitter.com/nero_eth', target='_blank')]
            ), className="mb-4"),
        dbc.Row(
            dbc.Col(
                dash_table.DataTable(
                    style_cell_conditional=[
                        {'if': {'column_id': 'Slot Nr. in Epoch'}, 'maxWidth': '30px', 'text-align': 'center'},
                        {'if': {'column_id': 'Slot'}, 'textAlign': 'right', 'maxWidth': '30px'},
                        {'if': {'column_id': 'Val. ID'}, 'maxWidth': '30px'},
                        {'if': {'column_id': 'Date'}, 'maxWidth': '80px'},
                        {'if': {'column_id': 'CL Client'}, 'maxWidth': '80px'}
                    ],
                    id='table',
                    columns=[{"name": i, "id": i, 'presentation': 'markdown'} if i == 'Slot' else {"name": i, "id": i} for i in df_table.columns],
                    data=df_table.to_dict('records'),
                    page_size=50,
                    style_table={'overflowX': 'auto'},
                    style_cell={'whiteSpace': 'normal','height': 'auto'},
                    style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}],
                    style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                    style_header_conditional=[
                        {'if': {'column_id': 'Slot'}, 'text-align': 'center'},
                        {'if': {'column_id': 'Slot Nr. in Epoch'}, 'text-align': 'center'},
                    ],
                    css=[dict(selector="p", rule="margin: 0; text-align: center")],

                ),
                className="mb-4", # margin bottom
                md=12 # Full width on medium and larger screens

            )
        ),
        dbc.Row(dbc.Col(dcc.Graph(id='graph1', figure=fig), md=12, className="mb-4")), # Full width on medium and larger screens, margin bottom
        dbc.Row(dbc.Col(dcc.Graph(id='graph2', figure=fig2), md=12, className="mb-4")), # Full width on medium and larger screens, margin bottom
        dbc.Row(dbc.Col(dcc.Graph(id='graph3', figure=fig3), md=12, className="mb-4")), # Full width on medium and larger screens, margin bottom
    ],
    fluid=True, # Full-width layout
)


if __name__ == '__main__':
    #app.run_server(debug=True)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)