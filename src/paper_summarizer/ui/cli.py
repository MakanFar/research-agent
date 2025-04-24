import yaml
import os
import json
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from ..agents.summary_agent import SummaryAgent

class CLI:
    def __init__(self):
        self.console = Console()
        
    def load_config(self, config_path="config.yaml"):
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                
            required_keys = ['openai_api_key', 'papers_directory', 'output_directory']
            missing_keys = [key for key in required_keys if key not in config]
            
            if missing_keys:
                raise ValueError(f"Missing required configuration keys: {', '.join(missing_keys)}")
                
            if not os.path.exists(config['papers_directory']):
                raise ValueError(f"Papers directory not found: {config['papers_directory']}")
                
            return config
            
        except FileNotFoundError:
            raise Exception(f"Configuration file not found: {config_path}")
        except yaml.YAMLError as e:
            raise Exception(f"Error parsing configuration file: {str(e)}")
    
    def get_paper_paths(self, directory):
        """Get all PDF files from directory"""
        paper_paths = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.pdf'):
                    paper_paths.append(os.path.join(root, file))
        return paper_paths
    
    def display_results(self, results, output_dir):
        """Display results in a rich table and save to file"""
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
                str(result.get('publication_date', 'N/A')),
                str(result.get('ai_goal', 'N/A'))[:100],
                str(result.get('ml_algorithm', 'N/A'))[:50],
                str(result.get('data_type', 'N/A'))[:50],
                str(result.get('evaluation_metrics', 'N/A'))[:100]
            )
        
        # Display table in console
        self.console.print(table)
        
        # Save results to JSON file
        output_file = os.path.join(output_dir, "paper_summaries.json")
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        self.console.print(f"\n[green]Results saved to:")
        self.console.print(f"- JSON: {output_file}")
       
    
    def run(self, config_path="config.yaml"):
        """Main CLI execution"""
        try:
            # Load configuration
            config = self.load_config(config_path)
            
            # Initialize agent
            agent = SummaryAgent(config['openai_api_key'])
            
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
            
            # Create output directory if it doesn't exist
            os.makedirs(config['output_directory'], exist_ok=True)
            
            # Display and save results
            self.display_results(results, config['output_directory'])
            
        except Exception as e:
            self.console.print(f"[red]Error: {str(e)}")
