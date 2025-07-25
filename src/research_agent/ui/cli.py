import typer 
import os
import json
import asyncio
import time
from rich.console import Console
from rich.prompt import Prompt
from rich import print

from ..agents.summary_agent import SummaryAgent
from ..retrievers.pubmed_central import PubMedCentralSearch
from ..utils.enums import Database, SortOrder, Task
from ..logger.logger import Logger
from ..config.config import config
from ..utils.paper_processor import convert2doc

# Initialize logger
logger = Logger().get_logger()
log_timer = Logger().log_execution_time

# Create Typer app
app = typer.Typer(
    name="papers-cli",
    help="A CLI to retrieve and analyze research papers.",
    add_completion=True,
    no_args_is_help=True
)

console = Console()
config = config.load_config("config.yaml")

@log_timer
def get_paper_paths(directory: str):
    paper_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".pdf"):
                file_path = os.path.abspath(os.path.join(root, file))
                if os.path.isfile(file_path):
                    paper_paths.append(file_path)
                else:
                    msg = f"File not accessible: {file_path}"
                    logger.warning(msg)
                    console.print(f"[yellow]Warning: {msg}")

    if not paper_paths:
        msg = f"No PDF files found in {directory}"
        logger.warning(msg)
        console.print(f"[yellow]Warning: {msg}")
    return paper_paths

@log_timer
def fetch_online(query, sort, max_results, database):
    if database == Database.pubmed:
        papers = PubMedCentralSearch(query, sort, max_results).search()
    else:
        msg = f"Currently only PubMed Central is supported"
        logger.error(msg)
        console.print(f"[bold red]Warning: {msg}")
        raise typer.Exit()

    if not papers:
        msg = "No papers found!"
        logger.error(msg)
        console.print(f"[bold red]{msg}")
        raise typer.Exit()

    articles = convert2doc(papers)
    return articles

@log_timer
def save_results(results, output_dir, _type):
    if isinstance(results, dict):
        results = [results]

    if _type == "filter":
        output_file = os.path.join(output_dir, "paper_screenings.json")
    else:
        output_file = os.path.join(output_dir, "paper_summaries.json")

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    logger.info(f"Results saved to {output_file}")
    console.print(f"\n[green]Results saved to:\n- JSON: {output_file}")

@app.command()
def analyze(
    task: Task = typer.Option(Task.meta,prompt=True, help="Type of review: 'meta' for meta-analysis, 'systematic' for systematic review"),
    #Source: Fetch = typer.Option(Fetch.online,prompt=True, help="Method to retrive papers [online|local]"),
    filter_papers: bool = typer.Option(True,help="Filter papers before analysis"),
    output_dir: str = typer.Option("./output", help="Directory to save results"),
    database: Database = typer.Option(Database.pubmed, help="Database to search [pubmed centeral|semantic]"),
    query: str = typer.Option(None, help="Search query"),
    objective: str = typer.Option(None, help="objective for abstract and title screening"),
    sort: SortOrder = typer.Option(SortOrder.relevance,help="Sort order [relevance|citatio,n|date]"),
    #directory: str = typer.Argument(None, help="Directory containing PDF files"),
    max_results: int = typer.Option(1000, help="Maximum number of papers to retrieve")
    ):
    """
    Retrieve papers online and perform analysis.
    """
    api_key = os.environ.get("OPENAI_API_KEY",config["OPENAI_API_KEY"])

    agent = SummaryAgent(api_key, config["meta_data"])

    console.print(f"[cyan]Retrieving papers from {database}...[/cyan]")
    

    _query = config.get("search_query",query)

    if not _query:
        _query = Prompt.ask("Enter your search query")

    logger.info(f"Querying database: {database} with query: {query}")

    articles = fetch_online(_query, sort, max_results, database)

    if filter_papers:
        console.print("[cyan]Screening papers...[/cyan]")
        if not objective:
            objective = Prompt.ask("Enter your objective for screening")

        filtered_results, filtered_articles = asyncio.run(agent.filter_papers(articles, objective))
        logger.info(f"Screened {len(filtered_articles)} articles.")
        console.print(f"[green]Screening complete.")

        os.makedirs(output_dir, exist_ok=True)
        save_results(filtered_results, output_dir, "filter")
    else:
        filtered_articles = articles

    if task == Task.meta:
        console.print("[green]Performing meta-analysis...[/green]")
        summary_results = asyncio.run(agent.meta_analysis(filtered_articles))
        logger.info(f"Meta-analysis complete.")
        console.print(f"[green]Meta-analysis complete.")

    elif task == Task.systematic:
        console.print("[green]Performing systematic review...[/green]")
        summary_results = asyncio.run(agent.systematic_review(filtered_articles))
        logger.info(f"Systematic review complete.")
        console.print(f"[green]Systematic review complete.")

    save_results(summary_results, output_dir, "summary")
