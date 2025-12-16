import dash
from dash import dcc, html, Input, Output
import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize AWS S3 client using default credential chain
# On EC2, this will automatically use the IAM role credentials
aws_region = os.getenv('AWS_REGION', 'eu-north-1') #hello
s3_bucket_name = os.getenv('S3_BUCKET_NAME')

# Debug: Print what we loaded (remove in production)
print(f"DEBUG: AWS_REGION = {aws_region}")
print(f"DEBUG: S3_BUCKET_NAME = {s3_bucket_name}")

# Initialize S3 client using default credential chain
# This automatically uses:
# - IAM role credentials (when running on EC2/Lambda)
# - Environment variables (if set)
# - ~/.aws/credentials (for local development)
s3_client = None
try:
    s3_client = boto3.client('s3', region_name=aws_region)
    print("DEBUG: S3 client created successfully")
    
    # Test connection by checking if bucket exists
    if s3_bucket_name:
        try:
            s3_client.head_bucket(Bucket=s3_bucket_name)
            print(f"DEBUG: Successfully connected to bucket '{s3_bucket_name}'")
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == '404':
                print(f"ERROR: Bucket '{s3_bucket_name}' not found")
            elif error_code == '403':
                print(f"ERROR: Access denied to bucket '{s3_bucket_name}'. Check IAM role permissions.")
            else:
                print(f"ERROR: {e}")
            # Don't set s3_client to None here - the client works, just bucket access issue
    else:
        print("WARNING: S3_BUCKET_NAME not set in .env file")
except Exception as e:
    print(f"ERROR: Failed to initialize S3 client: {e}")
    print(f"ERROR: Exception type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    s3_client = None

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
                       'backgroundColor': '#050505', 'borderRadius': '5px',
                       'marginTop': '10px', 'fontSize': '16px', 'whiteSpace': 'pre-wrap'})
    ], style={'width': '80%', 'margin': '0 auto', 'marginTop': '30px'}),
    
    html.Div([
        html.H3("S3 Bucket Images:", style={'fontSize': '18px', 'marginTop': '30px'}),
        html.Div(id='s3-images', 
                style={'width': '100%', 'padding': '15px',
                       'backgroundColor': '#050505', 'borderRadius': '5px',
                       'marginTop': '10px'})
    ], style={'width': '80%', 'margin': '0 auto', 'marginTop': '30px'})
], style={'fontFamily': 'Arial, sans-serif', 'maxWidth': '800px', 'margin': '0 auto', 'padding': '20px'})

# Function to get image URLs from S3 bucket
def get_s3_images():
    """Retrieve image URLs from S3 bucket"""
    if not s3_client or not s3_bucket_name:
        return []
    
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
    image_urls = []
    
    try:
        # List objects in the bucket
        response = s3_client.list_objects_v2(Bucket=s3_bucket_name)
        
        if 'Contents' in response:
            for obj in response['Contents']:
                key = obj['Key']
                # Check if the object is an image
                if any(key.lower().endswith(ext) for ext in image_extensions):
                    # Generate presigned URL (valid for 1 hour)
                    try:
                        url = s3_client.generate_presigned_url(
                            'get_object',
                            Params={'Bucket': s3_bucket_name, 'Key': key},
                            ExpiresIn=3600
                        )
                        image_urls.append({'url': url, 'key': key})
                    except ClientError as e:
                        print(f"Error generating presigned URL for {key}: {e}")
    except ClientError as e:
        print(f"Error accessing S3 bucket: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []
    
    return image_urls

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

# Define the callback to display S3 images
@app.callback(
    Output('s3-images', 'children'),
    Input('process-button', 'n_clicks')
)
def display_s3_images(n_clicks):
    """Display images from S3 bucket"""
    images = get_s3_images()
    
    if not images:
        if not s3_client or not s3_bucket_name:
            return html.Div("Please configure S3_BUCKET_NAME in .env file. Ensure EC2 instance has IAM role with S3 permissions.",
                          style={'color': '#666', 'fontSize': '14px', 'padding': '10px'})
        return html.Div("No images found in the S3 bucket.",
                      style={'color': '#666', 'fontSize': '14px', 'padding': '10px'})
    
    # Create image gallery
    image_elements = []
    for img in images:
        image_elements.append(
            html.Div([
                html.Img(
                    src=img['url'],
                    style={
                        'width': '100%',
                        'maxWidth': '300px',
                        'height': 'auto',
                        'margin': '10px',
                        'borderRadius': '5px',
                        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                    }
                ),
                html.P(img['key'], style={'fontSize': '12px', 'color': '#666', 'marginTop': '5px', 'textAlign': 'center'})
            ], style={'display': 'inline-block', 'verticalAlign': 'top', 'margin': '10px'})
        )
    
    return html.Div(image_elements, style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center'})

# Run the app
if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8050)

