import os
import json
import requests
from typing import List, Dict, Optional


class SemanticScholarBulkSearch:
  

    BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"

    def __init__(
        self,
        query: str,
        api_key: Optional[str] = None,
        fields: str = "title,url,publicationTypes,publicationDate,openAccessPdf",
        year: Optional[str] = None,
        publication_date_range: Optional[str] = None,
        publication_types: Optional[str] = None,
        fields_of_study: Optional[str] = None,
        venue: Optional[str] = None,
        open_access_only: bool = False,
        min_citation_count: Optional[int] = None,
        sort: Optional[str] = None,
    ):
        self.query = query
        self.fields = fields
        self.year = year
        self.publication_date_range = publication_date_range
        self.publication_types = publication_types
        self.fields_of_study = fields_of_study
        self.venue = venue
        self.open_access_only = open_access_only
        self.min_citation_count = min_citation_count
        self.sort = sort
        self.api_key = api_key or os.getenv("SEMANTIC_SCHOLAR_API_KEY")
        self.headers = {"x-api-key": self.api_key} if self.api_key else {}

    def build_params(self) -> Dict:
        params = {
            "query": self.query,
            "fields": "url,papers.abstract,papers.authors"
        }
        if self.year:
            params["year"] = self.year
        if self.publication_date_range:
            params["publicationDateOrYear"] = self.publication_date_range
        if self.publication_types:
            params["publicationTypes"] = self.publication_types
        if self.fields_of_study:
            params["fieldsOfStudy"] = self.fields_of_study
        if self.venue:
            params["venue"] = self.venue
        if self.min_citation_count is not None:
            params["minCitationCount"] = str(self.min_citation_count)
        if self.sort:
            params["sort"] = self.sort
        if self.open_access_only:
            params["openAccessPdf"] = ""  # just presence is enough
        return params

    def search(self, max_results: int = 1000) -> List[Dict[str, str]]:
        params = self.build_params()
        results = []
        retrieved = 0
        token = None

        print(f"🔍 Starting Semantic Scholar bulk search for: {self.query}")
        while retrieved < max_results:
            if token:
                url = f"{self.BASE_URL}?token={token}"
                response = requests.get(url, headers=self.headers).json()
            else:
                response = requests.get(self.BASE_URL, params=params).json()

            if "data" not in response:
                print(f"❌ No data returned. Response: {response}")
                break

            results.extend(response["data"])
            retrieved += len(response["data"])
            print(f"✅ Retrieved {retrieved} papers...")

            if "token" not in response or retrieved >= max_results:
                break
            token = response["token"]

        print(f"🎉 Done! Total papers retrieved: {retrieved}")
        return results[:max_results]
    

    def parse_articles(self, results: List[Dict]) -> List[Dict[str, str]]:
        """
        Parse Semantic Scholar bulk API results into structured article metadata.
        """
        articles = []

        for item in results:
            try:
                # Skip if no public PDF
                if "openAccessPdf" not in item or not item["openAccessPdf"]:
                    continue

                pdf_url = item["openAccessPdf"].get("url", "Unavailable")

                # First author (if available)
                authors = item.get("authors", [])
                first_author = authors[0]["name"] if authors else "Unknown"

                # Extract year from publicationDate
                pub_date = item.get("publicationDate")
                year = pub_date.split("-")[0] if pub_date else "Unknown"

                article = {
                    "title": item.get("title", "No Title"),
                    "first_author": first_author,
                    "year": year,
                    "journal": item.get("venue", "Unknown"),
                    "url": item.get("url", "Unavailable"),
                    "pdf": pdf_url,
                    "abstract": item.get("abstract", "Abstract not available"),
                    "body": None  # Full text not provided by Semantic Scholar
                }

                articles.append(article)

            except Exception as e:
                print(f"⚠️ Failed to parse one article: {e}")

        return articles

    def save_to_json(self, papers: List[Dict], file_path: str = "papers.json"):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(papers, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved {len(papers)} papers to '{file_path}'")
        except Exception as e:
            print(f"❌ Error saving JSON: {e}")

# Example usage
if __name__ == "__main__":
    searcher = SemanticScholarBulkSearch(
        query='"generative ai"',
        api_key="sFZyF4wUYOEhSb1FDDW2LWyy8jwANj5CP73F1300"
    )
    papers = searcher.search(max_results=25)
    searcher.save_to_json(papers)