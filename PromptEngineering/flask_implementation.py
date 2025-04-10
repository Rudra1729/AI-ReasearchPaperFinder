# from flask import Flask, render_template_string, request,jsonify
# from flask_cors import CORS  # Import CORS
# from Research_paper_function import generate_short_query
# from Search_Papers import search_most_cited_papers

# app = Flask(__name__)

# # Enable CORS for all routes
# CORS(app)

# # HTML Template for the Results Page
# results_page = """
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Research Papers</title>
#     <style>
#         body {
#             font-family: Arial, sans-serif;
#             margin: 20px;
#             padding: 20px;
#             background-color: #f4f4f9;
#         }
#         .container {
#             max-width: 800px;
#             margin: auto;
#             padding: 20px;
#             background: white;
#             border-radius: 8px;
#             box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
#         }
#         h2 {
#             color: #007BFF;
#         }
#         ul {
#             list-style-type: none;
#             padding-left: 0;
#         }
#         li {
#             margin-bottom: 10px;
#         }
#         a {
#             color: #007BFF;
#             text-decoration: none;
#         }
#         a:hover {
#             text-decoration: underline;
#         }
#     </style>
# </head>
# <body>
#     <div class="container">
#         <h2>Recommended research papers : </h2>
#         {% if results %}
#           <ul>
#               {% for paper in results %}
#                   <li><a href="{{ paper['url'] }}" target="_blank">{{ paper['title'] }}</a></li>
#               {% endfor %}
#           </ul>
#         {% else %}
#           <p>No results found.</p>
#         {% endif %}
#     </div>
# </body>
# </html>
# """

# @app.route("/search", methods=["POST"])
# def home():
#     # Get user input from the request JSON
#     data = request.get_json()

#     searchTerm = data.get('searchTerm', '')
#     long_prompt = searchTerm
#     print("long term", long_prompt)

#     # Process the input using your functions
#     short_query = generate_short_query(long_prompt)
    
#     # Get the search results using the modified search_most_cited_papers function
#     results = search_most_cited_papers(short_query)
    
#     # Render the results page with the output and user prompt
#     return jsonify({"results": results, "user_prompt": long_prompt})
    

# if __name__ == "__main__":
#     app.run(debug=True, port=5000)

from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from Research_paper_function import generate_short_query
from Search_Papers_Arvix import search_arxiv_papers

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

@app.route("/search", methods=["POST"])
def home():
    # Get user input from the request JSON
    data = request.get_json()

    searchTerm = data.get('searchTerm', '')
    long_prompt = searchTerm
    print("long term", long_prompt)

    # Process the input using your functions
    short_query = generate_short_query(long_prompt)
    
    # Get the search results using the modified search_most_cited_papers function
    results = search_arxiv_papers(short_query)
    
    # Return results as JSON instead of rendering HTML
    return jsonify({"results": results, "user_prompt": long_prompt})

@app.route('/log-click', methods=['POST'])
def log_click():
    data = request.get_json()
    print(f"User clicked on: {data['title']} - {data['url']}")
    
    # Optional: save to a file, database, or further processing
    return jsonify({"message": "Click logged successfully"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
