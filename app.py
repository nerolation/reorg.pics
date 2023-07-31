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
from plotly.subplots import make_subplots


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

def fig3_layout(width=801):
    if width <= 800:
        font_size = 8
    else:
        font_size = 16
    return dict(
        title=f'<span style="font-size: {font_size}px;font-weight:bold;>Slot Missed in Epoch</span>',
        xaxis_title='Date',
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(family="Ubuntu Mono", size = font_size),
        updatemenus=[dict(
            buttons=[
                dict(args=[{"visible": [True,False,False,False]},
                           {}],
                    label="24 hours",
                    method="update"
                )
                ,
                dict(args=[{"visible": [False,True,False,False]},
                               {"title": f'<span style="font-size: {font_size}px;font-weight:bold;">Number of Missed Blocks Over Date</span>',}],
                        label="48 hours",
                        method="update"
                ),
                dict(args=[{"visible": [False,False,True,False]},
                           {}],
                    label="7 days",
                    method="update"
                )
                ,
                dict(args=[{"visible": [False,False,False,True]},
                               {}],
                        label="14 days",
                        method="update"
                )
                ],
            showactive= True,
            direction= 'down',
            active= 1,
            x= 1.0, 
            xanchor= 'right', 
            y= 1.15, 
            yanchor= 'top'
        )]
    )

def create_fig3(df_per_sie):
    fig3 = make_subplots(rows=1, cols=1)
    fig3.add_trace(
        go.Bar(x=df_per_sie['slot_in_epoch'], y=df_per_sie['count'], visible=False, marker=dict(color='#1f77b4'))
    )
    fig3.add_trace(
        go.Bar(x=df_per_sie['slot_in_epoch'], y=df_per_sie['count'], visible=False, marker=dict(color='#1f77b4')))
    fig3.add_trace(
        go.Bar(x=df_per_sie['slot_in_epoch'], y=df_per_sie['count'], marker=dict(color='#1f77b4'))
    )
    fig3.add_trace(
        go.Bar(x=df_per_sie['slot_in_epoch'], y=df_per_sie['count'], visible=False, marker=dict(color='#1f77b4'))
    )


    fig3.update_layout(**fig3_layout())
    fig3.update_yaxes(title_standoff=5)
    return fig3

def fig2_layout(width=801):
    if width <= 800:
        font_size = 8
    else:
        font_size = 16
    return dict(
        title=f'<span style="font-size: {font_size}px;font-weight:bold;">Relative Share of Missed Slots per Client <span style="font-size:{font_size-3}px;">(last 14 days)</span></span>',
        xaxis_title='%',
        yaxis_title='Client',
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(family="Ubuntu Mono", size = font_size),
        updatemenus=[dict(
            buttons=[
                dict(args=[{"visible": [True,False]},
                           {"title": f'<span style="font-size: {font_size}px;font-weight:bold;">Relative Share of Missed Slots per Client <span style="font-size:{font_size-3}px;">(last 14 days)</span></span>',
                            # "height":500,
                            "xaxis.title": "%",
                            #"annotations": k
                           }],
                    label="Relative",
                    method="update"
                )
                ,
                dict(args=[{"visible": [False,True]},
                               {"title": f'<span style="font-size: {font_size}px;font-weight:bold;">Absulute Nr. of Missed Slots per Client <span style="font-size:{font_size-3}px;">(last 14 days)</span></span>',
                                # "height":500,
                                "xaxis.title": "slots",
                                #"annotations": k
                               }],
                        label="Absolute",
                        method="update"
                )
                ],
            showactive= True,
            direction= 'down',
            active= 0,
            x= 1.0, 
            xanchor= 'right', 
            y= 1.15, 
            yanchor= 'top'
        )]   
    )


