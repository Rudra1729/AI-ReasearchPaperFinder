import google.generativeai as genai
from IPython.display import HTML, Markdown, display

def get_word_meaning(GOOGLE_API_KEY,research_paper_name,word):
  genai.configure(api_key=GOOGLE_API_KEY)
  flash = genai.GenerativeModel('gemini-1.5-flash')
  response = flash.generate_content("Explain the word "+word+" in the context of the research paper "+research_paper_name+" in a clear and beginner-friendly manner. Assume the reader has no prior knowledge, but make it informative enough to be useful for a professional as well. Keep the explanation concise and to the point, avoiding unnecessary complexity while preserving depth. Use simple analogies if helpful. Keep it really concise less than 100 words")
  return response.text
