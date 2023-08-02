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
import numpy as np
from dash import Input, Output
from plotly.subplots import make_subplots


# Data preparation
def prepare_data():
    df = pd.read_csv("reorg-data.csv")
    #df = df[~df['cl_client'].str.contains('Unknown')]
    df2 = pd.read_csv("validator_slots.csv")
    df2 = df2[~df2['validator'].str.contains('Unknown')]
    df3 = pd.read_csv("relay_slots.csv")
    df3 = df3[~df3['relay'].str.contains('Unknown')]
    df4 = pd.read_csv("builder_slots.csv")
    df4 = df4[~df4['builder'].str.contains('Unknown')]
    df5 = pd.read_csv("clclient_slots.csv")
    df5 = df5[~df5['cl_client'].str.contains('Unknown')]
    
    def max_slot(slot):
        return int(slot.split("[")[1].split("]")[0])
    
    dfreorger = pd.read_csv("reorgers-data.csv")
    dfreorger = dfreorger[dfreorger["slot"].apply(max_slot) > max(dfreorger["slot"].apply(max_slot)) - 7200*60]
    
    df_30 = df[df["slot"].apply(max_slot) > max(df["slot"].apply(max_slot)) - 7200*30]
    df_table = df_30.rename(columns={"slot": "Slot", "cl_client": "CL Client", "validator_id": "Val. ID", "date": "Date", "slot_in_epoch": "Slot Nr. in Epoch"})
    df_table.sort_values("Slot", ascending=False, inplace=True)
    df_table = df_table[["Slot", "CL Client", "Val. ID", "Date", "Slot Nr. in Epoch"]].drop_duplicates()
    #df_table["Val. ID"] = df_table["Val. ID"]#.replace(0, np.NaN)
    df_table["Slot Nr. in Epoch"] = df_table["Slot Nr. in Epoch"].astype(int)
    df_table["Val. ID"] = df_table["Val. ID"].astype(int)
    #df_table['slot_sort'] = df_table['Slot'].apply(lambda x: int(x.split("[")[1].split("]")[0]))  # Update the split function as needed

    
    df = df[~df['cl_client'].str.contains('Unknown')]
    
    df_90 = df[df["slot"].apply(max_slot) > max(df["slot"].apply(max_slot)) - 7200*90]
    df_60 = df[df["slot"].apply(max_slot) > max(df["slot"].apply(max_slot)) - 7200*60]
    df_30 = df[df["slot"].apply(max_slot) > max(df["slot"].apply(max_slot)) - 7200*30]
    df_14 = df[df["slot"].apply(max_slot) > max(df["slot"].apply(max_slot)) - 7200*14]
    df_7 = df[df["slot"].apply(max_slot) > max(df["slot"].apply(max_slot)) - 7200*7]
    
    
    
    df_per_sie_60 = df_60.groupby(["cl_client", "slot_in_epoch"])['slot'].count().reset_index().sort_values("slot_in_epoch")
    #df_per_sie_60.set_index('slot_in_epoch', inplace=True)
    #print(df_per_sie_60)
    #df_per_sie_60 = df_per_sie_60.reindex(range(0, 32))
    #df_per_sie_60.fillna(0, inplace=True)
    #df_per_sie_60.reset_index(inplace=True)
    #df_per_sie_60.rename(columns={'index': 'slot_in_epoch'}, inplace=True)
    
    df_per_sie_30 = df_30.groupby(["cl_client", "slot_in_epoch"])['slot'].count().reset_index().sort_values("slot_in_epoch")
    #df_per_sie_30.set_index('slot_in_epoch', inplace=True)
    #df_per_sie_30 = df_per_sie_30.reindex(range(0, 32))
    #df_per_sie_30.fillna(0, inplace=True)
    #df_per_sie_30.reset_index(inplace=True)
    #df_per_sie_30.rename(columns={'index': 'slot_in_epoch'}, inplace=True)
    
    df_per_sie_14 = df_14.groupby(["cl_client", "slot_in_epoch"])['slot'].count().reset_index().sort_values("slot_in_epoch")
    #df_per_sie_14.set_index('slot_in_epoch', inplace=True)
    #df_per_sie_14 = df_per_sie_14.reindex(range(0, 32))
    #df_per_sie_14.fillna(0, inplace=True)
    #df_per_sie_14.reset_index(inplace=True)
    #df_per_sie_14.rename(columns={'index': 'slot_in_epoch'}, inplace=True)
    
    df_per_sie_7 = df_7.groupby(["cl_client", "slot_in_epoch"])['slot'].count().reset_index().sort_values("slot_in_epoch")
    #df_per_sie_7.set_index('slot_in_epoch', inplace=True)
    #df_per_sie_7 = df_per_sie_7.reindex(range(0, 32))
    #df_per_sie_7.fillna(0, inplace=True)
    #df_per_sie_7.reset_index(inplace=True)
    #df_per_sie_7.rename(columns={'index': 'slot_in_epoch'}, inplace=True)

    return df_90, df_60, df_30, df_14, df_7, df_table, df_per_sie_60, df_per_sie_30, df_per_sie_14, df_per_sie_7, df2, df3, df4, df5, dfreorger

