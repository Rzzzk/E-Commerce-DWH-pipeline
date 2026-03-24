from dash import Input, Output
import plotly.express as px
from layout import category_kpis # Import the dataframe already loaded in layout.py

def register_callbacks(app):
    """
    We wrap the callback in a function so we can pass the 'app' instance 
    to it from app.py without causing a circular import.
    """
    @app.callback(
        Output('dynamic-category-chart', 'figure'),
        Input('metric-selector', 'value')
    )
    def update_bar_chart(selected_metric):
        title_map = {
            'PROFIT_MARGIN_PCT': 'Profit Margin by Category (%)',
            'TOTAL_REVENUE': 'Total Revenue by Category ($)',
            'TOTAL_PROFIT': 'Total Profit by Category ($)'
        }
        
        fig = px.bar(
            category_kpis, 
            x='CATEGORY_NAME', 
            y=selected_metric,
            title=title_map[selected_metric],
            labels={'CATEGORY_NAME': 'Category', selected_metric: title_map[selected_metric]},
            color=selected_metric,
            color_continuous_scale='Viridis',
            template='plotly_white'
        )
        return fig