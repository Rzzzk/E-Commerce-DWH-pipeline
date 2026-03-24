import os
import pandas as pd
import plotly.express as px
from dash import dcc, html

# ==========================================
# 1. Load the Data Marts
# ==========================================
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data')

try:
    overall_kpis = pd.read_csv(f"{DATA_DIR}/overall_kpis.csv").iloc[0]
    daily_kpis = pd.read_csv(f"{DATA_DIR}/daily_kpis.csv")
    category_kpis = pd.read_csv(f"{DATA_DIR}/category_kpis.csv")
except FileNotFoundError:
    print("Error: Data Mart CSVs not found. Please run the ETL script first.")
    exit()

# ==========================================
# 2. Create Static Figure (Daily Trend)
# ==========================================
fig_daily = px.line(
    daily_kpis, x='FULL_DATE', y='DAILY_REVENUE',
    title='Daily Revenue Trend',
    labels={'FULL_DATE': 'Date', 'DAILY_REVENUE': 'Revenue ($)'},
    markers=True, template='plotly_white'
)
fig_daily.update_traces(line_color='#2980B9')

# ==========================================
# 3. Define the Dashboard Layout
# ==========================================
layout = html.Div(style={'fontFamily': 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif', 'padding': '30px', 'backgroundColor': '#F8F9F9', 'minHeight': '100vh'}, children=[
    
    html.H1("E-Commerce Analytical Dashboard", style={'textAlign': 'center', 'color': '#2C3E50', 'marginBottom': '30px'}),

    # KPI Summary Cards
    html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '40px'}, children=[
        html.Div(style={'padding': '20px', 'backgroundColor': '#FFFFFF', 'borderRadius': '8px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'textAlign': 'center', 'width': '18%'}, children=[
            html.H4("Total Revenue", style={'margin': '0', 'color': '#7F8C8D', 'fontWeight': 'normal'}),
            html.H2(f"${overall_kpis['Total_Revenue']:,.2f}", style={'margin': '10px 0 0 0', 'color': '#27AE60'})
        ]),
        html.Div(style={'padding': '20px', 'backgroundColor': '#FFFFFF', 'borderRadius': '8px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'textAlign': 'center', 'width': '18%'}, children=[
            html.H4("Gross Profit", style={'margin': '0', 'color': '#7F8C8D', 'fontWeight': 'normal'}),
            html.H2(f"${overall_kpis['Gross_Profit']:,.2f}", style={'margin': '10px 0 0 0', 'color': '#2980B9'})
        ]),
        html.Div(style={'padding': '20px', 'backgroundColor': '#FFFFFF', 'borderRadius': '8px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'textAlign': 'center', 'width': '18%'}, children=[
            html.H4("Profit Margin", style={'margin': '0', 'color': '#7F8C8D', 'fontWeight': 'normal'}),
            html.H2(f"{overall_kpis['Profit_Margin_Pct']}%", style={'margin': '10px 0 0 0', 'color': '#8E44AD'})
        ]),
        html.Div(style={'padding': '20px', 'backgroundColor': '#FFFFFF', 'borderRadius': '8px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'textAlign': 'center', 'width': '18%'}, children=[
            html.H4("Avg Order Value", style={'margin': '0', 'color': '#7F8C8D', 'fontWeight': 'normal'}),
            html.H2(f"${overall_kpis['AOV']:,.2f}", style={'margin': '10px 0 0 0', 'color': '#F39C12'})
        ]),
        html.Div(style={'padding': '20px', 'backgroundColor': '#FFFFFF', 'borderRadius': '8px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'textAlign': 'center', 'width': '18%'}, children=[
            html.H4("Repeat Purchase Rate", style={'margin': '0', 'color': '#7F8C8D', 'fontWeight': 'normal'}),
            html.H2(f"{overall_kpis['Repeat_Purchase_Rate_Pct']}%", style={'margin': '10px 0 0 0', 'color': '#C0392B'})
        ])
    ]),

    # Charts Section
    html.Div(style={'display': 'flex', 'justifyContent': 'space-between'}, children=[
        html.Div(dcc.Graph(figure=fig_daily), style={'width': '48%', 'backgroundColor': '#FFFFFF', 'padding': '10px', 'borderRadius': '8px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'}),
        
        html.Div(style={'width': '48%', 'backgroundColor': '#FFFFFF', 'padding': '20px', 'borderRadius': '8px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'}, children=[
            html.Label("Select Category Metric to Display:", style={'fontWeight': 'bold', 'color': '#2C3E50'}),
            dcc.Dropdown(
                id='metric-selector',
                options=[
                    {'label': 'Profit Margin (%)', 'value': 'PROFIT_MARGIN_PCT'},
                    {'label': 'Total Revenue ($)', 'value': 'TOTAL_REVENUE'},
                    {'label': 'Total Profit ($)', 'value': 'TOTAL_PROFIT'}
                ],
                value='PROFIT_MARGIN_PCT',
                clearable=False,
                style={'marginBottom': '10px', 'marginTop': '10px'}
            ),
            dcc.Graph(id='dynamic-category-chart')
        ])
    ])
])