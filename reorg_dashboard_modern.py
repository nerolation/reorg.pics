#!/usr/bin/env python3
# Modern Reorg Dashboard Generator using PyXatu
# Generates a stylish HTML file with reorg analytics

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from pyxatu import PyXatu
import json

# Modern color palette
COLORS = {
    'primary': '#6366f1',      # Indigo
    'secondary': '#8b5cf6',    # Purple
    'tertiary': '#ec4899',     # Pink
    'quaternary': '#14b8a6',   # Teal
    'warning': '#f59e0b',      # Amber
    'danger': '#ef4444',       # Red
    'success': '#10b981',      # Emerald
    'info': '#3b82f6',         # Blue
    'dark': '#1e293b',         # Slate
    'light': '#f1f5f9'         # Light slate
}

# Gradient colors for charts
GRADIENT_COLORS = [
    '#6366f1', '#8b5cf6', '#a78bfa', '#c4b5fd', '#ddd6fe',
    '#ec4899', '#f472b6', '#f9a8d4', '#fbcfe8', '#fce7f3'
]

def slot_to_time(slot):
    """Convert slot number to datetime"""
    timestamp = 1606824023 + slot * 12
    return datetime.utcfromtimestamp(timestamp)

def get_current_slot():
    """Get approximate current slot based on time"""
    current_time = datetime.utcnow()
    genesis_time = datetime(2020, 12, 1, 12, 0, 23)
    seconds_since_genesis = (current_time - genesis_time).total_seconds()
    return int(seconds_since_genesis / 12)

def fetch_reorg_data_pyxatu(days_back=90):
    """Fetch reorg data using pyxatu"""
    print(f"Fetching reorg data for last {days_back} days...")
    
    current_slot = get_current_slot()
    slots_per_day = 7200
    start_slot = current_slot - (days_back * slots_per_day)
    
    with PyXatu() as xatu:
        # Query for reorgs - get all reports and we'll take minimum depth per slot
        reorg_query = f"""
        SELECT 
            slot - depth as slot,
            depth,
            slot as reorg_slot
        FROM beacon_api_eth_v1_events_chain_reorg
        WHERE slot BETWEEN {start_slot} AND {current_slot}
            AND meta_network_name = 'mainnet'
            AND meta_client_implementation != 'Contributoor'
        ORDER BY slot DESC
        """
        
        print("Querying reorgs...")
        reorgs_raw = xatu.raw_query(reorg_query)
        
        # Group by slot and take MINIMUM depth to avoid false positives
        print("Processing reorgs - taking minimum depth per slot...")
        reorgs_df = reorgs_raw.groupby('slot').agg({
            'depth': 'min',  # Take minimum depth to be conservative
            'reorg_slot': 'first'
        }).reset_index()
        
        # Get missed slots
        print("Getting missed slots...")
        missed_slots = xatu.get_missed_slots(slot_range=[start_slot, current_slot])
        
        # Filter reorgs to only those at missed slots
        reorgs_df = reorgs_df[reorgs_df["slot"].isin(missed_slots)]
        
        # Add additional data
        reorgs_df['date'] = reorgs_df['slot'].apply(slot_to_time)
        reorgs_df['slot_in_epoch'] = reorgs_df['slot'] % 32
        reorgs_df['epoch'] = reorgs_df['slot'] // 32
        
        print(f"Found {len(reorgs_raw)} raw reorg reports, consolidated to {len(reorgs_df)} unique slots with minimum depths")
        
    return reorgs_df

