'''
Compares Papers using details like title, citation count and year published and asks Gemini Model to rank them on their influence.
Will need to add the ranking part in a function and possible fine-tune it.
'''
import google.generativeai as genai
from IPython.display import HTML, Markdown, display
import sys
import requests
sys.path.append("./docker-python/patches")

def format_paper_list(paper_names):
    if not paper_names:
        return "No papers provided."
    
    formatted_list = "The papers are: " + ", ".join(f"{i+1}. {name}" for i, name in enumerate(paper_names))
    return formatted_list

dois = [
    "10.1145/3292500.3332280",
    "10.1109/5.771073",
    "10.1038/s41586-019-1666-5"
]

# Base URL for Semantic Scholar API
base_url = "https://api.semanticscholar.org/graph/v1/paper/"

fields = "title,year,citationCount"

details = ""
for doi in dois:
    url = f"{base_url}{doi}?fields={fields}"
    response = requests.get(url)
    data = response.json()

    # Extract details
    title = data.get("title", "Unknown Title")
    year = data.get("year", "Unknown Year")
    citation_count = data.get("citationCount", "Unknown Citations")

    details += "Title:" + title + ", Year:" + str(year) + ", Citations:" + str(citation_count) + "\n"

genai.configure(api_key="xxxx")
flash = genai.GenerativeModel('gemini-1.5-flash')

paper_names = [
    "Towards a Security Analysis of Radiological Medical Devices using the MITRE ATT&CK Framework",
    "A Comprehensive Review of the State-of-the-Art on Security and Privacy Issues in Healthcare",
    "MITRE ATT&CK Applications in Cybersecurity and The Way Forward"
]

prompt = "Identify a single most influential academic papers from the following list: " + details + ". Normalize by the time since publication." + "Rank them based on citation impact per year and overall contribution to their domain." + "Provide a brief summary and explain why it is considered influential."
response = flash.generate_content(prompt)
print(response.text)
