import yaml
import os
import json
import time
import sys
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.panel import Panel
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
                    # Get the absolute path to ensure it's a valid file path
                    file_path = os.path.abspath(os.path.join(root, file))
                    # Verify the file exists and is accessible
                    if os.path.isfile(file_path):
                        paper_paths.append(file_path)
                    else:
                        self.console.print(f"[yellow]Warning: File not accessible: {file_path}")
        
        if not paper_paths:
            self.console.print(f"[yellow]Warning: No PDF files found in {directory}")
            
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
                str(result.get('journal', 'N/A')),
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
                
                # Add a delay between processing papers to avoid rate limits
                self.console.print("[yellow]Note: Processing papers with delay to avoid rate limits...")
                results = []
                
                for i, path in enumerate(paper_paths):
                    try:
                        # Process one paper at a time
                        self.console.print(f"[cyan]Processing paper {i+1}/{len(paper_paths)}: {os.path.basename(path)}")
                        paper_result = agent.analyze_papers([path])
                        results.extend(paper_result)
                        
                        # Add a delay between papers to avoid rate limits
                        if i < len(paper_paths) - 1:
                            delay = 5  # Increased to 5 seconds between papers
                            self.console.print(f"[yellow]Waiting {delay} seconds before next paper...")
                            time.sleep(delay)
                    except Exception as e:
                        error_msg = str(e)
                        self.console.print(f"[red]Error processing {os.path.basename(path)}: {error_msg}")
                        
                        # Check for quota exceeded error
                        if "quota exceeded" in error_msg.lower() or "insufficient_quota" in error_msg.lower():
                            self.console.print(Panel(
                                "[bold red]OpenAI API quota exceeded![/bold red]\n\n"
                                "Your OpenAI API account has run out of credits or hit your maximum monthly spend limit.\n\n"
                                "To fix this issue:\n"
                                "1. Visit https://platform.openai.com/account/billing\n"
                                "2. Add credits or update your payment method\n"
                                "3. Check your usage limits at https://platform.openai.com/account/limits",
                                title="API Quota Error",
                                border_style="red"
                            ))
                            # Exit the program since we can't continue without API credits
                            self.console.print("[yellow]Exiting program due to API quota limitations.")
                            sys.exit(1)
                            
                        # Add error to results
                        results.append({
                            'file': path,
                            'error': error_msg
                        })
                    finally:
                        progress.update(task, advance=1)
            
            # Create output directory if it doesn't exist
            os.makedirs(config['output_directory'], exist_ok=True)
            
            # Display and save results
            self.display_results(results, config['output_directory'])
            
        except Exception as e:
            error_msg = str(e)
            self.console.print(f"[red]Error: {error_msg}")
            
            # Check for quota exceeded error at the top level
            if "quota exceeded" in error_msg.lower() or "insufficient_quota" in error_msg.lower():
                self.console.print(Panel(
                    "[bold red]OpenAI API quota exceeded![/bold red]\n\n"
                    "Your OpenAI API account has run out of credits or hit your maximum monthly spend limit.\n\n"
                    "To fix this issue:\n"
                    "1. Visit https://platform.openai.com/account/billing\n"
                    "2. Add credits or update your payment method\n"
                    "3. Check your usage limits at https://platform.openai.com/account/limits",
                    title="API Quota Error",
                    border_style="red"
                ))
