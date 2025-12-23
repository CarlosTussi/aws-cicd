import dash
from dash import dcc, html, Input, Output
import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AWS configuration (unchanged)
aws_region = os.getenv('AWS_REGION', 'eu-north-1')
s3_bucket_name = os.getenv('S3_BUCKET_NAME')

# Debug prints (unchanged)
print(f"DEBUG: AWS_REGION = {aws_region}")
print(f"DEBUG: S3_BUCKET_NAME = {s3_bucket_name}")

# S3 client initialization (unchanged)
s3_client = None
try:
    s3_client = boto3.client('s3', region_name=aws_region)
    print("DEBUG: S3 client created successfully")
    
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
    else:
        print("WARNING: S3_BUCKET_NAME not set in .env file")
except Exception as e:
    print(f"ERROR: Failed to initialize S3 client: {e}")
    print(f"ERROR: Exception type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    s3_client = None

# Language dictionary
LANGUAGES = {
    'en': {
        'title': 'Text Processor',
        'input_label': 'Enter text:',
        'input_placeholder': 'Type your text here...',
        'process_button': 'Process',
        'output_label': 'Processed Text:',
        'gallery_title': 'S3 Bucket Images:',
        'no_s3_config': 'Please configure S3_BUCKET_NAME in .env file. Ensure EC2 instance has S3 permissions.',
        'no_images': 'No images found in the S3 bucket.',
        'output_placeholder': 'Processing results will appear here.'
    },
    'ja': {
        'title': 'テキストプロセッサ',
        'input_label': 'テキストを入力:',
        'input_placeholder': 'ここにテキストを入力してください...',
        'process_button': '処理',
        'output_label': '処理済みテキスト:',
        'gallery_title': 'S3 バケット画像:',
        'no_s3_config': 'S3_BUCKET_NAME を .env ファイルに設定してください。EC2 インスタンスに S3 パーミッションがあることを確認してください。',
        'no_images': 'S3 バケットに画像が見つかりません。',
        'output_placeholder': '処理結果がここに表示されます。'
    }
}

# Initialize Dash app with custom CSS for Japanese minimalism
external_stylesheets = [
    {
        'href': 'https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500&family=Inter:wght@300;400;500&display=swap',
        'rel': 'stylesheet'
    }
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Japanese minimalism styles - Wabi-sabi inspired with language toggle
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Text Processor</title>
        {%favicon%}
        {%css%}
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', 'Noto Sans JP', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                min-height: 100vh;
                color: #2d3748;
                line-height: 1.6;
                letter-spacing: 0.5px;
            }
            
            .container {
                max-width: 900px;
                margin: 0 auto;
                padding: 60px 20px;
            }
            
            .header-controls {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 40px;
            }
            
            .title {
                font-size: 2.5rem;
                font-weight: 300;
                text-align: center;
                margin: 0;
                color: #1a202c;
                letter-spacing: 2px;
                position: relative;
                flex: 1;
            }
            
            .title::after {
                content: '';
                display: block;
                width: 60px;
                height: 2px;
                background: linear-gradient(90deg, #4299e1, #63b3ed);
                margin: 20px auto 0;
                border-radius: 1px;
            }
            
            .lang-toggle {
                background: rgba(255, 255, 255, 0.8);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 25px;
                padding: 8px 20px;
                font-size: 0.95rem;
                font-weight: 500;
                color: #2d3748;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
                letter-spacing: 0.5px;
            }
            
            .lang-toggle:hover {
                background: white;
                transform: translateY(-1px);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
                border-color: #4299e1;
            }
            
            .lang-toggle.active {
                background: linear-gradient(135deg, #4299e1, #3182ce);
                color: white;
                border-color: #4299e1;
            }
            
            .input-section, .output-section {
                background: rgba(255, 255, 255, 0.85);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 20px;
                padding: 40px;
                margin-bottom: 40px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.05);
                transition: all 0.3s ease;
            }
            
            .input-section:hover, .output-section:hover {
                transform: translateY(-2px);
                box-shadow: 0 25px 50px rgba(0, 0, 0, 0.08);
            }
            
            .label {
                font-size: 1.1rem;
                font-weight: 400;
                margin-bottom: 20px;
                color: #2d3748;
                display: block; 
            }
            
            .textarea {
                width: 100%;
                min-height: 160px;
                padding: 24px;
                font-size: 16px;
                line-height: 1.7;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                background: rgba(255, 255, 255, 0.9);
                font-family: inherit;
                resize: vertical;
                transition: all 0.3s ease;
                color: #2d3748;
            }
            
            .textarea:focus {
                outline: none;
                border-color: #4299e1;
                box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
                background: white;
            }
            
            .process-btn {
                display: block;
                width: 200px;
                margin: 30px auto 0;
                padding: 16px 40px;
                font-size: 1.1rem;
                font-weight: 500;
                color: white;
                background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
                border: none;
                border-radius: 50px;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 10px 25px rgba(66, 153, 225, 0.3);
                letter-spacing: 1px;
            }
            
            .process-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 15px 35px rgba(66, 153, 225, 0.4);
                background: linear-gradient(135deg, #3182ce 0%, #2b6cb0 100%);
            }
            
            .process-btn:active {
                transform: translateY(0);
            }
            
            .output-content {
                min-height: 120px;
                padding: 30px;
                background: linear-gradient(135deg, rgba(255,255,255,0.7) 0%, rgba(248,250,252,0.7) 100%);
                border-radius: 16px;
                border: 1px solid rgba(226, 232, 240, 0.5);
                font-size: 18px;
                line-height: 1.8;
                color: #2d3748;
                white-space: pre-wrap;
                font-family: 'Noto Sans JP', 'Inter', monospace;
                letter-spacing: 0.8px;
                backdrop-filter: blur(10px);
            }
            
            .gallery-section {
                background: rgba(255, 255, 255, 0.85);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.05);
            }
            
            .gallery-title {
                font-size: 1.4rem;
                font-weight: 400;
                margin-bottom: 30px;
                color: #2d3748;
                text-align: center;
                letter-spacing: 1px;
            }
            
            .gallery {
                display: flex;
                flex-wrap: wrap;
                gap: 25px;
                justify-content: center;
            }
            
            .gallery-item {
                flex: 0 1 280px;
                background: white;
                border-radius: 16px;
                padding: 20px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease;
                text-align: center;
            }
            
            .gallery-item:hover {
                transform: translateY(-5px);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
            }
            
            .gallery-img {
                width: 100%;
                height: 200px;
                object-fit: cover;
                border-radius: 12px;
                margin-bottom: 15px;
            }
            
            .gallery-filename {
                font-size: 0.9rem;
                color: #718096;
                word-break: break-all;
                line-height: 1.4;
            }
            
            .empty-state {
                text-align: center;
                padding: 60px 20px;
                color: #a0aec0;
                font-size: 1.1rem;
                letter-spacing: 0.5px;
            }
            
            @media (max-width: 768px) {
                .container {
                    padding: 40px 15px;
                }
                
                .header-controls {
                    flex-direction: column;
                    gap: 20px;
                    text-align: center;
                }
                
                .title {
                    font-size: 2rem;
                    margin-bottom: 0;
                }
                
                .input-section, .output-section, .gallery-section {
                    padding: 30px 20px;
                }
                
                .gallery-item {
                    flex: 0 1 100%;
                    max-width: 350px;
                }
            }
        </style>
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

# Updated layout with language toggle
app.layout = html.Div(className="container", children=[
    html.Div(className="header-controls", children=[
        html.H1(id='app-title', className="title"),
        html.Button('EN', id='lang-toggle', className='lang-toggle active', n_clicks=0)
    ]),
    
    html.Div(id='input-section', className="input-section", children=[
        html.Label(id='input-label', className="label"),
        dcc.Textarea(
            id='input-text',
            className='textarea'
        ),
        html.Button(id='process-button', n_clicks=0, className='process-btn')
    ]),
    
    html.Div(id='output-section', className="output-section", children=[
        html.Div(id='output-text', className='output-content')
    ]),
    
    html.Div(className="gallery-section", children=[
        html.H3(id='gallery-title', className="gallery-title"),
        html.Div(id='s3-images')
    ])
])

# get_s3_images function (unchanged)
def get_s3_images():
    if not s3_client or not s3_bucket_name:
        return []
    
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
    image_urls = []
    
    try:
        response = s3_client.list_objects_v2(Bucket=s3_bucket_name)
        
        if 'Contents' in response:
            for obj in response['Contents']:
                key = obj['Key']
                if any(key.lower().endswith(ext) for ext in image_extensions):
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

# Language toggle callback
@app.callback(
    [Output('app-title', 'children'),
     Output('input-label', 'children'),
     Output('input-text', 'placeholder'),
     Output('process-button', 'children'),
     Output('gallery-title', 'children'),
     Output('lang-toggle', 'children'),
     Output('lang-toggle', 'className')],
    Input('lang-toggle', 'n_clicks')
)
def toggle_language(n_clicks):
    current_lang = 'en' if n_clicks % 2 == 0 else 'ja'
    lang_text = 'JA' if current_lang == 'en' else 'EN'
    class_name = 'lang-toggle active' if current_lang == 'en' else 'lang-toggle'
    
    texts = {
        'title': LANGUAGES[current_lang]['title'],
        'input_label': LANGUAGES[current_lang]['input_label'],
        'placeholder': LANGUAGES[current_lang]['input_placeholder'],
        'process_btn': LANGUAGES[current_lang]['process_button'],
        'gallery_title': LANGUAGES[current_lang]['gallery_title'],
        'lang_text': lang_text,
        'class_name': class_name
    }
    
    return (
        texts['title'],
        texts['input_label'],
        texts['placeholder'],
        texts['process_btn'],
        texts['gallery_title'],
        texts['lang_text'],
        texts['class_name']
    )

# Text processing callback
@app.callback(
    Output('output-text', 'children'),
    [Input('process-button', 'n_clicks'),
     Input('input-text', 'value')],
    [Input('lang-toggle', 'n_clicks')]
)
def process_text(n_clicks_process, input_value, n_clicks_lang):
    current_lang = 'en' if n_clicks_lang % 2 == 0 else 'ja'
    if n_clicks_process > 0 and input_value:
        processed = input_value.replace('a', '@').replace('i', '!').replace('e', '&')
        return processed
    return LANGUAGES[current_lang]['output_placeholder']

# S3 images callback
@app.callback(
    Output('s3-images', 'children'),
    Input('process-button', 'n_clicks'),
    [Input('lang-toggle', 'n_clicks')]
)
def display_s3_images(n_clicks_process, n_clicks_lang):
    current_lang = 'en' if n_clicks_lang % 2 == 0 else 'ja'
    images = get_s3_images()
    
    if not images:
        if not s3_client or not s3_bucket_name:
            return html.Div(
                LANGUAGES[current_lang]['no_s3_config'],
                className='empty-state'
            )
        return html.Div(LANGUAGES[current_lang]['no_images'], className='empty-state')
    
    image_elements = []
    for img in images:
        image_elements.append(
            html.Div(className='gallery-item', children=[
                html.Img(
                    src=img['url'],
                    className='gallery-img',
                    alt=img['key']
                ),
                html.P(img['key'], className='gallery-filename')
            ])
        )
    
    return html.Div(image_elements, className='gallery')

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8050)
