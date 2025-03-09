from flask import Flask, render_template_string
from Research_paper_function import generate_short_query
from Search_Papers import search_most_cited_papers

app = Flask(__name__)

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
        <h2>Recommended research papers : </h2>
        {% if results %}
          <ul>
              {% for paper in results %}
                  <li><a href="{{ paper['url'] }}" target="_blank">{{ paper['title'] }}</a></li>
              {% endfor %}
          </ul>
        {% else %}
          <p>No results found.</p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    # Get user input from the terminal
    long_prompt = "Thermodynamics"
    
    # Process the input using your functions
    short_query = generate_short_query(long_prompt)
    
    # Get the search results using modified search_most_cited_papers function
    results = search_most_cited_papers(short_query)
    
    # Render the results page with the output and user prompt
    return render_template_string(results_page, results=results, user_prompt=long_prompt)

if __name__ == "__main__":
    app.run(debug=True)
