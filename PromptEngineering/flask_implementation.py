from flask import Flask, request, render_template_string
from flask_cors import CORS  # Import Flask-CORS
from Research_paper_function import generate_short_query
from Search_Papers import search_most_cited_papers

app = Flask(__name__)
CORS(app)  # Enable CORS for the entire app

# HTML Template for the Home Page
home_page = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Paper Query</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            padding: 20px;
            background-color: #f4f4f9;
        }
        form {
            max-width: 600px;
            margin: auto;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        textarea {
            width: 100%;
            height: 100px;
            margin-bottom: 10px;
            padding: 10px;
            font-size: 16px;
        }
        button {
            background-color: #007BFF;
            color: white;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <h1 style="text-align:center;">Research Paper Generator</h1>
    <form method="POST" action="/search">
        <label for="long_prompt">Enter your prompt:</label><br>
        <textarea id="long_prompt" name="long_prompt" placeholder="Type your research prompt here..." required></textarea><br>
        <button type="submit">Submit</button>
    </form>
</body>
</html>
"""

# HTML Template for the Results Page
results_page = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Papers</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            padding: 20px;
            background-color: #f4f4f9;
        }
        .container {
            max-width: 800px;
            margin: auto;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h2 {
            color: #007BFF;
        }
        ul {
            list-style-type: none;
            padding-left: 0;
        }
        li {
            margin-bottom: 10px;
        }
        a {
            color: #007BFF;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Most Cited Research Papers:</h2>
        {% if results %}
          <ul>
              {% for paper in results %}
                  <li><a href="{{ paper['url'] }}" target="_blank">{{ paper['title'] }}</a></li>
              {% endfor %}
          </ul>
        {% else %}
          <p>No results found.</p>
        {% endif %}
        
        <a href="/" style="display:block; margin-top:20px; text-align:center; color:#007BFF;">New Search</a>
    </div>
</body>
</html>
"""

# Modified search_most_cited_papers Function
def search_most_cited_papers(query, num_results=5):
    from scholarly import scholarly

    search_query = scholarly.search_pubs(query)
    papers = []
    
    for _ in range(num_results):
        try:
            paper = next(search_query)
            title = paper['bib']['title']
            url = paper.get('pub_url', 'N/A')
            
            papers.append({'title': title, 'url': url})
        except StopIteration:
            break
    
    return papers

# Home route to display the form
@app.route("/search", methods=["POST"])
def home():
    if request.method == "POST":
        # Retrieve user input from the form
        long_prompt = request.form.get("long_prompt")
        print(long_prompt)
        
        # Process the input using your functions
        short_query = generate_short_query(long_prompt)
        
        # Get the search results using modified search_most_cited_papers function
        results = search_most_cited_papers(short_query)
        
        # Render the results page with only the output
        return render_template_string(results_page, results=results)
    
    # Render the home page template
    return render_template_string(home_page)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True,port=5000)