def create_time_series_chart(df, title="Reorgs Over Time", period_days=None):
    """Create beautiful time series chart of reorgs"""
    fig = go.Figure()
    
    if period_days:
        cutoff_date = datetime.utcnow() - timedelta(days=period_days)
        df = df[df['date'] >= cutoff_date]
    
    # Group by date
    df = df.copy()  # Create a copy to avoid SettingWithCopyWarning
    df['date_str'] = df['date'].dt.strftime('%Y-%m-%d')
    daily_counts = df.groupby('date_str').size().reset_index(name='count')
    
    # Add main trace with gradient fill
    fig.add_trace(go.Scatter(
        x=daily_counts['date_str'],
        y=daily_counts['count'],
        mode='lines+markers',
        name='Daily Reorgs',
        line=dict(
            color=COLORS['primary'],
            width=3,
            shape='spline'
        ),
        marker=dict(
            size=8,
            color=COLORS['primary'],
            line=dict(color='white', width=2)
        ),
        fill='tozeroy',
        fillcolor='rgba(99, 102, 241, 0.1)'
    ))
    
    # Add moving average
    if len(daily_counts) > 7:
        daily_counts['ma7'] = daily_counts['count'].rolling(window=7, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=daily_counts['date_str'],
            y=daily_counts['ma7'],
            mode='lines',
            name='7-day MA',
            line=dict(
                color=COLORS['secondary'],
                width=2,
                dash='dash'
            )
        ))
    
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=24, family='Ubuntu Mono', color=COLORS['dark'])
        ),
        xaxis=dict(
            title='Date',
            titlefont=dict(size=14, family='Ubuntu Mono'),
            tickfont=dict(size=12, family='Ubuntu Mono'),
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)',
            zeroline=False
        ),
        yaxis=dict(
            title='Number of Reorgs',
            titlefont=dict(size=14, family='Ubuntu Mono'),
            tickfont=dict(size=12, family='Ubuntu Mono'),
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)',
            zeroline=True,
            zerolinecolor='rgba(0,0,0,0.1)'
        ),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='white',
            font=dict(size=12, family='Ubuntu Mono'),
            bordercolor=COLORS['primary']
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500,
        margin=dict(l=60, r=30, t=80, b=60),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12, family='Ubuntu Mono')
        )
    )
    
    return fig

def create_slot_position_chart(df, title="Reorgs by Slot Position in Epoch"):
    """Create modern bar chart showing which slots in epoch get reorged most"""
    fig = go.Figure()
    
    # Group by slot position
    slot_counts = df['slot_in_epoch'].value_counts().sort_index()
    
    # Create gradient colors for bars
    colors = []
    for i in range(32):
        if i in slot_counts.index:
            intensity = slot_counts[i] / slot_counts.max()
            colors.append(f'rgba(99, 102, 241, {0.3 + intensity * 0.7})')
        else:
            colors.append('rgba(99, 102, 241, 0.3)')
    
    fig.add_trace(go.Bar(
        x=list(range(32)),
        y=[slot_counts.get(i, 0) for i in range(32)],
        marker=dict(
            color=colors,
            line=dict(color='rgba(99, 102, 241, 1)', width=1)
        ),
        text=[slot_counts.get(i, 0) for i in range(32)],
        textposition='outside',
        textfont=dict(size=10, family='Ubuntu Mono'),
        hovertemplate='<b>Slot %{x}</b><br>Reorgs: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=24, family='Ubuntu Mono', color=COLORS['dark'])
        ),
        xaxis=dict(
            title='Slot Position in Epoch (0-31)',
            titlefont=dict(size=14, family='Ubuntu Mono'),
            tickfont=dict(size=12, family='Ubuntu Mono'),
            tickmode='linear',
            tick0=0,
            dtick=1,
            showgrid=False
        ),
        yaxis=dict(
            title='Number of Reorgs',
            titlefont=dict(size=14, family='Ubuntu Mono'),
            tickfont=dict(size=12, family='Ubuntu Mono'),
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500,
        margin=dict(l=60, r=30, t=80, b=60),
        showlegend=False,
        hoverlabel=dict(
            bgcolor='white',
            font=dict(size=12, family='Ubuntu Mono'),
            bordercolor=COLORS['primary']
        )
    )
    
    return fig

def create_heatmap_chart(df, title="Reorg Activity Heatmap"):
    """Create beautiful heatmap of reorgs by hour and day"""
    df['hour'] = df['date'].dt.hour
    df['day_of_week'] = df['date'].dt.day_name()
    
    # Create pivot table
    pivot = df.pivot_table(
        values='slot',
        index='hour',
        columns='day_of_week',
        aggfunc='count',
        fill_value=0
    )
    
    # Reorder days
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot = pivot.reindex(columns=days_order, fill_value=0)
    
    # Custom colorscale
    colorscale = [
        [0, '#f1f5f9'],
        [0.2, '#ddd6fe'],
        [0.4, '#c4b5fd'],
        [0.6, '#a78bfa'],
        [0.8, '#8b5cf6'],
        [1.0, '#6366f1']
    ]
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale=colorscale,
        text=pivot.values,
        texttemplate='%{text}',
        textfont=dict(size=12, family='Ubuntu Mono'),
        hovertemplate='<b>%{x}</b><br>Hour: %{y}:00<br>Reorgs: %{z}<extra></extra>',
        colorbar=dict(
            title='Reorgs',
            titlefont=dict(size=12, family='Ubuntu Mono'),
            tickfont=dict(size=10, family='Ubuntu Mono'),
            thickness=15,
            len=0.7
        )
    ))
    
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=24, family='Ubuntu Mono', color=COLORS['dark'])
        ),
        xaxis=dict(
            title='Day of Week',
            titlefont=dict(size=14, family='Ubuntu Mono'),
            tickfont=dict(size=12, family='Ubuntu Mono'),
            side='bottom'
        ),
        yaxis=dict(
            title='Hour of Day (UTC)',
            titlefont=dict(size=14, family='Ubuntu Mono'),
            tickfont=dict(size=12, family='Ubuntu Mono'),
            tickmode='linear',
            tick0=0,
            dtick=1
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=600,
        margin=dict(l=60, r=80, t=80, b=60),
        hoverlabel=dict(
            bgcolor='white',
            font=dict(size=12, family='Ubuntu Mono'),
            bordercolor=COLORS['primary']
        )
    )
    
    return fig

