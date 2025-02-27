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
        table = Table(title="Paper Summaries", show_lines=True)
        
        # Add columns for key information
        columns = [
            ("Title", "cyan"),
            ("First Author", "green"),
            ("Journal", "yellow"),
            ("Publication Date", "blue"),
            ("AI Goal", "magenta"),
            ("ML Algorithm", "blue"),
            ("Data Type", "yellow"),
            ("Evaluation Metrics", "green")
        ]
        
        for col_name, style in columns:
            table.add_column(col_name, style=style, overflow="fold")
        
        # Add rows
        for result in results:
            if isinstance(result, dict) and 'error' in result:
                # Handle error cases
                self.console.print(f"[red]Error processing {result['file']}: {result['error']}")
                continue
                
            table.add_row(
                str(result.get('title', 'N/A'))[:100],
                str(result.get('first_author', 'N/A'))[:50],
                str(result.get('journal', 'N/A'))[:50],
                str(result.get('publication_date', 'N/A')),
                str(result.get('ai_goal', 'N/A'))[:100],
                str(result.get('ml_algorithm', 'N/A'))[:50],
                str(result.get('data_type', 'N/A'))[:50],
                str(result.get('evaluation_metrics', 'N/A'))[:100]
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
