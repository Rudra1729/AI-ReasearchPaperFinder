# flask implementation.

from flask import Flask, render_template_string, jsonify, request
import fitz  # PyMuPDF
import base64
import os
import rag
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import threading
import time
import importlib
import flask_implementation


from pdf_from_link import download_arxiv_pdf

app = Flask(__name__)
current_pdf_link = flask_implementation.link
current_pdf_path = download_arxiv_pdf(current_pdf_link)
 # Global variable to store the current PDF link


# Custom text processing function (built-in for single-file solution)
def process_text(selection):
    """Example processing function - modify this as needed"""
    return {
        "analysis": rag.get_contextual_definition(selection)
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

def monitor_link_changes():
    global current_pdf_link, current_pdf_path
    while True:
        importlib.reload(flask_implementation)
        new_link = flask_implementation.link
        if new_link != current_pdf_link:
            print(f"Detected change in link: {new_link}")
            current_pdf_link = new_link
            current_pdf_path = download_arxiv_pdf(current_pdf_link)
            reload_rag_model()


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
    
from rag import reload_rag_model

@app.route('/reload-rag', methods=['POST'])
def reload_rag():
    try:
        reload_rag_model()  # Use the updated PDF path
        return jsonify({"status": "success", "message": "RAG model reloaded."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    

@app.route('/update-pdf', methods=['POST'])
def update_pdf():
    global current_pdf_link
    try:
        data = request.get_json()
        new_link = data.get("link")

        if not new_link:
            return jsonify({"error": "Missing 'link' in request data"}), 400

        # Download the new PDF
        result = download_arxiv_pdf(new_link)
        if not result or not os.path.exists(result):
            return jsonify({"error": "Failed to download PDF"}), 500

        # Update the global link variable
        current_pdf_link = new_link

        # Reload the RAG model with the new PDF
        reload_rag_model()

        return jsonify({"message": "PDF and model updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/')
def pdf_viewer():
    global current_pdf_link
    if not current_pdf_link:
        return render_template_string('<h1>No PDF link provided.</h1>')

    pdf_path = download_arxiv_pdf(current_pdf_link)
    pages = pdf_to_images(current_pdf_path)
    
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
                                <p>${data.analysis}</p>
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
    result = download_arxiv_pdf(flask_implementation.link)
    if not result or not os.path.exists(result):
        print("❌ Could not download the PDF. Exiting Flask server startup.")
        exit(1)

    from rag import reload_rag_model
    reload_rag_model()
    threading.Thread(target=monitor_link_changes, daemon=True).start()
    app.run(host='0.0.0.0', port=5001, debug=True)

