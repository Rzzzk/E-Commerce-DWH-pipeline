import dash
from layout import layout
from callbacks import register_callbacks

# 1. Initialize the App
app = dash.Dash(__name__, title="E-Commerce DWH")

# 2. Assign the layout from layout.py
app.layout = layout

# 3. Register the interactive logic from callbacks.py
register_callbacks(app)

# 4. Run the Server
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)