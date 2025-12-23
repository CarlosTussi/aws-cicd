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


# 10-language dictionary (no Hebrew)
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
    },
    'zh': {
        'title': '文本处理器',
        'input_label': '输入文本：',
        'input_placeholder': '在这里输入您的文本...',
        'process_button': '处理',
        'output_label': '处理后的文本：',
        'gallery_title': 'S3 存储桶图片：',
        'no_s3_config': '请在 .env 文件中配置 S3_BUCKET_NAME。确保 EC2 实例具有 S3 权限。',
        'no_images': 'S3 存储桶中未找到图片。',
        'output_placeholder': '处理结果将显示在这里。'
    },
    'fr': {
        'title': 'Processeur de texte',
        'input_label': 'Entrez du texte :',
        'input_placeholder': 'Tapez votre texte ici...',
        'process_button': 'Traiter',
        'output_label': 'Texte traité :',
        'gallery_title': 'Images du bucket S3 :',
        'no_s3_config': 'Veuillez configurer S3_BUCKET_NAME dans le fichier .env. Assurez-vous que l\'instance EC2 a les permissions S3.',
        'no_images': 'Aucune image trouvée dans le bucket S3.',
        'output_placeholder': 'Les résultats du traitement apparaîtront ici.'
    },
    'pt-BR': {
        'title': 'Processador de Texto',
        'input_label': 'Digite o texto:',
        'input_placeholder': 'Digite seu texto aqui...',
        'process_button': 'Processar',
        'output_label': 'Texto Processado:',
        'gallery_title': 'Imagens do Bucket S3:',
        'no_s3_config': 'Configure S3_BUCKET_NAME no arquivo .env. Certifique-se de que a instância EC2 tem permissões S3.',
        'no_images': 'Nenhuma imagem encontrada no bucket S3.',
        'output_placeholder': 'Os resultados do processamento aparecerão aqui.'
    },
    'it': {
        'title': 'Processore di Testo',
        'input_label': 'Inserisci testo:',
        'input_placeholder': 'Digita il tuo testo qui...',
        'process_button': 'Elabora',
        'output_label': 'Testo Elaborato:',
        'gallery_title': 'Immagini Bucket S3:',
        'no_s3_config': 'Configura S3_BUCKET_NAME nel file .env. Assicurati che l\'istanza EC2 abbia i permessi S3.',
        'no_images': 'Nessuna immagine trovata nel bucket S3.',
        'output_placeholder': 'I risultati dell\'elaborazione appariranno qui.'
    },
    'ru': {
        'title': 'Обработчик текста',
        'input_label': 'Введите текст:',
        'input_placeholder': 'Введите ваш текст здесь...',
        'process_button': 'Обработать',
        'output_label': 'Обработанный текст:',
        'gallery_title': 'Изображения из S3 бакета:',
        'no_s3_config': 'Настройте S3_BUCKET_NAME в файле .env. Убедитесь, что EC2 имеет права доступа к S3.',
        'no_images': 'Изображения в S3 бакете не найдены.',
        'output_placeholder': 'Результаты обработки появятся здесь.'
    },
    'el': {
        'title': 'Επεξεργαστής Κειμένου',
        'input_label': 'Εισαγάγετε κείμενο:',
        'input_placeholder': 'Πληκτρολογήστε το κείμενό σας εδώ...',
        'process_button': 'Επεξεργασία',
        'output_label': 'Επεξεργασμένο Κείμενο:',
        'gallery_title': 'Εικόνες S3 Bucket:',
        'no_s3_config': 'Ρυθμίστε το S3_BUCKET_NAME στο αρχείο .env. Βεβαιωθείτε ότι η EC2 έχει δικαιώματα S3.',
        'no_images': 'Δεν βρέθηκαν εικόνες στο S3 bucket.',
        'output_placeholder': 'Τα αποτελέσματα επεξεργασίας θα εμφανιστούν εδώ.'
    },
    'ar': {
        'title': 'معالج النصوص',
        'input_label': 'أدخل النص:',
        'input_placeholder': 'اكتب نصك هنا...',
        'process_button': 'معالجة',
        'output_label': 'النص المعالج:',
        'gallery_title': 'صور حاوية S3:',
        'no_s3_config': 'يرجى تكوين S3_BUCKET_NAME في ملف .env. تأكد من أن مثيل EC2 لديه أذونات S3.',
        'no_images': 'لم يتم العثور على صور في حاوية S3.',
        'output_placeholder': 'ستظهر نتائج المعالجة هنا.'
    },
    'tl': {
        'title': 'Text Processor',
        'input_label': 'Ilagay ang teksto:',
        'input_placeholder': 'I-type ang iyong teksto dito...',
        'process_button': 'Proseso',
        'output_label': 'Na-process na Teksto:',
        'gallery_title': 'Mga Larawan ng S3 Bucket:',
        'no_s3_config': 'I-configure ang S3_BUCKET_NAME sa .env file. Siguraduhin na ang EC2 instance ay may S3 permissions.',
        'no_images': 'Walang natagpuang mga larawan sa S3 bucket.',
        'output_placeholder': 'Dito lalabas ang mga resulta ng pagproseso.'
    },
    'es': {
        'title': 'Procesador de Texto',
        'input_label': 'Ingresa texto:',
        'input_placeholder': 'Escribe tu texto aquí...',
        'process_button': 'Procesar',
        'output_label': 'Texto Procesado:',
        'gallery_title': 'Imágenes del Bucket S3:',
        'no_s3_config': 'Configura S3_BUCKET_NAME en el archivo .env. Asegúrate de que la instancia EC2 tenga permisos S3.',
        'no_images': 'No se encontraron imágenes en el bucket S3.',
        'output_placeholder': 'Los resultados del procesamiento aparecerán aquí.'
    }
}


