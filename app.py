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
from dash import Input, Output


# Data preparation
def prepare_data():
    df = pd.read_csv("reorg-data.csv")
    df_table = df.rename(columns={"slot": "Slot", "cl_client": "CL Client", "validator_id": "Val. ID", "date": "Date", "slot_in_epoch": "Slot Nr. in Epoch"})
    df_table.sort_values("Slot", ascending=False, inplace=True)

    df_per_sie = df['slot_in_epoch'].value_counts().reset_index()
    df_per_sie.set_index('slot_in_epoch', inplace=True)
    df_per_sie = df_per_sie.reindex(range(0, 32))
    df_per_sie.fillna(0, inplace=True)
    df_per_sie.reset_index(inplace=True)
    df_per_sie.rename(columns={'index': 'slot_in_epoch'}, inplace=True)

    return df, df_table, df_per_sie

# Figures
def create_figures(df, df_per_sie):
    fig1 = px.histogram(df, x='date', nbins=100)
    fig1.update_layout(
        title='Number of Missed Blocks Over Date',
        xaxis_title='Date',
        margin=dict(l=20, r=20, t=40, b=20)
    )
    fig1.update_yaxes(title_standoff=5)

    fig2 = px.bar(df['cl_client'].value_counts().reset_index(), x='count', y='cl_client', labels={'cl_client': 'Client', 'count': ''})
    fig2.update_layout(
        title='Number of Missed Slots per Client',
        xaxis_title='Slot in Epoch',
        margin=dict(l=20, r=20, t=40, b=20)
    )
    fig2.update_yaxes(title_standoff=5)

    fig3 = go.Figure(data=go.Bar(x=df_per_sie['slot_in_epoch'], y=df_per_sie['count']))
    fig3.update_layout(
        title='Number of Missed Slots per Slot Nr. in Epoch',
        xaxis_title='Slot in Epoch',
        yaxis_title='',
        margin=dict(l=20, r=20, t=40, b=20)
    )
    fig3.update_yaxes(title_standoff=5)
    fig3.update_xaxes(tickvals=list(range(32)))

    return fig1, fig2, fig3

df, df_table, df_per_sie = prepare_data()
fig1, fig2, fig3 = create_figures(df, df_per_sie)

# Layout based on window size
def get_layout(width):
    if width <= 800:
        font_size = 8
    else:
        font_size = 20

    return dict(
        title='Number of Missed Slots per Slot Nr. in Epoch',
        xaxis_title='Slot in Epoch',
        yaxis_title='',
        margin=dict(l=20, r=20, t=40, b=20),
        font={'size': font_size}
    )

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.scripts.append_script({"external_url": "update_window_width.js"})
app.clientside_callback(
    "window.dash_clientside.update_window_size",
    Output('window-size-store', 'data'),
    Input('window-size-trigger', 'n_intervals')
)
server = app.server



app.layout = dbc.Container(
    [
        # Title
        dbc.Row(html.H1("Reorg Dashboard", style={'text-align': 'center'}), className="mb-4"),

        # Author
        dbc.Row(
            html.H5(
                ['Built with 🖤 by ', html.A('Toni Wahrstätter', href='https://twitter.com/nero_eth', target='_blank')]
            ), className="mb-4"),

        # DataTable
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
                    columns=[
                        {"name": i, 
                         "id": i, 
                         'presentation': 'markdown'} if i == 'Slot' else {"name": i, "id": i} for i in df_table.columns
                    ],
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
                className="mb-4", md=12
            )
        ),

        # Graphs
        dbc.Row(dbc.Col(dcc.Graph(id='graph1', figure=fig1), md=12, className="mb-4")),
        dbc.Row(dbc.Col(dcc.Graph(id='graph2', figure=fig2), md=12, className="mb-4")),
        dbc.Row(dbc.Col(dcc.Graph(id='graph3', figure=fig3), md=12, className="mb-4")),

        # Additional Components
        dbc.Row(dcc.Interval(id='window-size-trigger', interval=1000, n_intervals=0)),
        dcc.Store(id='window-size-store')
    ],
    fluid=True,
)


# Callbacks
@app.callback(
    Output('graph3', 'figure'),
    Input('window-size-store', 'data')
)
def update_layout(window_size_data):
    if window_size_data is None:
        raise dash.exceptions.PreventUpdate

    width = window_size_data['width']
    fig3.update_layout(**get_layout(width))
    return fig3


if __name__ == '__main__':
    #app.run_server(debug=True)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
