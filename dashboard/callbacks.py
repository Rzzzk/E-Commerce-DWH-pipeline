from dash import Input, Output
import plotly.express as px
from layout import category_kpis

def register_callbacks(app):
    """
    Registers all dashboard callbacks to handle user interactions.
    Wrapped in a function to avoid circular imports.
    """
    @app.callback(
        Output('dynamic-category-chart', 'figure'),
        Input('metric-selector', 'value')
    )
    def update_bar_chart(selected_metric):
        # 1. Configuration dictionary for dynamic formatting
        metric_config = {
            'PROFIT_MARGIN_PCT': {'title': 'Profit Margin by Category', 'format': '.2f', 'prefix': '', 'suffix': '%'},
            'TOTAL_REVENUE': {'title': 'Total Revenue by Category', 'format': ',.2f', 'prefix': '$', 'suffix': ''},
            'TOTAL_PROFIT': {'title': 'Total Profit by Category', 'format': ',.2f', 'prefix': '$', 'suffix': ''}
        }
        
        # Fallback to Profit Margin if something goes wrong
        config = metric_config.get(selected_metric, metric_config['PROFIT_MARGIN_PCT'])
        
        # 2. Sort data so the highest performing category is always on the left
        sorted_df = category_kpis.sort_values(by=selected_metric, ascending=False)
        
        # 3. Generate the base figure
        fig = px.bar(
            sorted_df, 
            x='CATEGORY_NAME', 
            y=selected_metric,
            title=config['title'],
            color=selected_metric,
            color_continuous_scale='Teal', # A more professional corporate color scale
            template='plotly_white',
            text=selected_metric # Adds the actual number to the top of the bar
        )
        
        # 4. Polish the Aesthetics & UX
        fig.update_traces(
            # Format the text on top of the bars dynamically ($ vs %)
            texttemplate=f"{config['prefix']}%{{text:{config['format']}}}{config['suffix']}",
            textposition='outside',
            # Clean up the tooltip that appears when a user hovers over a bar
            hovertemplate=f"<b>%{{x}}</b><br>{config['title']}: {config['prefix']}%{{y:{config['format']}}}{config['suffix']}<extra></extra>"
        )
        
        fig.update_layout(
            xaxis_title=None,          # Removes redundant 'Category' label
            yaxis_title=None,          # Removes redundant Y-axis label (title already explains it)
            coloraxis_showscale=False, # Hides the redundant color legend on the right
            margin=dict(l=20, r=20, t=50, b=20), # Tightens up the blank space around the chart
            hoverlabel=dict(bgcolor="white", font_size=14, font_family="Segoe UI")
        )
        
        # Ensure the Y-axis has enough room for the text labels sitting on top of the bars
        fig.update_yaxes(autorange="reversed" if selected_metric == 'none' else True, rangemode="tozero", title_text='')
        # Add 15% padding to the top of the y-axis so the text labels don't get cut off
        fig.layout.yaxis.range = [0, sorted_df[selected_metric].max() * 1.15]

        return fig