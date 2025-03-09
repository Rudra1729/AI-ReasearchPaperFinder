from scholarly import scholarly

def search_most_cited_papers(query, num_results=5):
    search_query = scholarly.search_pubs(query)
    papers = []
    
    for _ in range(num_results):
        try:
            paper = next(search_query)
            citation_count = paper.get('num_citations', 0)  # Get citation count
            papers.append((paper, citation_count))
        except StopIteration:
            break
    
    # Sort papers by citation count in descending order
    sorted_papers = sorted(papers, key=lambda x: x[1], reverse=True)
    
    # Format results for rendering in Flask
    formatted_results = []
    for i, (paper, citations) in enumerate(sorted_papers, 1):
        title = paper['bib']['title']
        url = paper.get('pub_url', 'N/A')
        formatted_results.append(f"{i}. {title}\n   Citations: {citations}\n   URL: {url}")
    
    return formatted_results