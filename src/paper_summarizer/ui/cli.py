import yaml
import os
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from ..agents.paper_agent import PaperAgent

class CLI:
    def __init__(self):
        self.console = Console()
        
    def load_config(self, config_path="config.yaml"):
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def get_paper_paths(self, directory):
        """Get all PDF files from directory"""
        paper_paths = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.pdf'):
                    paper_paths.append(os.path.join(root, file))
        return paper_paths
    
    def display_results(self, results):
        """Display results in a rich table"""
        table = Table(title="Paper Summaries")
        
        # Add columns
        table.add_column("Title", style="cyan")
        table.add_column("First Author", style="green")
        table.add_column("Journal", style="yellow")
        table.add_column("AI Goal", style="magenta")
        table.add_column("ML Algorithm", style="blue")
        
        # Add rows
        for result in results:
            table.add_row(
                result.get('title', 'N/A'),
                result.get('first_author', 'N/A'),
                result.get('journal', 'N/A'),
                result.get('ai_goal', 'N/A'),
                result.get('ml_algorithm', 'N/A')
            )
        
        self.console.print(table)
    
    def run(self, config_path="config.yaml"):
        """Main CLI execution"""
        try:
            # Load configuration
            config = self.load_config(config_path)
            
            # Initialize agent
            agent = PaperAgent(config['openai_api_key'])
            
            # Get paper paths
            paper_paths = self.get_paper_paths(config['papers_directory'])
            
            if not paper_paths:
                self.console.print("[red]No PDF files found in the specified directory!")
                return
            
            # Process papers with progress bar
            with Progress() as progress:
                task = progress.add_task("[cyan]Analyzing papers...", total=len(paper_paths))
                results = agent.analyze_papers(paper_paths)
                progress.update(task, advance=1)
            
            # Display results
            self.display_results(results)
            
        except Exception as e:
            self.console.print(f"[red]Error: {str(e)}")