# Language options for dropdown
LANGUAGE_OPTIONS = [
    {'label': '🇺🇸 English', 'value': 'en'},
    {'label': '🇯🇵 日本語', 'value': 'ja'},
    {'label': '🇨🇳 简体中文', 'value': 'zh'},
    {'label': '🇫🇷 Français', 'value': 'fr'},
    {'label': '🇧🇷 Português (BR)', 'value': 'pt-BR'},
    {'label': '🇮🇹 Italiano', 'value': 'it'},
    {'label': '🇷🇺 Русский', 'value': 'ru'},
    {'label': '🇬🇷 Ελληνικά', 'value': 'el'},
    {'label': '🇸🇦 العربية', 'value': 'ar'},
    {'label': '🇵🇭 Tagalog', 'value': 'tl'},
    {'label': '🇪🇸 Español', 'value': 'es'}
]


# Initialize Dash app with comprehensive font support
external_stylesheets = [
    {
        'href': 'https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500&family=Noto+Sans+SC:wght@300;400;500&family=Inter:wght@300;400;500&family=Noto+Sans:wght@300;400;500&family=Noto+Sans+Arabic:wght@300;400;500&display=swap',
        'rel': 'stylesheet'
    }
]


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# FIXED styles with proper z-index for dropdown
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
                font-family: 'Inter', 'Noto Sans JP', 'Noto Sans SC', 'Noto Sans', 'Noto Sans Arabic', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                min-height: 100vh;
                color: #2d3748;
                line-height: 1.6;
                letter-spacing: 0.5px;
                direction: ltr;
            }
            
            body.rtl {
                direction: rtl;
            }
            
            .container {
                max-width: 900px;
                margin: 0 auto;
                padding: 60px 20px;
                position: relative;
                z-index: 1;
            }
            
            .header-controls {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 40px;
                gap: 20px;
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
            
            .lang-dropdown {
                background: rgba(255, 255, 255, 0.9);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 12px;
                padding: 8px 16px;
                font-size: 1rem;
                font-weight: 500;
                color: #2d3748;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
                min-width: 200px;
                z-index: 1000;
                position: relative;
            }
            
            .lang-dropdown .Select-control {
                border-radius: 8px !important;
                background: white !important;
                border: 2px solid #e2e8f0 !important;
                z-index: 1001 !important;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15) !important;
            }
            
            .lang-dropdown .Select-menu-outer {
                z-index: 1002 !important;
                border-radius: 12px !important;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2) !important;
                border: 1px solid rgba(66, 153, 225, 0.2) !important;
                background: white !important;
                margin-top: 4px !important;
                max-height: 300px !important;
                overflow: auto !important;
            }
            
            .lang-dropdown:hover .Select-control {
                border-color: #4299e1 !important;
                box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1), 0 10px 30px rgba(0, 0, 0, 0.15) !important;
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
                z-index: 10;
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
                direction: inherit;
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
                font-family: inherit;
                letter-spacing: 0.8px;
                backdrop-filter: blur(10px);
                direction: inherit;
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
                direction: ltr;
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


# Updated layout with language dropdown
app.layout = html.Div(className="container", children=[
    html.Div(className="header-controls", children=[
        html.H1(id='app-title', className="title"),
        dcc.Dropdown(
            id='lang-dropdown',
            options=LANGUAGE_OPTIONS,
            value='en',  # Default English
            clearable=False,
            className='lang-dropdown'
        )
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


# Language dropdown callback - handles 10 languages, RTL only for Arabic
@app.callback(
    [Output('app-title', 'children'),
     Output('input-label', 'children'),
     Output('input-text', 'placeholder'),
     Output('process-button', 'children'),
     Output('gallery-title', 'children'),
     Output('input-section', 'className'),
     Output('output-section', 'className'),
     Output('output-text', 'className'),
     Output('input-text', 'dir')],
    Input('lang-dropdown', 'value')
)
def update_language(selected_lang):
    # RTL only for Arabic
    rtl_langs = ['ar']
    is_rtl = selected_lang in rtl_langs
    
    texts = LANGUAGES[selected_lang]
    dir_attr = 'rtl' if is_rtl else 'ltr'
    
    input_class = "input-section" + (" rtl" if is_rtl else "")
    output_class = "output-section" + (" rtl" if is_rtl else "")
    output_content_class = "output-content" + (" rtl" if is_rtl else "")
    
    return (
        texts['title'],
        texts['input_label'],
        texts['input_placeholder'],
        texts['process_button'],
        texts['gallery_title'],
        input_class,
        output_class,
        output_content_class,
        dir_attr
    )


# Text processing callback
@app.callback(
    Output('output-text', 'children'),
    [Input('process-button', 'n_clicks'),
     Input('input-text', 'value')],
    [Input('lang-dropdown', 'value')]
)
def process_text(n_clicks_process, input_value, selected_lang):
    if n_clicks_process > 0 and input_value:
        processed = input_value.replace('a', '@').replace('i', '!').replace('e', '&')
        return processed
    texts = LANGUAGES[selected_lang]
    return texts['output_placeholder']


# S3 images callback
@app.callback(
    Output('s3-images', 'children'),
    Input('process-button', 'n_clicks'),
    [Input('lang-dropdown', 'value')]
)
def display_s3_images(n_clicks_process, selected_lang):
    images = get_s3_images()
    
    if not images:
        if not s3_client or not s3_bucket_name:
            texts = LANGUAGES[selected_lang]
            return html.Div(
                texts['no_s3_config'],
                className='empty-state'
            )
        texts = LANGUAGES[selected_lang]
        return html.Div(texts['no_images'], className='empty-state')
    
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