def create_fig2(df):
    _df = df['cl_client'].value_counts().reset_index()
    _df["relative_count"] = round(_df['count']/_df['count'].sum()*100, 0)
    fig2 = make_subplots(rows=1, cols=1)
    fig2.add_trace(
        go.Bar(x=_df['relative_count'], y=_df['cl_client'], orientation='h', 
               marker=dict(color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])) # Add more colors if needed
    )

    fig2.add_trace(
        go.Bar(
            x=_df['count'], y=_df['cl_client'], orientation='h', 
            marker=dict(color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']), visible=False
        )
    )
    fig2.update_layout(**fig2_layout())
    fig2.update_yaxes(title_standoff=5)
    return fig2

def fig1_layout(width=801):
    if width <= 800:
        font_size = 8
    else:
        font_size = 16
    return dict(
        title=f'<span style="font-size: {font_size}px;font-weight:bold;">Number of Missed Blocks Over Date</span>',
        xaxis_title='Date',
        yaxis_title='#Blocks',
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(family="Ubuntu Mono", size = font_size),
        updatemenus=[dict(
            buttons=[
                dict(args=[{"visible": [True,False,False,False]},
                           {}],
                    label="500 bins",
                    method="update"
                )
                ,
                dict(args=[{"visible": [False,True,False,False]},
                               {}],
                        label="100 bins",
                        method="update"
                ),
                dict(args=[{"visible": [False,False,True,False]},
                           {}],
                    label="50 bins",
                    method="update"
                )
                ,
                dict(args=[{"visible": [False,False,False,True]},
                               {}],
                        label="20 bins",
                        method="update"
                )
                ],
            showactive= True,
            direction= 'down',
            active= 1,
            x= 1.0, 
            xanchor= 'right', 
            y= 1.15, 
            yanchor= 'top'
        )]
    )

def create_fig1(df):
    fig1 = make_subplots(rows=1, cols=1)
    fig1.add_trace(
        go.Histogram(x=df['date'], nbinsx=500, visible=False, marker=dict(color='#1f77b4'))
    )
    fig1.add_trace(
        go.Histogram(x=df['date'], nbinsx=100, marker=dict(color='#1f77b4'))
    )
    fig1.add_trace(
        go.Histogram(x=df['date'], nbinsx=50, visible=False, marker=dict(color='#1f77b4'))
    )
    fig1.add_trace(
        go.Histogram(x=df['date'], nbinsx=20, visible=False, marker=dict(color='#1f77b4'))
    )


    fig1.update_layout(**fig1_layout())
    fig1.update_yaxes(title_standoff=5)
    return fig1


# Figures
def create_figures(df, df_per_sie):
    fig1 = create_fig1(df)
    fig2 = create_fig2(df)
    fig3 = create_fig3(df_per_sie)
    return fig1, fig2, fig3

df, df_table, df_per_sie = prepare_data()
fig1, fig2, fig3 = create_figures(df, df_per_sie)

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.scripts.append_script({"external_url": "update_window_width.js"})
app.clientside_callback(
    "window.dash_clientside.update_window_size",
    Output('window-size-store', 'data'),
    Input('window-size-trigger', 'n_intervals')
)
app.title = 'Reorg.pics'
server = app.server

def table_styles(width):
    font_size = '16px' if width >= 800 else '10px'

    return [
        {'if': {'column_id': 'Slot Nr. in Epoch'}, 'maxWidth': '30px', 'text-align': 'center', 'fontSize': font_size},
        {'if': {'column_id': 'Slot'}, 'textAlign': 'right', 'maxWidth': '30px', 'fontSize': font_size},
        {'if': {'column_id': 'Val. ID'}, 'maxWidth': '30px', 'fontSize': font_size},
        {'if': {'column_id': 'Date'}, 'maxWidth': '80px', 'fontSize': font_size},
        {'if': {'column_id': 'CL Client'}, 'maxWidth': '80px', 'fontSize': font_size}
    ]

app.layout = dbc.Container(
    [
        # Title
        dbc.Row(html.H1("Reorg Dashboard", style={'text-align': 'center','margin-top': '20px'}), className="mb-4"),

        html.H5(
            ['Built with 🖤 by ', html.A('Toni Wahrstätter', href='https://twitter.com/nero_eth', target='_blank')],
            className="mb-4 smaller-text" # Apply the class
        ),

        # DataTable
        dbc.Row(
            dbc.Col(
                dash_table.DataTable(
                    style_cell_conditional=table_styles(799),
                    id='table',
                    columns=[
                        {"name": i, 
                         "id": i, 
                         'presentation': 'markdown'} if i == 'Slot' else {"name": i, "id": i} for i in df_table.columns
                    ],
                    data=df_table.to_dict('records'),
                    page_size=20,
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
        dbc.Row(dcc.Interval(id='window-size-trigger', interval=5000, n_intervals=0, max_intervals=1)),
        dcc.Store(id='window-size-store',data={'width': 800})
    ],
    fluid=True,
)




# Callbacks

@app.callback(
    Output('table', 'style_cell_conditional'),
    Input('window-size-store', 'data')
)
def update_table_styles(window_size_data):
    if window_size_data is None:
        raise dash.exceptions.PreventUpdate

    window_width = window_size_data['width']
    return table_styles(window_width)


@app.callback(
    Output('graph1', 'figure'),
    Input('window-size-store', 'data')
)
def update_layout1(window_size_data):
    if window_size_data is None:
        raise dash.exceptions.PreventUpdate
    width = window_size_data['width']
    fig1.update_layout(**fig1_layout(width))
    return fig1

@app.callback(
    Output('graph2', 'figure'),
    Input('window-size-store', 'data')
)
def update_layout2(window_size_data):
    if window_size_data is None:
        raise dash.exceptions.PreventUpdate
    width = window_size_data['width']
    fig2.update_layout(**fig2_layout(width))
    return fig2

@app.callback(
    Output('graph3', 'figure'),
    Input('window-size-store', 'data')
)
def update_layout3(window_size_data):
    if window_size_data is None:
        raise dash.exceptions.PreventUpdate
    width = window_size_data['width']
    fig3.update_layout(**fig3_layout(width))
    return fig3

if __name__ == '__main__':
    #app.run_server(debug=True)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
