import os
import json
import xml.etree.ElementTree as ET
from Bio import Entrez
from ..config.config import config
from rich.console import Console
import typer
from ..logger.logger import Logger

console = Console()
logger = Logger().get_logger()

config = config.load_config("config.yaml")

class PubMedCentralSearch:
    """
    PubMed Central API Retriever using Biopython's Entrez module
    """

    def __init__(self, query, sort, max_results):
        """
        Initializes the PubMedCentralSearch object.
        Args:
            query: The search query.
            sort: Sort method for search results (e.g., 'relevance', 'pub+date').
        """
        self.query = query
        self.sort = sort
        self.max_results = max_results
        self.api_key = os.environ.get("NCBI_API_KEY",config["NCBI_API_KEY"])
        if self.api_key:
            Entrez.api_key = self.api_key

    def search(self, max_results=100000):
        try:
            handle = Entrez.esearch(
                db="pmc",
                term=self.query,
                retmax=max_results,
                sort=self.sort
                
            )
            results = Entrez.read(handle)
            handle.close()
            total_count = int(results.get("Count", 0))
            ids = results.get("IdList", [])
            print(f"Total results found: {total_count}")
            print(f"Retrieving top {min(len(ids), max_results)} articles...\n")

            if not ids:
                return []
            
            return self.fetch_details(ids)
        except Exception as e:

            msg = f"PMC search error: {e}"
            logger.error(msg)
            console.print("[red]Error searching via PMC")
            return []

    def fetch_details(self, ids):
        try:
            
            handle = Entrez.efetch(
                db="pmc",
                id=['11024426','10556456','8600326','9554590','6767062','10675300','11616947', '8079424', '11238906', '11558902', '11271534', '11822732', '11865484'],#",".join(ids),
                retmode="xml"
            )
            data = handle.read()
            handle.close()
            return self.parse_articles(data)
        except Exception as e:
            msg = f"Error fetching details via PMC: {e}"
            logger.error(msg)
            console.print("[red]Error fetching details via PMC")
            return []
        
    
    def parse_articles(self, xml_data):

        root = ET.fromstring(xml_data)
        articles = []
        for article in root.findall(".//article"):
            try:
                # Title
                
                title_elem = article.find(".//article-title")
                title = "".join(title_elem.itertext()) if title_elem is not None else "No title"
                

                # Abstract
                abstract_elem = article.find(".//abstract")
                if abstract_elem is  None:
                    msg = f"Skipping article '{title}' (no abstract)"
                    logger.error(msg)
                    console.print(f"[yellow]Warning: Skipping article '{title}' (no abstract)")
            
                    continue

                abstract = " ".join("".join(p.itertext()) for p in abstract_elem.findall(".//p"))
     

                # PMC ID
                pmc_elem = article.find(".//article-meta/article-id[@pub-id-type='pmcid']")

                pmc = pmc_elem.text if pmc_elem is not None else "Unknown"

                # First Author
                author = "Unknown"
                contrib = article.find(".//contrib-group/contrib[@contrib-type='author']")
                if contrib is not None:
                    surname = contrib.findtext(".//surname", default="")
                    given = contrib.findtext(".//given-names", default="")
                    author = f"{given} {surname}".strip()

                # Year
                year = "Unknown"
                pub_date = article.find(".//pub-date[@pub-type='epub']") or article.find(".//pub-date[@pub-type='ppub']")
                if pub_date is not None:
                    year_elem = pub_date.find("year")
                    if year_elem is not None:
                        year = year_elem.text

                # Journal
                journal_elem = article.find(".//journal-title")
                journal = journal_elem.text if journal_elem is not None else "Unknown"

                # Body
                body_elem = article.find(".//body")
                if body_elem is not None:
                    sections = []
                    for sec in body_elem.findall(".//sec"):
                        title_elem = sec.find("./title")
                        section_title = title_elem.text.strip() if title_elem is not None else "No section title"
                        
                        # Join all paragraph texts in the section
                        section_text = " ".join("".join(p.itertext()) for p in sec.findall(".//p"))
                        
                        # Add structured section to list
                        sections.append(f"{section_title}:\n{section_text}")
                    
                    # Combine all sections into one body string
                    body = "\n\n".join(sections)
                else:
                    body = None

                article_data = {
                    "pmc": pmc,
                    "first_author": author,
                    "year": year,
                    "journal": journal,
                    "url": f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc}/" if pmc != "Unknown" else "Unavailable",
                    "title": title,
                    "abstract": abstract,
                    "body": body
                    
                }

                articles.append(article_data)

            except Exception as e:
                msg = f"Failed to parse article: {e}"
                logger.error(msg)
                console.print(f"[red]Error: Failed to parse article")

        return articles


