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
    clv_df = pd.read_csv(f"{DATA_DIR}/customer_clv.csv")
    growth_df = pd.read_csv(f"{DATA_DIR}/monthly_growth.csv")
except FileNotFoundError as e:
    print(f"Error: Data Mart CSVs not found. Please run the ETL script first. Details: {e}")
    exit()

# ==========================================
# 2. Create Static Figures
# ==========================================
# A. Daily Revenue
fig_daily = px.line(daily_kpis, x='FULL_DATE', y='DAILY_REVENUE', markers=True, template='plotly_white')
fig_daily.update_traces(line_color='#2980B9', line_width=3, marker=dict(size=6))
fig_daily.update_layout(xaxis_title="", yaxis_title="Revenue ($)", margin=dict(l=0, r=0, t=20, b=0), height=320)

# B. MoM Growth
growth_df['PERIOD'] = growth_df['MONTH_NAME'] + " " + growth_df['YEAR'].astype(str)
fig_growth = px.bar(growth_df, x='PERIOD', y='MOM_GROWTH_PCT', text='MOM_GROWTH_PCT', template='plotly_white', color='MOM_GROWTH_PCT', color_continuous_scale='RdYlGn')
fig_growth.update_traces(texttemplate='%{text}%', textposition='outside')
fig_growth.update_layout(xaxis_title="", yaxis_title="Growth (%)", coloraxis_showscale=False, margin=dict(l=0, r=0, t=20, b=0), height=320)

# C. Top 10 CLV
top_10_clv = clv_df.head(10).copy()
top_10_clv['CUSTOMER_KEY'] = 'Customer ' + top_10_clv['CUSTOMER_KEY'].astype(str)
fig_clv = px.bar(top_10_clv, x='CLV', y='CUSTOMER_KEY', orientation='h', text='CLV', template='plotly_white', color='CLV', color_continuous_scale='Blues')
fig_clv.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
fig_clv.update_layout(yaxis={'categoryorder':'total ascending'}, xaxis_title="", yaxis_title="", coloraxis_showscale=False, margin=dict(l=0, r=0, t=20, b=0), height=320)


# ==========================================
# 3. CSS Style Dictionary (Upgraded for Grid)
# ==========================================
APP_BG = '#F0F2F5'

# Notice we removed 'width', 'flex', and 'margin' because CSS Grid handles all spacing automatically
kpi_card = {
    'backgroundColor': '#FFFFFF', 'borderRadius': '8px', 'padding': '20px', 
    'boxShadow': '0 2px 4px rgba(0,0,0,0.08)',
    'borderTop': '4px solid #2C3E50'
}

chart_card = {
    'backgroundColor': '#FFFFFF', 'borderRadius': '8px', 'padding': '25px',
    'boxShadow': '0 2px 4px rgba(0,0,0,0.08)',
    'display': 'flex', 'flexDirection': 'column' # Ensures the chart pushes to the bottom of the card
}

section_title = {
    'color': '#34495E', 'marginTop': '40px', 'marginBottom': '20px', 
    'fontWeight': '600', 'borderBottom': '2px solid #D5D8DC', 'paddingBottom': '10px'
}

