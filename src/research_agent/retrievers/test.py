from pubmed_central import PubMedCentralSearch

def test_final_search():
    # Create a search query
    query = "Machine learning PSS"
    
    # Initialize the search object
    pmc_search = PubMedCentralSearch(query)
    
    # Search for articles
    results = pmc_search.search(max_results=3)
    
    # Print the results
    print(f"\nFound {len(results)} results:")
    print(results[0])
"""
    print(results[0])
    for i, result in enumerate(results):
        print(f"\nResult {i+1}:")
        print(f"URL: {result['href']}")
        print(f"Content preview: {result['body'][:200]}...\n")
        print("-" * 80)
"""
if __name__ == "__main__":
    test_final_search()