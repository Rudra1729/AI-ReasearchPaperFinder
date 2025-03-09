from scholarly import scholarly

def search_most_cited_papers(query, num_results=5):
    from scholarly import scholarly

    search_query = scholarly.search_pubs(query)
    papers = []
    
    for _ in range(num_results):
        try:
            paper = next(search_query)
            title = paper['bib']['title']
            url = paper.get('pub_url')
            citation_count = paper.get('num_citations', 0)
            
            if url:  # Only include papers with a valid URL
                papers.append({
                    'title': title,
                    'url': url,
                    'citations': citation_count
                })
        except StopIteration:
            break
    
    # Sort papers by citation count in descending order
    sorted_papers = sorted(papers, key=lambda x: x['citations'], reverse=True)
    
    return sorted_papers


# Example usage:
#print(search_most_cited_papers("JK Rowling"))
