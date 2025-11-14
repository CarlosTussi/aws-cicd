import dash
from dash import dcc, html, Input, Output

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div([
    html.H1("Simple Text Processor", style={'textAlign': 'center', 'marginTop': '50px'}),
    
    html.Div([
        html.Label("Enter text:", style={'fontSize': '18px', 'marginBottom': '10px'}),
        dcc.Textarea(
            id='input-text',
            placeholder='Type your text here...',
            style={'width': '100%', 'height': '150px', 'fontSize': '16px', 'padding': '10px'}
        ),
    ], style={'width': '80%', 'margin': '0 auto', 'marginTop': '30px'}),
    
    html.Div([
        html.Button('Process', id='process-button', n_clicks=0,
                   style={'fontSize': '18px', 'padding': '10px 30px', 'marginTop': '20px',
                          'backgroundColor': '#4CAF50', 'color': 'white', 'border': 'none',
                          'borderRadius': '5px', 'cursor': 'pointer'})
    ], style={'textAlign': 'center', 'marginTop': '20px'}),
    
    html.Div([
        html.H3("Processed Text:", style={'fontSize': '18px', 'marginTop': '30px'}),
        html.Div(id='output-text', 
                style={'width': '100%', 'minHeight': '100px', 'padding': '15px',
                       'backgroundColor': '#f0f0f0', 'borderRadius': '5px',
                       'marginTop': '10px', 'fontSize': '16px', 'whiteSpace': 'pre-wrap'})
    ], style={'width': '80%', 'margin': '0 auto', 'marginTop': '30px'})
], style={'fontFamily': 'Arial, sans-serif', 'maxWidth': '800px', 'margin': '0 auto', 'padding': '20px'})

# Define the callback to process the text
@app.callback(
    Output('output-text', 'children'),
    Input('process-button', 'n_clicks'),
    Input('input-text', 'value')
)
def process_text(n_clicks, input_value):
    if n_clicks > 0 and input_value:
        # Process the text: replace 'a' with '@', 'i' with '!', 'e' with '&'
        processed = input_value.replace('a', '@').replace('i', '!').replace('e', '&')
        return processed
    return ""

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)