def fig3_layout(width=801):
    if width <= 800:
        font_size = 10
    else:
        font_size = 18
    return dict(
        title=f'<span style="font-size: {font_size}px;font-weight:bold;">Slot Nr. Missed in Epoch</span>',
        xaxis_title='Date',
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(family="Ubuntu Mono", size = font_size),
        barmode='stack',
        legend=dict(
            x=1,           # x position of the legend (1 corresponds to the right end of the plot)
            y=1,           # y position of the legend (1 corresponds to the top of the plot)
            xanchor="auto",  # x anchor of the legend
            yanchor="auto",  # y anchor of the legend
            bgcolor="rgba(255, 255, 255, 0.5)" # You can set a background color for readability if needed
        ),
        xaxis=dict(
            fixedrange=True, # Disables zooming/panning on the x-axis,
            tickvals=list(range(32))
        ),
        yaxis=dict(
            fixedrange=True # Disables zooming/panning on the y-axis
        ),
        updatemenus=[dict(
            buttons=[
                dict(args=[{"visible": [True if i %4==0 else False for i in range(20)]},
                           {}],
                    label="60 days",
                    method="update"
                )
                ,
                dict(args=[{"visible": [True if i %4==1 else False for i in range(20)]},
                               {"title": f'<span style="font-size: {font_size}px;font-weight:bold;">Slot Nr. Missed in Epoch</span>',}],
                        label="30 days",
                        method="update"
                ),
                dict(args=[{"visible": [True if i %4==2 else False for i in range(20)]},
                           {}],
                    label="14 days",
                    method="update"
                )
                ,
                dict(args=[{"visible": [True if i %4==3 else False for i in range(20)]},
                               {}],
                        label="7 days",
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

def create_fig3(df_per_sie_60, df, df_per_sie_14, df_per_sie_7):
    fig = make_subplots(rows=1, cols=1)
    df_per_sie_60 = df_per_sie_60[df_per_sie_60["cl_client"] != "missed"]
    df = df[df["cl_client"] != "missed"]
    df_per_sie_14 = df_per_sie_14[df_per_sie_14["cl_client"] != "missed"]
    df_per_sie_7 = df_per_sie_7[df_per_sie_7["cl_client"] != "missed"]
    

    # Colors array (can be extended with more colors)
    colors = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ]

    # Add traces for each client
    for i, client in enumerate(df["cl_client"].unique()):
        visible = True
        for j in (df_per_sie_60, df, df_per_sie_14, df_per_sie_7):
            k = j[j["cl_client"] == client]
            fig.add_trace(go.Bar(x=k["slot_in_epoch"], y=k["slot"], name=client, marker_color=colors[i], visible=visible))
            visible = False
        


    fig.update_layout(**fig3_layout())
    fig.update_yaxes(title_standoff=5)
    return fig

def fig2_layout(width=801):
    if width <= 800:
        font_size = 10
    else:
        font_size = 18
    return dict(
        title=f'<span style="font-size: {font_size}px;font-weight:bold;">Relative Share of Missed Slots per Client<br><span style="font-size:{font_size-3}px;">(last 60 days)</span></span>',
        xaxis_title='%',
        yaxis_title='Client',
        margin=dict(l=20, r=20, t=80, b=20),
        font=dict(family="Ubuntu Mono", size = font_size),
                xaxis=dict(
            fixedrange=True # Disables zooming/panning on the x-axis
        ),
        yaxis=dict(
            fixedrange=True # Disables zooming/panning on the y-axis
        ),
        updatemenus=[dict(
            type="buttons",
            buttons=[
                dict(args=[{"visible": [True,False]},
                           {"title": f'<span style="font-size: {font_size}px;font-weight:bold;">Relative Share of Missed Slots per Client<br><span style="font-size:{font_size-3}px;">(last 60 days)</span></span>',
                            # "height":500,
                            "xaxis.title": "%",
                            #"annotations": k
                           }],
                    label="Relative",
                    method="update"
                )
                ,
                dict(args=[{"visible": [False,True]},
                               {"title": f'<span style="font-size: {font_size}px;font-weight:bold;">Absulute Nr. of Missed Slots per Client<br><span style="font-size:{font_size-3}px;">(last 60 days)</span></span>',
                                # "height":500,
                                "xaxis.title": "slots",
                                #"annotations": k
                               }],
                        label="Absolute",
                        method="update"
                )
                ],
            showactive= True,
            direction= 'left',
            active= 0,
            x= 1.0, 
            xanchor= 'right', 
            y= 1.15, 
            yanchor= 'top'
        )]   
    )


def create_fig2(df_90, df, df_30, df_14, df_7, order):
    df = df[df["cl_client"] != "missed"]
    _df = df['cl_client'].value_counts().reset_index()
    _df = pd.merge(_df,order,how="left", left_on="cl_client", right_on="cl_client")
    _df["cl_client"]= _df["cl_client"].apply(lambda x: x[0].upper()+x[1:])
    _df.columns = ['cl_client', 'count', 'slots']
    _df["relative_count"] = round(_df['count'] / _df['slots'] * 100, 5)
    _df.sort_values("relative_count", ascending=False, inplace=True)
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
        font_size = 10
    else:
        font_size = 20
    return dict(
        title=f'<span style="font-size: {font_size}px;font-weight:bold;">Number of Missed Blocks Over Time</span>',
        xaxis_title='Date',
        yaxis_title='#Blocks',
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(family="Ubuntu Mono", size = font_size),
        legend=dict(
            x=0,           # x position of the legend (1 corresponds to the right end of the plot)
            y=1,           # y position of the legend (1 corresponds to the top of the plot)
            xanchor="auto",  # x anchor of the legend
            yanchor="auto",  # y anchor of the legend
            bgcolor="rgba(255, 255, 255, 0.7)" # You can set a background color for readability if needed
        ),
        xaxis=dict(
            fixedrange=True # Disables zooming/panning on the x-axis
        ),
        yaxis=dict(
            fixedrange=True # Disables zooming/panning on the y-axis
        ),
        updatemenus=[dict(
            type="buttons",
            buttons=[
                dict(args=[{"visible": [True if i%2==0 else False for i in range(10)]},
                           {}],
                    label="Absolute",
                    method="update"
                )
                ,
                dict(args=[{"visible": [True if i%2==1 else False for i in range(10)]},
                               {}],
                        label="Relative",
                        method="update"
                )
                ],
            showactive= True,
            direction= 'left',
            active= 0,
            x= 1.0, 
            xanchor= 'right', 
            y= 1.15, 
            yanchor= 'top'
        )]
    )

def create_fig1(df_90, df_60, df, df_14, df_7):
    df = df[df["cl_client"] != "missed"]
    fig1 = make_subplots(rows=1, cols=1)
    df.loc[:,"date"] = df["date"].apply(lambda x: x.split(" ")[0])
    grouped_data = df.groupby(["date","cl_client"])["slot"].count().reset_index()
    ordering = grouped_data.groupby("cl_client")["slot"].count().index.sort_values().values.tolist()
    grouped_data.set_index("cl_client", inplace=True)
    grouped_data = grouped_data.loc[ordering].reset_index()
    for i, j in grouped_data.iterrows():
        grouped_data.loc[i, "relative_count"] = float(j["slot"] / grouped_data[grouped_data["date"] == j["date"]]["slot"].sum())
 
        
        
    #grouped_data["relative_count"] = grouped_data["slot"]/grouped_data["sum"]

    # Add a trace for each unique client
    for client in grouped_data['cl_client'].unique():
        client_data = grouped_data[grouped_data['cl_client'] == client]
        fig1.add_trace(
            go.Scatter(x=client_data['date'], y=client_data['slot'], mode='lines', name=client, stackgroup='A')
        )
        fig1.add_trace(
            go.Scatter(x=client_data['date'], y=client_data['relative_count'], mode='lines', name=client, stackgroup='B', visible=False)
        )
        

    fig1.update_layout(**fig1_layout())
    fig1.update_yaxes(title_standoff=5)
    return fig1

def fig4_layout(width=801):
    if width <= 800:
        font_size = 10
    else:
        font_size = 20
    return dict(
        title=f'<span style="font-size: {font_size}px;font-weight:bold;">Relative Share of Missed Slots per Validator<br><span style="font-size:{font_size-3}px;">(last 60 days)</span></span>',
        xaxis_title='%',
        yaxis_title='Validator',
        margin=dict(l=20, r=20, t=80, b=20),
        font=dict(family="Ubuntu Mono", size=font_size),
        xaxis=dict(
            fixedrange=True # Disables zooming/panning on the x-axis
        ),
        yaxis=dict(
            fixedrange=True # Disables zooming/panning on the y-axis
        ),
        updatemenus=[dict(
            type="buttons",
            buttons=[
                dict(args=[{"visible": [True,False]},
                           {"title": f'<span style="font-size: {font_size}px;font-weight:bold;">Relative Share of Missed Slots per Validator<br><span style="font-size:{font_size-3}px;">(last 60 days)</span></span>',
                            "xaxis.title": "%",
                           }],
                    label="Relative",
                    method="update"
                ),
                dict(args=[{"visible": [False,True]},
                           {"title": f'<span style="font-size: {font_size}px;font-weight:bold;">Absolute Nr. of Missed Slots per Validator<br><span style="font-size:{font_size-3}px;">(last 60 days)</span></span>',
                            "xaxis.title": "slots",
                           }],
                    label="Absolute",
                    method="update"
                )
            ],
            showactive=True,
            direction='left',
            active=0,
            x=1.0,
            xanchor='right',
            y=1.15,
            yanchor='top'
        )]
    )


def create_fig_for_validators(df_90, df, df_30, df_14, df_7, order):
    df = df[df["validator"] != "missed"]
    _df = df['validator'].value_counts().reset_index()
    _df = pd.merge(_df,order,how="left", left_on="validator", right_on="validator")
    _df["validator"]= _df["validator"].apply(lambda x: x[0].upper()+x[1:])
    _df.columns = ['validator', 'count', 'slots']
    _df["relative_count"] = round(_df['count'] / _df['slots'] * 100, 5)
    _df = _df[_df["count"] > 0]
    _df["validator"] = _df["validator"].apply(lambda x: x[0:9]+"..." if x.startswith("0x") else x)
    _df.sort_values("relative_count", ascending=False, inplace=True)
    _df = _df.iloc[0:12]
    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(
        go.Bar(x=_df['relative_count'], y=_df['validator'], orientation='h',
               marker=dict(color = [
                '#1f77b4', # blue
                '#ff7f0e', # orange
                '#2ca02c', # green
                '#d62728', # red
                '#9467bd', # purple
                '#8c564b', # brown
                '#e377c2', # pink
                '#7f7f7f', # grey
                '#bcbd22', # olive
                '#17becf'  # teal
            ]) # Add more colors if needed
    ))

    fig.add_trace(
        go.Bar(
            x=_df['count'], y=_df['validator'], orientation='h',
            marker=dict(color = [
                '#1f77b4', # blue
                '#ff7f0e', # orange
                '#2ca02c', # green
                '#d62728', # red
                '#9467bd', # purple
                '#8c564b', # brown
                '#e377c2', # pink
                '#7f7f7f', # grey
                '#bcbd22', # olive
                '#17becf'  # teal
            ]), visible=False
        )
    )
    fig.update_layout(**fig4_layout())
    fig.update_yaxes(title_standoff=5)
    return fig

def fig5_layout(width=801):
    if width <= 800:
        font_size = 10
    else:
        font_size = 20
    return dict(
        title=f'<span style="font-size: {font_size}px;font-weight:bold;">Relative Share of Missed Slots per Relay<br><span style="font-size:{font_size-3}px;">(last 60 days)</span></span>',
        xaxis_title='%',
        yaxis_title='Relay',
        margin=dict(l=20, r=20, t=80, b=20),
        font=dict(family="Ubuntu Mono", size=font_size),
        xaxis=dict(
            fixedrange=True # Disables zooming/panning on the x-axis
        ),
        yaxis=dict(
            fixedrange=True # Disables zooming/panning on the y-axis
        ),
        updatemenus=[dict(
            type="buttons",
            buttons=[
                dict(args=[{"visible": [True,False]},
                           {"title": f'<span style="font-size: {font_size}px;font-weight:bold;">Relative Share of Missed Slots per Relay<br><span style="font-size:{font_size-3}px;">(last 60 days)</span></span>',
                            "xaxis.title": "%",
                           }],
                    label="Relative",
                    method="update"
                ),
                dict(args=[{"visible": [False,True]},
                           {"title": f'<span style="font-size: {font_size}px;font-weight:bold;">Absolute Nr. of Missed Slots per Relay<br><span style="font-size:{font_size-3}px;">(last 60 days)</span></span>',
                            "xaxis.title": "slots",
                           }],
                    label="Absolute",
                    method="update"
                )
            ],
            showactive=True,
            direction='left',
            active=0,
            x=1.0,
            xanchor='right',
            y=1.15,
            yanchor='top'
        )]
    )

def create_fig_for_relays(df_90, df, df_30, df_14, df_7, order):
    df = df[df["relay"] != "missed"]
    _df = df['relay'].value_counts().reset_index()
    _df = pd.merge(_df,order,how="left", left_on="relay", right_on="relay")
    _df["relay"]= _df["relay"].apply(lambda x: x[0].upper()+x[1:])
    _df.columns = ['relay', 'count', 'slots']
    _df["relative_count"] = round(_df['count'] / _df['slots'] * 100, 5)
    _df = _df[_df["count"] > 0]
    _df["relay"] = _df["relay"].apply(lambda x: x[0:9]+"..." if x.startswith("0x") else x)
    _df["relay"]= _df["relay"].apply(lambda x: x[0].upper()+x[1:])
    _df.sort_values("relative_count", ascending=False, inplace=True)
    _df = _df.iloc[0:11]
    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(
        go.Bar(x=_df['relative_count'], y=_df['relay'], orientation='h',
               marker=dict(color=[
                '#1f77b4', # blue
                '#ff7f0e', # orange
                '#2ca02c', # green
                '#d62728', # red
                '#9467bd', # purple
                '#8c564b', # brown
                '#e377c2', # pink
                '#7f7f7f', # grey
                '#bcbd22', # olive
                '#17becf'  # teal
            ])) # Add more colors if needed
    )

    fig.add_trace(
        go.Bar(
            x=_df['count'], y=_df['relay'], orientation='h',
            marker=dict(color = [
                '#1f77b4', # blue
                '#ff7f0e', # orange
                '#2ca02c', # green
                '#d62728', # red
                '#9467bd', # purple
                '#8c564b', # brown
                '#e377c2', # pink
                '#7f7f7f', # grey
                '#bcbd22', # olive
                '#17becf'  # teal
            ]), visible=False
        )
    )
    fig.update_layout(**fig5_layout())
    fig.update_yaxes(title_standoff=5)
    return fig






def create_reorger_builder_layout(width=801):
    if width <= 800:
        font_size = 10
    else:
        font_size = 20
    return dict(
        title=f'<span style="font-size: {font_size}px;font-weight:bold;">Relative Nr. of Slots by Reorging Builder<br><span style="font-size:{font_size-3}px;">(last 60 days)</span></span>',
        xaxis_title='%',
        yaxis_title='Builder',
        margin=dict(l=20, r=20, t=80, b=20),
        font=dict(family="Ubuntu Mono", size=font_size),
        xaxis=dict(
            fixedrange=True # Disables zooming/panning on the x-axis
        ),
        yaxis=dict(
            fixedrange=True # Disables zooming/panning on the y-axis
        ),
        paper_bgcolor= "#eee",
        updatemenus=[dict(
            type="buttons",
            buttons=[
                dict(args=[{"visible": [True,False]},
                           {"title": f'<span style="font-size: {font_size}px;font-weight:bold;">Relative Nr. of Slots by Reorging Builder<br><span style="font-size:{font_size-3}px;">(last 60 days)</span></span>',
                            "xaxis.title": "%",
                           }],
                    label="Relative",
                    method="update"
                ),
                dict(args=[{"visible": [False,True]},
                           {"title": f'<span style="font-size: {font_size}px;font-weight:bold;">Absolute Nr. of Slots by Reorging Builder<br><span style="font-size:{font_size-3}px;">(last 60 days)</span></span>',
                            "xaxis.title": "slots",
                           }],
                    label="Absolute",
                    method="update"
                )
            ],
            showactive=True,
            direction='left',
            active=0,
            x=1.0,
            xanchor='right',
            y=1.15,
            yanchor='top'
        )]
    )

def create_reorger_builder(df_90, df_60, df_30, df_14, df_7, order, df):
    df = df[df["builder"] != "missed"]
    _df = df['builder'].value_counts().reset_index()
    _df = pd.merge(_df,order,how="left", left_on="builder", right_on="builder")
    _df["builder"]= _df["builder"].apply(lambda x: x[0].upper()+x[1:])
    _df.columns = ['builder', 'count', 'slots']
    _df["relative_count"] = round(_df['count'] / _df['slots'] * 100, 5)
    _df = _df[_df["count"] > 0]
    _df["builder"] = _df["builder"].apply(lambda x: x[0:9]+"..." if x.startswith("0x") else x)
    _df["builder"]= _df["builder"].apply(lambda x: x[0].upper()+x[1:])
    _df.sort_values("relative_count", ascending=False, inplace=True)    
    _df = _df.iloc[0:12]
    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(
        go.Bar(x=_df['relative_count'], y=_df['builder'], orientation='h',
               marker=dict(color=[
                '#1f77b4', # blue
                '#ff7f0e', # orange
                '#2ca02c', # green
                '#d62728', # red
                '#9467bd', # purple
                '#8c564b', # brown
                '#e377c2', # pink
                '#7f7f7f', # grey
                '#bcbd22', # olive
                '#17becf'  # teal
            ])) # Add more colors if needed
    )

    fig.add_trace(
        go.Bar(
            x=_df['count'], y=_df['builder'], orientation='h',
            marker=dict(color = [
                '#1f77b4', # blue
                '#ff7f0e', # orange
                '#2ca02c', # green
                '#d62728', # red
                '#9467bd', # purple
                '#8c564b', # brown
                '#e377c2', # pink
                '#7f7f7f', # grey
                '#bcbd22', # olive
                '#17becf'  # teal
            ]), visible=False
        )
    )
    fig.update_layout(**create_reorger_builder_layout())
    fig.update_yaxes(title_standoff=5)
    return fig






def create_reorger_validator_layout(width=801):
    if width <= 800:
        font_size = 10
    else:
        font_size = 20
    return dict(
        title=f'<span style="font-size: {font_size}px;font-weight:bold;">Relative Nr. of Slots by Reorging Validator<br><span style="font-size:{font_size-3}px;">(last 60 days)</span></span>',
        xaxis_title='%',
        yaxis_title='Validator',
        margin=dict(l=20, r=20, t=80, b=20),
        font=dict(family="Ubuntu Mono", size=font_size),
        xaxis=dict(
            fixedrange=True # Disables zooming/panning on the x-axis
        ),
        yaxis=dict(
            fixedrange=True # Disables zooming/panning on the y-axis
        ),
        paper_bgcolor= "#eee",
        updatemenus=[dict(
            type = "buttons",
            direction = "left",

            buttons=[
                dict(args=[{"visible": [True,False]},
                           {"title": f'<span style="font-size: {font_size}px;font-weight:bold;">Relative Nr. of Slots by Reorging Validator<br><span style="font-size:{font_size-3}px;">(last 60 days)</span></span>',
                            "xaxis.title": "%",
                           }],
                    label="Relative",
                    method="update"
                ),
                dict(args=[{"visible": [False,True]},
                           {"title": f'<span style="font-size: {font_size}px;font-weight:bold;">Absolute Nr. of Slots by Reorging Builder<br><span style="font-size:{font_size-3}px;">(last 60 days)</span></span>',
                            "xaxis.title": "slots",
                           }],
                    label="Absolute",
                    method="update"
                )
            ],
            showactive=True,
            active=0,
            x=1.0,
            xanchor='right',
            y=1.15,
            yanchor='top'
        )]
    )

def create_reorger_validator(df_90, df_60, df_30, df_14, df_7, order, df):
    df = df[df["validator"] != "missed"]
    _df = df['validator'].value_counts().reset_index()
    _df = pd.merge(_df,order,how="left", left_on="validator", right_on="validator")
    _df["validator"]= _df["validator"].apply(lambda x: x[0].upper()+x[1:])
    _df.columns = ['validator', 'count', 'slots']
    _df["relative_count"] = round(_df['count'] / _df['slots'] * 100, 5)
    _df = _df[_df["count"] > 0]
    _df["validator"] = _df["validator"].apply(lambda x: x[0:9]+"..." if x.startswith("0x") else x)
    _df["validator"]= _df["validator"].apply(lambda x: x[0].upper()+x[1:])
    _df.sort_values("relative_count", ascending=False, inplace=True)    
    _df = _df.iloc[0:12]
    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(
        go.Bar(x=_df['relative_count'], y=_df['validator'], orientation='h',
               marker=dict(color=[
                '#1f77b4', # blue
                '#ff7f0e', # orange
                '#2ca02c', # green
                '#d62728', # red
                '#9467bd', # purple
                '#8c564b', # brown
                '#e377c2', # pink
                '#7f7f7f', # grey
                '#bcbd22', # olive
                '#17becf'  # teal
            ])) # Add more colors if needed
    )

    fig.add_trace(
        go.Bar(
            x=_df['count'], y=_df['validator'], orientation='h',
            marker=dict(color = [
                '#1f77b4', # blue
                '#ff7f0e', # orange
                '#2ca02c', # green
                '#d62728', # red
                '#9467bd', # purple
                '#8c564b', # brown
                '#e377c2', # pink
                '#7f7f7f', # grey
                '#bcbd22', # olive
                '#17becf'  # teal
            ]), visible=False
        )
    )
    fig.update_layout(**create_reorger_validator_layout())
    fig.update_yaxes(title_standoff=5)
    return fig






def create_reorger_relay_layout(width=801):
    if width <= 800:
        font_size = 10
    else:
        font_size = 20
    return dict(
        title=f'<span style="font-size: {font_size}px;font-weight:bold;">Relative Nr. of Slots by Reorging Relay<br><span style="font-size:{font_size-3}px;">(last 60 days)</span></span>',
        xaxis_title='%',
        yaxis_title='Relay',
        margin=dict(l=20, r=20, t=80, b=20),
        font=dict(family="Ubuntu Mono", size=font_size),
        xaxis=dict(
            fixedrange=True # Disables zooming/panning on the x-axis
        ),
        yaxis=dict(
            fixedrange=True # Disables zooming/panning on the y-axis
        ),
        paper_bgcolor= "#eee",
        updatemenus=[dict(
            type="buttons",
            buttons=[
                dict(args=[{"visible": [True,False]},
                           {"title": f'<span style="font-size: {font_size}px;font-weight:bold;">Relative Nr. of Slots by Reorging Relay<br><span style="font-size:{font_size-3}px;">(last 60 days)</span></span>',
                            "xaxis.title": "%",
                           }],
                    label="Relative",
                    method="update"
                ),
                dict(args=[{"visible": [False,True]},
                           {"title": f'<span style="font-size: {font_size}px;font-weight:bold;">Absolute Nr. of Slots by Reorging Relay<br><span style="font-size:{font_size-3}px;">(last 60 days)</span></span>',
                            "xaxis.title": "slots",
                           }],
                    label="Absolute",
                    method="update"
                )
            ],
            showactive=True,
            direction='left',
            active=0,
            x=1.0,
            xanchor='right',
            y=1.15,
            yanchor='top'
        )]
    )

def create_reorger_relay(df_90, df_60, df_30, df_14, df_7, order, df):
    df = df[df["relay"] != "missed"]
    _df = df['relay'].value_counts().reset_index()
    _df = pd.merge(_df,order,how="left", left_on="relay", right_on="relay")
    _df["relay"]= _df["relay"].apply(lambda x: x[0].upper()+x[1:])
    _df.columns = ['relay', 'count', 'slots']
    _df["relative_count"] = round(_df['count'] / _df['slots'] * 100, 5)
    _df = _df[_df["count"] > 0]
    _df["relay"] = _df["relay"].apply(lambda x: x[0:9]+"..." if x.startswith("0x") else x)
    _df["relay"]= _df["relay"].apply(lambda x: x[0].upper()+x[1:])
    _df.sort_values("relative_count", ascending=False, inplace=True)    
    _df = _df.iloc[0:11]
    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(
        go.Bar(x=_df['relative_count'], y=_df['relay'], orientation='h',
               marker=dict(color=[
                '#1f77b4', # blue
                '#ff7f0e', # orange
                '#2ca02c', # green
                '#d62728', # red
                '#9467bd', # purple
                '#8c564b', # brown
                '#e377c2', # pink
                '#7f7f7f', # grey
                '#bcbd22', # olive
                '#17becf'  # teal
            ])) # Add more colors if needed
    )

    fig.add_trace(
        go.Bar(
            x=_df['count'], y=_df['relay'], orientation='h',
            marker=dict(color = [
                '#1f77b4', # blue
                '#ff7f0e', # orange
                '#2ca02c', # green
                '#d62728', # red
                '#9467bd', # purple
                '#8c564b', # brown
                '#e377c2', # pink
                '#7f7f7f', # grey
                '#bcbd22', # olive
                '#17becf'  # teal
            ]), visible=False
        )
    )
    fig.update_layout(**create_reorger_relay_layout())
    fig.update_yaxes(title_standoff=5)
    return fig

def fig6_layout(width=801):
    if width <= 800:
        font_size = 10
    else:
        font_size = 20
    return dict(
        title=f'<span style="font-size: {font_size}px;font-weight:bold;">Relative Share of Missed Slots per Builder<br><span style="font-size:{font_size-3}px;">(last 60 days)</span></span>',
        xaxis_title='%',
        yaxis_title='Builder',
        margin=dict(l=20, r=20, t=80, b=20),
        font=dict(family="Ubuntu Mono", size=font_size),
        xaxis=dict(
            fixedrange=True # Disables zooming/panning on the x-axis
        ),
        yaxis=dict(
            fixedrange=True # Disables zooming/panning on the y-axis
        ),
        updatemenus=[dict(
            type="buttons",
            buttons=[
                dict(args=[{"visible": [True,False]},
                           {"title": f'<span style="font-size: {font_size}px;font-weight:bold;">Relative Share of Missed Slots per Builder<br><span style="font-size:{font_size-3}px;">(last 60 days)</span></span>',
                            "xaxis.title": "%",
                           }],
                    label="Relative",
                    method="update"
                ),
                dict(args=[{"visible": [False,True]},
                           {"title": f'<span style="font-size: {font_size}px;font-weight:bold;">Absolute Nr. of Missed Slots per Builder<br><span style="font-size:{font_size-3}px;">(last 60 days)</span></span>',
                            "xaxis.title": "slots",
                           }],
                    label="Absolute",
                    method="update"
                )
            ],
            showactive=True,
            direction='left',
            active=0,
            x=1.0,
            xanchor='right',
            y=1.15,
            yanchor='top'
        )]
    )


def create_fig_for_builders(df_90, df, df_30, df_14, df_7, order):
    df = df[df["builder"] != "missed"]
    _df = df['builder'].value_counts().reset_index()
    _df = pd.merge(_df,order,how="left", left_on="builder", right_on="builder")
    _df["builder"]= _df["builder"].apply(lambda x: x[0].upper()+x[1:])
    _df.columns = ['builder', 'count', 'slots']
    _df["relative_count"] = round(_df['count'] / _df['slots'] * 100, 5)
    _df = _df[_df["count"] > 0]
    _df["validator"] = _df["builder"].apply(lambda x: x[0:9]+"..." if x.startswith("0x") else x)
    _df.sort_values("relative_count", ascending=False, inplace=True)
    _df = _df.iloc[0:12]
    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(
        go.Bar(x=_df['relative_count'], y=_df['builder'], orientation='h',
               marker=dict(color = [
                '#1f77b4', # blue
                '#ff7f0e', # orange
                '#2ca02c', # green
                '#d62728', # red
                '#9467bd', # purple
                '#8c564b', # brown
                '#e377c2', # pink
                '#7f7f7f', # grey
                '#bcbd22', # olive
                '#17becf'  # teal
            ]) # Add more colors if needed
    ))

    fig.add_trace(
        go.Bar(
            x=_df['count'], y=_df['builder'], orientation='h',
            marker=dict(color = [
                '#1f77b4', # blue
                '#ff7f0e', # orange
                '#2ca02c', # green
                '#d62728', # red
                '#9467bd', # purple
                '#8c564b', # brown
                '#e377c2', # pink
                '#7f7f7f', # grey
                '#bcbd22', # olive
                '#17becf'  # teal
            ]), visible=False
        )
    )
    fig.update_layout(**fig6_layout())
    fig.update_yaxes(title_standoff=5)
    
    return fig

def fig7_layout(width=801):
    if width <= 800:
        font_size = 10
    else:
        font_size = 20
    return dict(
        title=f'<span style="font-size: {font_size}px;font-weight:bold;">Missed Slots over Time<br><span style="font-size:{font_size-3}px;">(last 30 days)</span></span>',
        xaxis_title='Date',
        yaxis_title='Slots',
        margin=dict(l=20, r=20, t=80, b=20),
        font=dict(family="Ubuntu Mono", size=font_size),
        barmode='stack',
        xaxis=dict(
            fixedrange=True # Disables zooming/panning on the x-axis
        ),
        yaxis=dict(
            fixedrange=True # Disables zooming/panning on the y-axis
        ),
        legend=dict(
            x=1,           # x position of the legend (1 corresponds to the right end of the plot)
            y=1,           # y position of the legend (1 corresponds to the top of the plot)
            xanchor="auto",  # x anchor of the legend
            yanchor="auto",  # y anchor of the legend
            bgcolor="rgba(255, 255, 255, 0.5)" # You can set a background color for readability if needed
        ),
        updatemenus=[dict(
            type="buttons",
            buttons=[
                dict(args=[{"visible": [True if i %2==0 else False for i in range(10)]},
                           {"title": f'<span style="font-size: {font_size}px;font-weight:bold;">Relative Share of Missed Slots per CL Client<br><span style="font-size:{font_size-3}px;">(last 30 days)</span></span>',
                            "xaxis.title": "%",
                           }],
                    label="Relative",
                    method="update"
                ),
                dict(args=[{"visible": [False if i %2==0 else True for i in range(10)]},
                           {"title": f'<span style="font-size: {font_size}px;font-weight:bold;">Absolute Nr. of Missed Slots per CL Client<br><span style="font-size:{font_size-3}px;">(last 30 days)</span></span>',
                            "xaxis.title": "slots",
                           }],
                    label="Absolute",
                    method="update"
                )
            ],
            showactive=True,
            direction='left',
            active=1,
            x=1.0,
            xanchor='right',
            y=1.15,
            yanchor='top'
        )]
    )

def create_fig_stacked(df_90, df_60, df, df_14, df_7, order):
    df = df[df["cl_client"] != "missed"]
    df.loc[:,"date"] = df["date"].apply(lambda x: x.split(" ")[0])
    _df = df.groupby(["date","cl_client"])["slot"].count().reset_index()

    _df = pd.merge(_df,order,how="left", left_on="cl_client", right_on="cl_client")
    _df["cl_client"]= _df["cl_client"].apply(lambda x: x[0].upper()+x[1:])
    _df.columns = ['date', 'cl_client', 'slot', 'slots']
    _df["relative_count"] = round(_df['slot'] / _df['slots'] * 100, 5)
    _df.sort_values("relative_count", ascending=False, inplace=True)

    fig = make_subplots(rows=1, cols=1)

    # Colors array (can be extended with more colors)
    colors = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ]

    # Add traces for each client
    for i, client in enumerate(_df["cl_client"].unique()):
        df = _df[_df["cl_client"] == client]
        fig.add_trace(go.Bar(x=df["date"], y=df["relative_count"], name=client, marker_color=colors[i], visible=False))
        fig.add_trace(go.Bar(x=df["date"], y=df["slot"], name=client, marker_color=colors[i]))
        
    fig.update_layout(**fig7_layout())
    
    fig.update_yaxes(title_standoff=5)
    return fig



# Figures
def create_figures(df_90, df_60, df_30, df_14, df_7, df_per_sie_60, df_per_sie_30, df_per_sie_14, df_per_sie_7, df2, df3, df4, df5, dfreorger):
    fig1 = create_fig1(df_90, df_60, df_30, df_14, df_7)
    fig2 = create_fig2(df_90, df_60, df_30, df_14, df_7, df5)
    fig3 = create_fig3(df_per_sie_60, df_per_sie_30, df_per_sie_14, df_per_sie_7)
    fig4 = create_fig_for_validators(df_90, df_60, df_30, df_14, df_7, df2)
    fig5 = create_fig_for_relays(df_90, df_60, df_30, df_14, df_7, df3)
    fig6 = create_fig_for_builders(df_90, df_60, df_30, df_14, df_7, df4)
    fig7 = create_fig_stacked(df_90, df_60, df_30, df_14, df_7, df5)
    fig8 = create_reorger_relay(df_90, df_60, df_30, df_14, df_7, df3, dfreorger)
    fig9 = create_reorger_validator(df_90, df_60, df_30, df_14, df_7, df2, dfreorger)
    fig10 = create_reorger_builder(df_90, df_60, df_30, df_14, df_7, df4, dfreorger)
    return fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10

df_90, df_60, df_30, df_14, df_7, df_table, df_per_sie_60, df_per_sie_30, df_per_sie_14, df_per_sie_7, df2, df3, df4, df5, dfreorger = prepare_data()
fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10 = create_figures(df_90, df_60, df_30, df_14, df_7, df_per_sie_60, df_per_sie_30, df_per_sie_14, df_per_sie_7, df2, df3, df4, df5, dfreorger)

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <meta name="twitter:card" content="summary_large_image">
        <meta name="twitter:site" content="@nero_ETH">
        <meta name="twitter:title" content="Ethereum Reorg Dashboard">
        <meta name="twitter:description" content="Selected comparative visualizations on reorged blocks on Ethereum.">
        <meta name="twitter:image" content="https://raw.githubusercontent.com/nerolation/reorg.pics/main/assets/reorg.png">
        <meta property="og:title" content="Reorg.pics" relay="" api="" dashboard="">
        <meta property="og:site_name" content="reorg.pics">
        <meta property="og:url" content="reorg.pics">
        <meta property="og:description" content="Selected comparative visualizations on reorged blocks on Ethereum.">
        <meta property="og:type" content="website">
        <link rel="shortcut icon" href="https://raw.githubusercontent.com/nerolation/reorg.pics/main/assets/reorg.png">
        <meta property="og:image" content="https://raw.githubusercontent.com/nerolation/reorg.pics/main/assets/reorg.png">
        <meta name="description" content="Selected comparative visualizations on reorged blocks on Ethereum.">
        <meta name="keywords" content="Ethereum, Reorg, Consensus, Dashboard">
        <meta name="author" content="Toni Wahrstätter">
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''
app.scripts.append_script({"external_url": "update_window_width.js"})
app.clientside_callback(
    "window.dash_clientside.update_window_size",
    Output('window-size-store', 'data'),
    Input('window-size-trigger', 'n_intervals')
)
app.title = 'Reorg.pics'
server = app.server

def table_styles(width):
    font_size = '20px' if width >= 800 else '10px'

    return [
        {'if': {'column_id': 'Slot Nr. in Epoch'}, 'maxWidth': '30px', 'text-align': 'center', 'fontSize': font_size},
        {'if': {'column_id': 'Slot'}, 'textAlign': 'right', 'maxWidth': '40px', 'fontSize': font_size},
        {'if': {'column_id': 'Val. ID'}, 'maxWidth': '30px', 'fontSize': font_size},
        {'if': {'column_id': 'Date'}, 'maxWidth': '80px', 'fontSize': font_size},
        {'if': {'column_id': 'CL Client'}, 'maxWidth': '80px', 'fontSize': font_size}
    ]

@app.callback(
    Output('main-div', 'style'),
    Input('window-size-store', 'data')
)
def update_main_div_style(window_size_data):
    if window_size_data is None:
        raise dash.exceptions.PreventUpdate

    window_width = window_size_data['width']
    if window_width > 800:
        return {'margin-right': '110px', 'margin-left': '110px'}
    else:
        return {}

app.layout = html.Div(
    [
        dbc.Container(
        [
            # Title
            dbc.Row(html.H1("Ethereum Reorg Dashboard", style={'text-align': 'center','margin-top': '20px'}), className="mb-4"),
            html.Div([
                dbc.Row([
                    dbc.Col(
                        html.H5(
                            ['Built with 🖤 by ', html.A('Toni Wahrstätter', href='https://twitter.com/nero_eth', target='_blank')],
                            className="mb-4 even-smaller-text" # Apply the class
                        ),
                        width={"size": 6, "order": 1}
                    ),
                    dbc.Col(
                        html.H5(
                            ['Built using ', html.A('blockprint', href='https://github.com/sigp/blockprint', target='_blank')],
                            className="mb-4 even-smaller-text text-right",
                            style={'textAlign': 'right'}
                        ),
                        width={"size": 6, "order": 2}
                    )
                ])
            ]),
            dbc.Row(
               html.H5(
                        ['Reorg Overview', ' (last 30 days)'],
                        className="mb-4 smaller-text" # Apply the class
                    )
            ),
            dbc.Row(
                dbc.Col(
                    dash_table.DataTable(
                        style_cell_conditional=table_styles(799),
                        id='table',
                        columns=[
                            {"name": i, 
                             "id": i, 
                             'presentation': 'markdown'} if i == 'Slot' else {"name": i, "id": i} for i in df_table.columns#[:-1]
                        ],# + [{"name": 'slot_sort', "id": 'slot_sort', "hidden": True}],
                        data=df_table.to_dict('records'),
                        page_size=20,
                        style_table={'overflowX': 'auto'},
                        style_cell={'whiteSpace': 'normal','height': 'auto'},
                        style_data_conditional=[
                            {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'},
                        ],
                        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                        style_header_conditional=[
                            {'if': {'column_id': 'Slot'}, 'text-align': 'center'},
                            {'if': {'column_id': 'Slot Nr. in Epoch'}, 'text-align': 'center'},
                        ],
                        css=[dict(selector="p", rule="margin: 0; text-align: center")],
                        sort_action="native",
                        sort_mode="multi"

                    ),
                    className="mb-4", md=12
                )
            ),

            # Graphs
            dbc.Row(dbc.Col(dcc.Graph(id='graph1', figure=fig1), md=12, className="mb-4")),
            dbc.Row(dbc.Col(dcc.Graph(id='graph7', figure=fig7), md=12, className="mb-4")),
            dbc.Row(dbc.Col(dcc.Graph(id='graph3', figure=fig3), md=12, className="mb-4")),
            dbc.Row(dbc.Col(dcc.Graph(id='graph2', figure=fig2), md=12, className="mb-4")),
            dbc.Row(dbc.Col(dcc.Graph(id='graph4', figure=fig4), md=12, className="mb-4")),
            dbc.Row(dbc.Col(dcc.Graph(id='graph5', figure=fig5), md=12, className="mb-4")),
            dbc.Row(dbc.Col(dcc.Graph(id='graph6', figure=fig6), md=12, className="mb-4")),
            dbc.Row(dbc.Col(dcc.Graph(id='graph8', figure=fig8), md=12, className="mb-4")),
            dbc.Row(dbc.Col(dcc.Graph(id='graph9', figure=fig9), md=12, className="mb-4")),
            dbc.Row(dbc.Col(dcc.Graph(id='graph10', figure=fig10), md=12, className="mb-4")),

            # Additional Components
            dbc.Row(dcc.Interval(id='window-size-trigger', interval=1000, n_intervals=0, max_intervals=1)),
            dcc.Store(id='window-size-store',data={'width': 800})
        ],
        fluid=True,
    )],
    id='main-div'  # This ID is used in the callback to update the style
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

@app.callback(
    Output('graph4', 'figure'),
    Input('window-size-store', 'data')
)
def update_layout4(window_size_data):
    if window_size_data is None:
        raise dash.exceptions.PreventUpdate
    width = window_size_data['width']
    fig4.update_layout(**fig4_layout(width))
    return fig4

@app.callback(
    Output('graph5', 'figure'),
    Input('window-size-store', 'data')
)
def update_layout5(window_size_data):
    if window_size_data is None:
        raise dash.exceptions.PreventUpdate
    width = window_size_data['width']
    fig5.update_layout(**fig5_layout(width))
    return fig5

@app.callback(
    Output('graph6', 'figure'),
    Input('window-size-store', 'data')
)
def update_layout6(window_size_data):
    if window_size_data is None:
        raise dash.exceptions.PreventUpdate
    width = window_size_data['width']
    fig6.update_layout(**fig6_layout(width))
    return fig6
@app.callback(
    Output('graph7', 'figure'),
    Input('window-size-store', 'data')
)
def update_layout7(window_size_data):
    if window_size_data is None:
        raise dash.exceptions.PreventUpdate
    width = window_size_data['width']
    fig7.update_layout(**fig7_layout(width))
    return fig7

@app.callback(
    Output('graph8', 'figure'),
    Input('window-size-store', 'data')
)
def update_layout8(window_size_data):
    if window_size_data is None:
        raise dash.exceptions.PreventUpdate
    width = window_size_data['width']
    fig8.update_layout(**create_reorger_relay_layout(width))
    return fig8

@app.callback(
    Output('graph9', 'figure'),
    Input('window-size-store', 'data')
)
def update_layout9(window_size_data):
    if window_size_data is None:
        raise dash.exceptions.PreventUpdate
    width = window_size_data['width']
    fig9.update_layout(**create_reorger_validator_layout(width))
    return fig9

@app.callback(
    Output('graph10', 'figure'),
    Input('window-size-store', 'data')
)
def update_layout10(window_size_data):
    if window_size_data is None:
        raise dash.exceptions.PreventUpdate
    width = window_size_data['width']
    fig10.update_layout(**create_reorger_builder_layout(width))
    return fig10

if __name__ == '__main__':
    #app.run_server(debug=True)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