# ==========================================
# 4. Define the Dashboard Layout
# ==========================================
layout = html.Div(style={'fontFamily': 'Segoe UI, Roboto, Helvetica, Arial, sans-serif', 'backgroundColor': APP_BG, 'minHeight': '100vh'}, children=[
    
    # HEADER
    html.Div(style={'backgroundColor': '#1A252F', 'padding': '20px 40px', 'boxShadow': '0 2px 10px rgba(0,0,0,0.2)'}, children=[
        html.H2("TechHub Electronics", style={'color': '#FFFFFF', 'margin': '0', 'display': 'inline-block', 'fontWeight': '600'}),
        html.Span("Executive BI Dashboard", style={'color': '#BDC3C7', 'marginLeft': '20px', 'fontSize': '18px', 'borderLeft': '1px solid #7F8C8D', 'paddingLeft': '20px'})
    ]),

    # MAIN CONTENT BODY
    html.Div(style={'padding': '30px 40px', 'maxWidth': '1800px', 'margin': '0 auto'}, children=[
        
        # --- EXECUTIVE SUMMARY KPIS (Using 5-Column Grid) ---
        html.Div(style={'display': 'grid', 'gridTemplateColumns': 'repeat(5, 1fr)', 'gap': '20px', 'marginTop': '10px'}, children=[
            html.Div(style=dict(kpi_card, borderTop='4px solid #27AE60'), children=[
                html.P("Total Revenue", style={'margin': '0', 'color': '#7F8C8D', 'textTransform': 'uppercase', 'fontSize': '12px', 'fontWeight': 'bold'}),
                html.H2(f"${overall_kpis['Total_Revenue']:,.0f}", style={'margin': '5px 0 0 0', 'color': '#2C3E50'})
            ]),
            html.Div(style=dict(kpi_card, borderTop='4px solid #2980B9'), children=[
                html.P("Gross Profit", style={'margin': '0', 'color': '#7F8C8D', 'textTransform': 'uppercase', 'fontSize': '12px', 'fontWeight': 'bold'}),
                html.H2(f"${overall_kpis['Gross_Profit']:,.0f}", style={'margin': '5px 0 0 0', 'color': '#2C3E50'})
            ]),
            html.Div(style=dict(kpi_card, borderTop='4px solid #8E44AD'), children=[
                html.P("Profit Margin", style={'margin': '0', 'color': '#7F8C8D', 'textTransform': 'uppercase', 'fontSize': '12px', 'fontWeight': 'bold'}),
                html.H2(f"{overall_kpis['Profit_Margin_Pct']}%", style={'margin': '5px 0 0 0', 'color': '#2C3E50'})
            ]),
            html.Div(style=dict(kpi_card, borderTop='4px solid #F39C12'), children=[
                html.P("Avg Order Value", style={'margin': '0', 'color': '#7F8C8D', 'textTransform': 'uppercase', 'fontSize': '12px', 'fontWeight': 'bold'}),
                html.H2(f"${overall_kpis['AOV']:,.2f}", style={'margin': '5px 0 0 0', 'color': '#2C3E50'})
            ]),
            html.Div(style=dict(kpi_card, borderTop='4px solid #E74C3C'), children=[
                html.P("Repeat Purchase Rate", style={'margin': '0', 'color': '#7F8C8D', 'textTransform': 'uppercase', 'fontSize': '12px', 'fontWeight': 'bold'}),
                html.H2(f"{overall_kpis['Repeat_Purchase_Rate_Pct']}%", style={'margin': '5px 0 0 0', 'color': '#2C3E50'})
            ])
        ]),

        # --- SECTION 1: SALES & PRODUCT PERFORMANCE (Using 2-Column Grid) ---
        html.H3("📈 Sales & Product Performance", style=section_title),
        html.Div(style={'display': 'grid', 'gridTemplateColumns': 'repeat(2, 1fr)', 'gap': '30px'}, children=[
            
            # Left Chart: Daily Trend
            html.Div(style=chart_card, children=[
                html.H4("Daily Revenue Trend", style={'margin': '0 0 15px 0', 'color': '#2C3E50'}),
                dcc.Graph(figure=fig_daily, config={'displayModeBar': False}, style={'flexGrow': '1'})
            ]),
            
            # Right Chart: Interactive Category
            html.Div(style=chart_card, children=[
                html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'marginBottom': '15px'}, children=[
                    html.H4("Category Breakdown", style={'margin': '0', 'color': '#2C3E50'}),
                    dcc.Dropdown(
                        id='metric-selector',
                        options=[
                            {'label': 'Profit Margin (%)', 'value': 'PROFIT_MARGIN_PCT'},
                            {'label': 'Total Revenue ($)', 'value': 'TOTAL_REVENUE'},
                            {'label': 'Total Profit ($)', 'value': 'TOTAL_PROFIT'}
                        ],
                        value='TOTAL_REVENUE',
                        clearable=False,
                        style={'width': '220px', 'fontSize': '14px'}
                    )
                ]),
                dcc.Graph(id='dynamic-category-chart', config={'displayModeBar': False}, style={'flexGrow': '1'})
            ])
        ]),

        # --- SECTION 2: CUSTOMER & GROWTH ANALYTICS (Using 2-Column Grid) ---
        html.H3("👥 Customer & Growth Analytics", style=section_title),
        html.Div(style={'display': 'grid', 'gridTemplateColumns': 'repeat(2, 1fr)', 'gap': '30px'}, children=[
            
            # Left Chart: MoM Growth
            html.Div(style=chart_card, children=[
                html.H4("Month-over-Month Growth", style={'margin': '0 0 15px 0', 'color': '#2C3E50'}),
                dcc.Graph(figure=fig_growth, config={'displayModeBar': False}, style={'flexGrow': '1'})
            ]),
            
            # Right Chart: CLV
            html.Div(style=chart_card, children=[
                html.H4("Top Customers by Lifetime Value", style={'margin': '0 0 15px 0', 'color': '#2C3E50'}),
                dcc.Graph(figure=fig_clv, config={'displayModeBar': False}, style={'flexGrow': '1'})
            ])
        ])
    ])
])