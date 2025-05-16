import os
import xml.etree.ElementTree as ET
import json
import requests
from datetime import datetime


class PubMedCentralSearch:
    """
    PubMed Central API Retriever - Enhanced version with metadata extraction
    """

    def __init__(self, query, query_domains=None):
        """
        Initializes the PubMedCentralSearch object.
        Args:
            query: The search query.
        """
        self.query = query
        self.api_key = self._retrieve_api_key()

    def _retrieve_api_key(self):
        """
        Retrieves the NCBI API key from environment variables.
        Returns:
            The API key.
        """
        try:
            api_key = os.environ.get("NCBI_API_KEY", "f53a067f173f9df219d4c14fb458afd80b08")
            return api_key
        except Exception:
            raise Exception(
                "NCBI API key not found. Please set the NCBI_API_KEY environment variable. "
                "You can obtain your key from https://www.ncbi.nlm.nih.gov/account/"
            )

    def search(self, max_results=10):
        """
        Searches the query using the PubMed Central API.
        Args:
            max_results: The maximum number of results to return.
        Returns:
            A list of search results.
        """
        print(f"Searching for articles about: {self.query}")
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        
        params = {
            "db": "pmc",
            "term": f"{self.query}",
            "retmax": max_results * 3,  # Get more in case some don't have content
            "usehistory": "y",
            "api_key": self.api_key,
            "retmode": "json",
            "sort": "relevance"
        }
        
        response = requests.get(base_url, params=params)

        if response.status_code != 200:
            raise Exception(
                f"Failed to retrieve data: {response.status_code} - {response.text}"
            )

        results = response.json()
        ids = results["esearchresult"]["idlist"]
        print(f"Found {len(ids)} articles in PMC database")

        search_response = []
        articles_processed = 0
        
        for article_id in ids:
            articles_processed += 1
            print(f"Processing article {articles_processed}/{len(ids)}: PMC{article_id}")
            
            try:
                xml_content = self.fetch([article_id])
                article_data = self.parse_xml(xml_content)
                citation_count = self.get_citation_count(article_id)
                
                if article_data and article_data["title"] and (article_data["abstract"] or article_data["body"]):
                    print(f"✓ Article has content. Title: {article_data['title'][:50]}...")
                    
                    article_data["citation_count"] = citation_count
                    article_data["pmc_id"] = article_id
                    
                    search_response.append({
                        "href": f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{article_id}/",
                        "metadata": {
                            "pmc_id": article_id,
                            "title": article_data['title'],
                            "authors": article_data['authors'],
                            "journal": article_data['journal'],
                            "publication_date": article_data['publication_date'],
                            "citation_count": citation_count
                        },
                        "body": f"{article_data['title']}\n\n{article_data['abstract']}\n\n{article_data['body'][:1500]}...",
                    })
                else:
                    print("✗ Article missing required content (title, abstract, or body)")
            except Exception as e:
                print(f"✗ Error processing article {article_id}: {e}")
                continue

            if len(search_response) >= max_results:
                print(f"Reached target of {max_results} results")
                break
                
            if articles_processed >= max_results * 5:
                print(f"Processed maximum number of articles ({articles_processed})")
                break

        print(f"Final results: {len(search_response)} articles with content")
        return search_response

    def get_citation_count(self, article_id):
        """
        Retrieves citation count for a PMC article using the NCBI E-utilities API.
        
        Args:
            article_id: PMC ID of the article
            
        Returns:
            The number of citations or 0 if unavailable
        """
        try:
            # Use the elink utility to get citation data
            base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi"
            params = {
                "dbfrom": "pmc",
                "id": article_id,
                "linkname": "pmc_pmc_citedby",  # Get articles that cite this one
                "retmode": "json",
                "api_key": self.api_key
            }
            
            response = requests.get(base_url, params=params)
            
            if response.status_code != 200:
                print(f"Failed to retrieve citation data: {response.status_code}")
                return 0
                
            data = response.json()
            
            # Parse the linkset data to get citation count
            if "linksets" in data and len(data["linksets"]) > 0:
                linkset = data["linksets"][0]
                if "linksetdbs" in linkset and len(linkset["linksetdbs"]) > 0:
                    for linksetdb in linkset["linksetdbs"]:
                        if linksetdb.get("linkname") == "pmc_pmc_citedby":
                            return len(linksetdb.get("links", []))
            
            return 0
        except Exception as e:
            print(f"Error retrieving citation count: {e}")
            return 0

    def fetch(self, ids):
        """
        Fetches the full text content for given article IDs.
        Args:
            ids: List of article IDs.
        Returns:
            XML content of the articles.
        """
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        params = {
            "db": "pmc",
            "id": ",".join(ids),
            "retmode": "xml",
            "api_key": self.api_key,
        }
        response = requests.get(base_url, params=params)

        if response.status_code != 200:
            raise Exception(
                f"Failed to retrieve data: {response.status_code} - {response.text}"
            )

        return response.text

    def parse_xml(self, xml_content):
        """
        Parses the XML content to extract title, abstract, body, and metadata.
        Args:
            xml_content: XML content of the article.
        Returns:
            Dictionary containing title, abstract, body text, and metadata.
        """
        try:
            root = ET.fromstring(xml_content)
            
            # Handle different XML structures
            article = None
            if root.tag == 'pmc-articleset':
                article = root.find('.//article')
            else:
                article = root
                
            if article is None:
                return None

            # Get title - try multiple approaches
            title = ""
            title_paths = [
                './/article-title',
                './/title-group/article-title',
                './/front/article-meta/title-group/article-title',
                './/front-stub/title-group/article-title',
                './/journal-meta/journal-title'
            ]
            
            for path in title_paths:
                title_elem = article.find(path)
                if title_elem is not None:
                    title = ''.join(title_elem.itertext()).strip()
                    break
            
            # Extract author information
            authors = self._extract_authors(article)
            
            # Extract journal information
            journal_info = self._extract_journal_info(article)
            
            # Extract publication date
            pub_date = self._extract_publication_date(article)
            
            # Get abstract - try multiple approaches
            abstract_text = ""
            abstract_paths = [
                './/abstract',
                './/front/article-meta/abstract',
                './/front-stub/abstract'
            ]
            
            for path in abstract_paths:
                abstract = article.find(path)
                if abstract is not None:
                    # Try to get paragraphs first
                    paragraphs = abstract.findall('.//p')
                    if paragraphs:
                        abstract_text = ' '.join(''.join(p.itertext()).strip() for p in paragraphs)
                    else:
                        # If no paragraphs, get all text
                        abstract_text = ''.join(abstract.itertext()).strip()
                    break

            # Get body content - try multiple approaches
            body = []
            body_paths = [
                './/body',
                './/article-body',
                './/main'
            ]
            
            for path in body_paths:
                body_elem = article.find(path)
                if body_elem is not None:
                    # Try to extract sections with headings
                    sections = body_elem.findall('.//sec')
                    if sections:
                        for sec in sections:
                            # Add section title if present
                            sec_title = sec.findtext('.//title')
                            if sec_title:
                                body.append(f"**{sec_title.strip()}**")
                            
                            # Add paragraphs
                            for p in sec.findall('.//p'):
                                p_text = ''.join(p.itertext()).strip()
                                if p_text:
                                    body.append(p_text)
                    else:
                        # If no sections, get paragraphs directly
                        for p in body_elem.findall('.//p'):
                            p_text = ''.join(p.itertext()).strip()
                            if p_text:
                                body.append(p_text)
                    break
            
            # Try sections approach if no body found
            if not body:
                for sec in article.findall('.//sec'):
                    sec_title = sec.findtext('.//title')
                    if sec_title:
                        body.append(f"**{sec_title.strip()}**")
                    
                    for p in sec.findall('.//p'):
                        p_text = ''.join(p.itertext()).strip()
                        if p_text:
                            body.append(p_text)

            return {
                "title": title or "No title found", 
                "abstract": abstract_text or "No abstract available", 
                "body": "\n\n".join(body),
                "authors": authors,
                "journal": journal_info,
                "publication_date": pub_date
            }
        except Exception as e:
            print(f"Error parsing XML: {e}")
            return None
            
    def _extract_authors(self, article):
        """
        Extracts author information from the article XML.
        
        Args:
            article: The article XML element
            
        Returns:
            List of author dictionaries with names and affiliations
        """
        authors = []
        
        # Multiple possible paths for contributor/author groups
        contrib_group_paths = [
            './/contrib-group',
            './/front/article-meta/contrib-group',
            './/front-stub/contrib-group'
        ]
        
        for group_path in contrib_group_paths:
            contrib_groups = article.findall(group_path)
            if not contrib_groups:
                continue
                
            for contrib_group in contrib_groups:
                for contrib in contrib_group.findall('.//contrib[@contrib-type="author"]'):
                    author_info = {}
                    
                    # Get name components
                    surname = contrib.findtext('.//surname')
                    given_names = contrib.findtext('.//given-names')
                    
                    if surname and given_names:
                        author_info['name'] = f"{given_names} {surname}"
                    elif surname:
                        author_info['name'] = surname
                    else:
                        # Try to find a string-name
                        string_name = contrib.findtext('.//string-name')
                        if string_name:
                            author_info['name'] = string_name.strip()
                        else:
                            continue  # Skip authors with no name
                    
                    # Get affiliations
                    affiliations = []
                    
                    # Direct affiliation elements
                    for aff in contrib.findall('.//aff'):
                        aff_text = ''.join(aff.itertext()).strip()
                        if aff_text:
                            affiliations.append(aff_text)
                    
                    # Linked affiliations via xref
                    for xref in contrib.findall('.//xref[@ref-type="aff"]'):
                        aff_id = xref.get('rid')
                        if aff_id:
                            # Find the corresponding affiliation in the article
                            aff = article.find(f'.//aff[@id="{aff_id}"]')
                            if aff is not None:
                                aff_text = ''.join(aff.itertext()).strip()
                                if aff_text:
                                    affiliations.append(aff_text)
                    
                    if affiliations:
                        author_info['affiliations'] = affiliations
                    
                    authors.append(author_info)
                
                # If we found authors, no need to check other groups
                if authors:
                    break
            
            # If we found authors, no need to check other paths
            if authors:
                break
        
        return authors
    
    def _extract_journal_info(self, article):
        """
        Extracts journal information from the article XML.
        
        Args:
            article: The article XML element
            
        Returns:
            Dictionary with journal title, ISSN, publisher, etc.
        """
        journal_info = {}
        
        # Journal title
        journal_title_paths = [
            './/journal-title',
            './/journal-meta/journal-title',
            './/journal-meta/journal-title-group/journal-title'
        ]
        
        for path in journal_title_paths:
            journal_title = article.findtext(path)
            if journal_title:
                journal_info['title'] = journal_title.strip()
                break
        
        # ISSN
        issn = article.findtext('.//journal-meta/issn')
        if issn:
            journal_info['issn'] = issn.strip()
        
        # Publisher
        publisher_name = article.findtext('.//journal-meta/publisher/publisher-name')
        if publisher_name:
            journal_info['publisher'] = publisher_name.strip()
        
        # Volume, issue, pages
        volume = article.findtext('.//front/article-meta/volume')
        if volume:
            journal_info['volume'] = volume.strip()
            
        issue = article.findtext('.//front/article-meta/issue')
        if issue:
            journal_info['issue'] = issue.strip()
            
        fpage = article.findtext('.//front/article-meta/fpage')
        lpage = article.findtext('.//front/article-meta/lpage')
        if fpage and lpage:
            journal_info['pages'] = f"{fpage.strip()}-{lpage.strip()}"
        elif fpage:
            journal_info['pages'] = fpage.strip()
        
        return journal_info
    
    def _extract_publication_date(self, article):
        """
        Extracts publication date from the article XML.
        
        Args:
            article: The article XML element
            
        Returns:
            Publication date as string in YYYY-MM-DD format (partial if unavailable)
        """
        pub_date = {}
        
        # Find publication date elements - try multiple paths
        pub_date_paths = [
            './/pub-date[@pub-type="epub"]',
            './/pub-date[@publication-format="electronic"]',
            './/pub-date[@date-type="pub"]',
            './/pub-date',
            './/front/article-meta/pub-date',
            './/front-stub/pub-date'
        ]
        
        for path in pub_date_paths:
            pub_date_elem = article.find(path)
            if pub_date_elem is not None:
                year = pub_date_elem.findtext('year')
                month = pub_date_elem.findtext('month')
                day = pub_date_elem.findtext('day')
                
                if year:
                    pub_date['year'] = year.strip()
                    if month:
                        pub_date['month'] = month.strip().zfill(2)
                        if day:
                            pub_date['day'] = day.strip().zfill(2)
                    break
        
        # Format the date as string
        if 'year' in pub_date:
            if 'month' in pub_date and 'day' in pub_date:
                return f"{pub_date['year']}-{pub_date['month']}-{pub_date['day']}"
            elif 'month' in pub_date:
                return f"{pub_date['year']}-{pub_date['month']}"
            else:
                return pub_date['year']
        
        return "Unknown"