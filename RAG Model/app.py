# flask implementation.

from flask import Flask, render_template_string, jsonify, request
import fitz  # PyMuPDF
import base64
import os
from rag import get_contextual_definition

app = Flask(__name__)

# Custom text processing function (built-in for single-file solution)
def process_text(selection):
    """Example processing function - modify this as needed"""
    return {
        "length": len(selection),
        "word_count": len(selection.split()),
        "analysis": get_contextual_definition(selection)
    }

def pdf_to_images(pdf_path):
    """Convert PDF to base64 images with error handling"""
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found at {pdf_path}")
            
        doc = fitz.open(pdf_path)
        pages = []
        
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_data = {
                "image": base64.b64encode(pix.tobytes("png")).decode("utf-8"),
                "width": pix.width,
                "height": pix.height
            }
            pages.append(img_data)
            
        return pages
        
    except Exception as e:
        print(f"PDF Processing Error: {str(e)}")
        return []

@app.route('/process-selection', methods=['POST'])
def handle_selection():
    try:
        data = request.json
        selection = data.get('text', '').strip()
        if not selection:
            return jsonify({"error": "Empty selection"}), 400
            
        result = process_text(selection)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def pdf_viewer():
    pdf_path = "research.pdf"
    pages = pdf_to_images(pdf_path)
    
    if not pages:
        return render_template_string('''
            <h1>Error Loading PDF</h1>
            <p>Could not load PDF file at: {{ pdf_path }}</p>
            <p>Check if:</p>
            <ul>
                <li>File exists at specified path</li>
                <li>File is not password protected</li>
                <li>File is a valid PDF document</li>
            </ul>
        ''', pdf_path=os.path.abspath(pdf_path))
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>PDF Analyzer</title>
        <style>
            body { margin: 0; font-family: Arial, sans-serif; }
            .container { display: flex; height: 100vh; }
            .pdf-viewer { 
                flex: 2; 
                overflow-y: auto; 
                padding: 20px;
                background: #f0f0f0;
            }
            .analysis-panel {
                flex: 1;
                padding: 25px;
                background: #ffffff;
                box-shadow: -2px 0 15px rgba(0,0,0,0.1);
            }
            .page {
                margin-bottom: 30px;
                background: white;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .analysis-card {
                background: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
            }
            img { max-width: 100%; height: auto; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="pdf-viewer">
                {% for page in pages %}
                <div class="page">
                    <img src="data:image/png;base64,{{ page.image }}" 
                         style="width: {{ page.width//2 }}px; height: {{ page.height//2 }}px">
                </div>
                {% endfor %}
            </div>
            
            <div class="analysis-panel">
                <h2>Text Analysis</h2>
                <div id="results">
                    <div class="analysis-card" id="default-message">
                        Select text in the PDF to see analysis results
                    </div>
                </div>
            </div>
        </div>

        <script>
            const resultsDiv = document.getElementById('results');
            let currentSelection = '';
            
            async function updateAnalysis(selection) {
                try {
                    const response = await fetch('/process-selection', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({text: selection})
                    });
                    
                    const data = await response.json();
                    
                    if(data.error) {
                        resultsDiv.innerHTML = `
                            <div class="analysis-card error">
                                Error: ${data.error}
                            </div>
                        `;
                        return;
                    }
                    
                    resultsDiv.innerHTML = `
                        <div class="analysis-card">
                            <h3>Selected Text:</h3>
                            <p class="selection-preview">"${selection}"</p>
                            <div class="analysis-results">
                                <p>Character Count: ${data.length}</p>
                                <p>Word Count: ${data.word_count}</p>
                                <p>Custom Analysis: ${data.analysis}</p>
                            </div>
                        </div>
                    `;
                    
                } catch(error) {
                    console.error('Analysis Error:', error);
                    resultsDiv.innerHTML = `
                        <div class="analysis-card error">
                            Network Error: Could not get analysis
                        </div>
                    `;
                }
            }

            document.addEventListener('selectionchange', () => {
                const selection = window.getSelection().toString().trim();
                if(selection && selection !== currentSelection) {
                    currentSelection = selection;
                    updateAnalysis(selection);
                }
            });
        </script>
    </body>
    </html>
    ''', pages=pages)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