def create_depth_distribution_chart(df, title="Reorg Depth Distribution"):
    """Create stylish chart showing distribution of reorg depths"""
    fig = go.Figure()
    
    depth_counts = df['depth'].value_counts().sort_index()
    
    # Different colors for different depths
    colors = [COLORS['success'] if d == 1 else COLORS['warning'] if d == 2 else COLORS['danger'] 
              for d in depth_counts.index]
    
    fig.add_trace(go.Bar(
        x=depth_counts.index,
        y=depth_counts.values,
        marker=dict(
            color=colors,
            line=dict(color='white', width=2)
        ),
        text=depth_counts.values,
        textposition='outside',
        textfont=dict(size=14, family='Ubuntu Mono', color=COLORS['dark']),
        hovertemplate='<b>Depth: %{x} blocks</b><br>Count: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=24, family='Ubuntu Mono', color=COLORS['dark'])
        ),
        xaxis=dict(
            title='Reorg Depth (blocks)',
            titlefont=dict(size=14, family='Ubuntu Mono'),
            tickfont=dict(size=12, family='Ubuntu Mono'),
            tickmode='linear',
            tick0=1,
            dtick=1,
            showgrid=False
        ),
        yaxis=dict(
            title='Count',
            titlefont=dict(size=14, family='Ubuntu Mono'),
            tickfont=dict(size=12, family='Ubuntu Mono'),
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        margin=dict(l=60, r=30, t=80, b=60),
        showlegend=False,
        hoverlabel=dict(
            bgcolor='white',
            font=dict(size=12, family='Ubuntu Mono'),
            bordercolor=COLORS['primary']
        )
    )
    
    return fig

def create_epoch_analysis_chart(df, title="Reorgs by Epoch"):
    """Create chart showing reorg distribution across epochs"""
    fig = go.Figure()
    
    # Group by epoch and get counts
    epoch_counts = df.groupby('epoch').size().reset_index(name='count')
    recent_epochs = epoch_counts.tail(100)  # Last 100 epochs
    
    fig.add_trace(go.Scatter(
        x=recent_epochs['epoch'],
        y=recent_epochs['count'],
        mode='lines+markers',
        line=dict(
            color=COLORS['tertiary'],
            width=2
        ),
        marker=dict(
            size=6,
            color=COLORS['tertiary'],
            line=dict(color='white', width=1)
        ),
        fill='tozeroy',
        fillcolor='rgba(236, 72, 153, 0.1)',
        hovertemplate='<b>Epoch %{x}</b><br>Reorgs: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b> (Last 100 Epochs)",
            font=dict(size=24, family='Ubuntu Mono', color=COLORS['dark'])
        ),
        xaxis=dict(
            title='Epoch Number',
            titlefont=dict(size=14, family='Ubuntu Mono'),
            tickfont=dict(size=12, family='Ubuntu Mono'),
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)'
        ),
        yaxis=dict(
            title='Number of Reorgs',
            titlefont=dict(size=14, family='Ubuntu Mono'),
            tickfont=dict(size=12, family='Ubuntu Mono'),
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        margin=dict(l=60, r=30, t=80, b=60),
        showlegend=False,
        hoverlabel=dict(
            bgcolor='white',
            font=dict(size=12, family='Ubuntu Mono'),
            bordercolor=COLORS['tertiary']
        )
    )
    
    return fig

def generate_modern_html_dashboard(charts, df, days_back=90, output_file="reorg_dashboard_modern.html"):
    """Generate a modern, stylish HTML file with all charts"""
    
    # Calculate statistics
    total_reorgs = len(df)
    avg_depth = df['depth'].mean() if 'depth' in df.columns else 1.0
    max_depth = df['depth'].max() if 'depth' in df.columns else 1
    today = datetime.utcnow().date()
    reorgs_today = len(df[df['date'].dt.date == today]) if not df.empty else 0
    reorgs_7d = len(df[df['date'] >= datetime.utcnow() - timedelta(days=7)])
    reorgs_30d = len(df[df['date'] >= datetime.utcnow() - timedelta(days=30)])
    
    # Determine period label
    if days_back >= 365:
        period_label = f"last {days_back // 365} year{'s' if days_back >= 730 else ''}"
    elif days_back >= 30:
        months = days_back // 30
        period_label = f"last {months} month{'s' if months > 1 else ''}"
    elif days_back >= 7:
        weeks = days_back // 7
        period_label = f"last {weeks} week{'s' if weeks > 1 else ''}"
    else:
        period_label = f"last {days_back} day{'s' if days_back > 1 else ''}"
    
    # Prepare table data (last 100 reorgs)
    df_table = df.sort_values('date', ascending=False).head(100).copy()
    df_table['date_str'] = df_table['date'].dt.strftime('%Y-%m-%d %H:%M:%S UTC')
    df_table['slot_link'] = df_table['slot'].apply(lambda x: f'<a href="https://beaconcha.in/slot/{x}" target="_blank">{x}</a>')
    df_table['epoch_link'] = df_table['epoch'].apply(lambda x: f'<a href="https://beaconcha.in/epoch/{x}" target="_blank">{x}</a>')
    
    table_rows = []
    for _, row in df_table.iterrows():
        depth_class = 'depth-normal' if row['depth'] == 1 else 'depth-warning' if row['depth'] == 2 else 'depth-danger'
        table_rows.append(f"""
            <tr>
                <td>{row['slot_link']}</td>
                <td>{row['epoch_link']}</td>
                <td class="{depth_class}">{row['depth']}</td>
                <td>{row['slot_in_epoch']}</td>
                <td>{row['date_str']}</td>
            </tr>
        """)
    
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reorg.pics</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Ubuntu+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Ubuntu Mono', monospace;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            position: relative;
        }}
        
        body::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23ffffff" fill-opacity="0.03"%3E%3Cpath d="M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E');
            pointer-events: none;
            z-index: 1;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 30px;
            position: relative;
            z-index: 2;
        }}
        
        .header {{
            text-align: center;
            padding: 50px 30px;
            background: rgba(255, 255, 255, 0.98);
            border-radius: 30px;
            margin-bottom: 40px;
            backdrop-filter: blur(10px);
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
            border: 1px solid rgba(255,255,255,0.5);
        }}
        
        h1 {{
            color: #1e293b;
            font-size: 3.5em;
            margin-bottom: 15px;
            font-weight: 700;
            letter-spacing: -1px;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .subtitle {{
            color: #64748b;
            font-size: 1.1em;
            letter-spacing: 1px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.98);
            border-radius: 20px;
            padding: 30px;
            text-align: center;
            backdrop-filter: blur(10px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.5);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: default;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}
        
        .stat-value {{
            font-size: 3em;
            font-weight: 700;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            line-height: 1;
        }}
        
        .stat-label {{
            color: #64748b;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 2px;
            font-weight: 400;
        }}
        
        .chart-container {{
            background: rgba(255, 255, 255, 0.98);
            border-radius: 25px;
            padding: 30px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.5);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        .chart-container:hover {{
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}
        
        .chart-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(700px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }}
        
        .footer {{
            text-align: center;
            padding: 40px;
            color: rgba(255,255,255,0.9);
            font-size: 0.95em;
            letter-spacing: 1px;
        }}
        
        .footer a {{
            color: white;
            text-decoration: none;
            font-weight: 700;
            border-bottom: 2px solid transparent;
            transition: border-color 0.3s;
        }}
        
        .footer a:hover {{
            border-bottom-color: white;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 15px;
            }}
            h1 {{
                font-size: 2em;
            }}
            .stat-value {{
                font-size: 2em;
            }}
            .chart-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        
        /* Loading animation */
        @keyframes pulse {{
            0%, 100% {{
                opacity: 1;
            }}
            50% {{
                opacity: 0.5;
            }}
        }}
        
        .loading {{
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }}
        
        /* Table styles */
        .table-container {{
            background: rgba(255, 255, 255, 0.98);
            border-radius: 25px;
            padding: 30px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.5);
            overflow-x: auto;
        }}
        
        .table-title {{
            font-size: 1.8em;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 20px;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            font-family: 'Ubuntu Mono', monospace;
        }}
        
        thead {{
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
        }}
        
        th {{
            padding: 15px;
            text-align: left;
            font-weight: 700;
            font-size: 14px;
            letter-spacing: 1px;
            text-transform: uppercase;
        }}
        
        th:first-child {{
            border-top-left-radius: 10px;
        }}
        
        th:last-child {{
            border-top-right-radius: 10px;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid rgba(0,0,0,0.05);
            font-size: 13px;
            color: #334155;
        }}
        
        tbody tr {{
            transition: all 0.2s;
        }}
        
        tbody tr:hover {{
            background: rgba(99, 102, 241, 0.05);
            transform: scale(1.01);
        }}
        
        td a {{
            color: #6366f1;
            text-decoration: none;
            font-weight: 700;
            transition: all 0.2s;
        }}
        
        td a:hover {{
            color: #8b5cf6;
            text-decoration: underline;
        }}
        
        .depth-normal {{
            color: #10b981;
            font-weight: 700;
        }}
        
        .depth-warning {{
            color: #f59e0b;
            font-weight: 700;
        }}
        
        .depth-danger {{
            color: #ef4444;
            font-weight: 700;
        }}
        
        .table-info {{
            margin-top: 15px;
            padding: 10px;
            background: rgba(99, 102, 241, 0.1);
            border-radius: 10px;
            font-size: 12px;
            color: #64748b;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Reorg.pics</h1>
            <div class="subtitle">
                Real-time blockchain reorganization monitoring | Powered by PyXatu
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{total_reorgs}</div>
                <div class="stat-label">Total Reorgs ({period_label})</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{reorgs_today}</div>
                <div class="stat-label">Today</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{reorgs_7d}</div>
                <div class="stat-label">Last 7 Days</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{reorgs_30d}</div>
                <div class="stat-label">Last 30 Days</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{avg_depth:.2f}</div>
                <div class="stat-label">Avg Depth ({period_label})</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{max_depth}</div>
                <div class="stat-label">Max Depth ({period_label})</div>
            </div>
        </div>
        
        {chart_divs}
        
        <div class="table-container">
            <div class="table-title">Recent Reorgs (Last 100)</div>
            <table>
                <thead>
                    <tr>
                        <th>Slot</th>
                        <th>Epoch</th>
                        <th>Depth</th>
                        <th>Position</th>
                        <th>Time (UTC)</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
            <div class="table-info">
                Click on slot or epoch numbers to view details on beaconcha.in
            </div>
        </div>
        
        <div class="footer">
            Built with 🖤 by <a href="https://twitter.com/nero_eth" target="_blank">Toni Wahrstätter</a> | 
            Generated {timestamp} | 
            Using <a href="https://github.com/nerolation/pyxatu" target="_blank">PyXatu</a> | 
            Data from <a href="https://ethpandaops.io" target="_blank">EthPandaOps</a>
        </div>
    </div>
    
    <script>
        // Set Plotly config
        const config = {{
            responsive: true,
            displayModeBar: false
        }};
        
        {chart_scripts}
    </script>
</body>
</html>"""
    
    # Generate chart HTML
    chart_divs = []
    chart_scripts = []
    
    chart_index = 0
    for name, fig in charts.items():
        div_id = f"chart_{chart_index}"
        chart_divs.append(f'<div class="chart-container" id="{div_id}"></div>')
        
        # Convert figure to JSON
        fig_json = fig.to_json()
        
        # Create script to render the chart
        script = f"""
        (function() {{
            var figure_{chart_index} = {fig_json};
            Plotly.newPlot('{div_id}', figure_{chart_index}.data, figure_{chart_index}.layout, config);
        }})();
        """
        chart_scripts.append(script)
        chart_index += 1
    
    # Fill template
    html = html_template.format(
        total_reorgs=total_reorgs,
        reorgs_today=reorgs_today,
        reorgs_7d=reorgs_7d,
        reorgs_30d=reorgs_30d,
        avg_depth=avg_depth,
        max_depth=max_depth,
        period_label=period_label,
        timestamp=datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
        chart_divs='\n'.join(chart_divs),
        table_rows=''.join(table_rows),
        chart_scripts='\n'.join(chart_scripts)
    )
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Modern dashboard generated: {output_file}")

def main():
    """Main function to generate the modern dashboard"""
    print("Starting Modern Reorg Dashboard generation...")
    
    # Configuration - fetch last year of data
    days_back = 365
    
    # Fetch data
    df = fetch_reorg_data_pyxatu(days_back=days_back)
    
    if df.empty:
        print("No reorg data found!")
        return
    
    print(f"Found {len(df)} reorgs")
    
    # Create charts with appropriate titles
    period_label = "Year" if days_back >= 365 else f"{days_back}-Day"
    charts = {
        'time_series_year': create_time_series_chart(df, f"{period_label} Reorg Trend"),
        'time_series_90d': create_time_series_chart(df, "90-Day Reorg Trend", period_days=90),
        'time_series_30d': create_time_series_chart(df, "30-Day Reorg Trend", period_days=30),
        'time_series_7d': create_time_series_chart(df, "7-Day Reorg Trend", period_days=7),
        'slot_position': create_slot_position_chart(df),
        'heatmap': create_heatmap_chart(df),
        'depth_distribution': create_depth_distribution_chart(df),
        'epoch_analysis': create_epoch_analysis_chart(df)
    }
    
    # Generate HTML
    generate_modern_html_dashboard(charts, df, days_back, "reorg_dashboard_modern.html")
    
    print("Modern dashboard generation complete!")

if __name__ == "__main__":
    main()