import yaml
import os
import json
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.progress import Progress
from ..agents.summary_agent import SummaryAgent
from ..retrievers.semantic_scholar import SemanticScholarSearch
# from ..retrievers.semantic_scholar import SemanticScholarSearch  # Uncomment and import your retriever

class CLI:
    def __init__(self):
        self.console = Console()

    def load_config(self, config_path="config.yaml"):
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

            required_keys = ['openai_api_key', 'papers_directory', 'output_directory']
            missing_keys = [key for key in required_keys if key not in config]

            if missing_keys:
                raise ValueError(f"Missing required configuration keys: {', '.join(missing_keys)}")

            return config

        except FileNotFoundError:
            raise Exception(f"Configuration file not found: {config_path}")
        except yaml.YAMLError as e:
            raise Exception(f"Error parsing configuration file: {str(e)}")

    def get_paper_paths(self, directory):
        paper_paths = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.pdf'):
                    file_path = os.path.abspath(os.path.join(root, file))
                    if os.path.isfile(file_path):
                        paper_paths.append(file_path)
                    else:
                        self.console.print(f"[yellow]Warning: File not accessible: {file_path}")

        if not paper_paths:
            self.console.print(f"[yellow]Warning: No PDF files found in {directory}")
        return paper_paths

    def display_results(self, results, output_dir):
        table = Table(title="Paper Summaries", show_lines=True)
        print(results)
        for result in results:
            if isinstance(result, dict) and 'error' not in result:
                columns = list(result.keys())
                break
        else:
            self.console.print("[red]No valid results to display.")
            return

        for col in columns:
            table.add_column(col.replace("_", " ").title(), overflow="fold")

        for result in results:
            if isinstance(result, dict) and 'error' in result:
                self.console.print(f"[red]Error processing {result['file']}: {result['error']}")
                continue
            row = [str(result.get(col, 'N/A'))[:100] for col in columns]
            table.add_row(*row)

        self.console.print(table)

        output_file = os.path.join(output_dir, "paper_summaries.json")
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        self.console.print(f"\n[green]Results saved to:\n- JSON: {output_file}")

    def retrieve_papers(self, query, sort, objective ,max_results=10, type="abstract"):
        """Stub for integrating actual paper retrieval logic"""
        test = [
            {
                'title': 'Machine Learning for Healthcare Radars: Recent Progresses in Human Vital Sign Measurement and Activity Recognition',
                'href': 'https://ieeexplore.ieee.org/ielx7/9739/5451756/10322785.pdf',
                'body': 'The unprecedented non-contact, non-invasive, and privacy-preserving nature of radar sensors has enabled various healthcare applications, including vital sign monitoring, fall detection, gait analysis, activity recognition, fitness evaluation, and sleep monitoring. Machine learning (ML) is revolutionizing every domain, with radar-based healthcare being no exception. Progress in the field of healthcare radars and ML is complementing the existing radar-based healthcare industry. This article provides an overview of ML usage for two major healthcare applications: vital sign monitoring and activity recognition. Vital sign monitoring is the most promising healthcare application of radar, as it can predict several chronic cardiac and respiratory diseases. Activity recognition is also a prominent application since the inability to perform activities may result in critical suffering. The article presents an overview of commercial radars, radar hardware, and historical progress of healthcare radars, followed by the usage of ML for healthcare radars. Subsequently, the paper discusses how ML can overcome the limitations of conventional radar data processing chains for healthcare radars. The article also touches upon recent generative ML concepts used in healthcare radars. Among several interesting findings, it was discovered that ML does not completely replace existing vital sign monitoring algorithms; rather, ML is deployed to overcome the limitations of traditional algorithms. On the other hand, activity recognition always relies on ML approaches. The most widely used algorithms for both applications are Convolutional Neural Network (CNN) followed by Support Vector Machine (SVM). Generative AI has the capability to augment data and is expected to have a significant impact soon. Recent trends, lessons learned from these trends, and future directions for both healthcare applications are presented in detail. Finally, the future work section discusses a wide range of healthcare topics for humans, ranging from neonates to elderly individuals.'
            },
            {
                'title': 'Machine Learning for Healthcare-IoT Security: A Review and Risk Mitigation',
                'href': 'https://ieeexplore.ieee.org/ielx7/6287639/6514899/10371310.pdf',
                'body': 'The Healthcare Internet-of-Things (H-IoT), commonly known as Digital Healthcare, is a data-driven infrastructure that highly relies on smart sensing devices (i.e., blood pressure monitors, temperature sensors, etc.) for faster response time, treatments, and diagnosis. However, with the evolving cyber threat landscape, IoT devices have become more vulnerable to the broader risk surface (e.g., risks associated with generative AI, 5G-IoT, etc.), which, if exploited, may lead to data breaches, unauthorized access, and lack of command and control and potential harm. This paper reviews the fundamentals of healthcare IoT, its privacy, and data security challenges associated with machine learning and H-IoT devices. The paper further emphasizes the importance of monitoring healthcare IoT layers such as perception, network, cloud, and application. Detecting and responding to anomalies involves various cyber-attacks and protocols such as Wi-Fi 6, Narrowband Internet of Things (NB-IoT), Bluetooth, ZigBee, LoRa, and 5G New Radio (5G NR). A robust authentication mechanism based on machine learning and deep learning techniques is required to protect and mitigate H-IoT devices from increasing cybersecurity vulnerabilities. Hence, in this review paper, security and privacy challenges and risk mitigation strategies for building resilience in H-IoT are explored and reported.'
            }
        ]
        config = self.load_config("config.yaml")                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
        agent = SummaryAgent(config['openai_api_key'], config['meta_data'],)
        with Progress() as progress:
                task = progress.add_task("[cyan]Analyzing papers...", total=len(test))
                results = agent.analyze_papers(test,type,objective)
                progress.update(task, advance=1)
        return results
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    

    def run(self, config_path="config.yaml"):
        try:
            config = self.load_config(config_path)
            choice = Prompt.ask("\nDo you want to [bold green]retrieve[/bold green] new papers or use [bold yellow]local[/bold yellow] PDFs?", choices=["search", "local"], default="local")

            if choice == "search":
                query = Prompt.ask("Enter your search query", default=None)
                sort = Prompt.ask("Sort by", choices=["relevance", "citation", "date"], default="relevance")
                objective = Prompt.ask("Enter your objective", default=None)

                results = self.retrieve_papers(query=query, sort=sort,objective=objective)
                

            else:# Fallback to local summarization logic
                agent = SummaryAgent(config['openai_api_key'], config['meta_data'])
                paper_paths = self.get_paper_paths(config['papers_directory'])

                if not paper_paths:
                    self.console.print("[red]No PDF files found in the specified directory!")
                    return

                with Progress() as progress:
                    task = progress.add_task("[cyan]Analyzing papers...", total=len(paper_paths))
                    results = agent.analyze_papers(paper_paths)
                    progress.update(task, advance=1)

            os.makedirs(config['output_directory'], exist_ok=True)
            self.display_results(results, config['output_directory'])

        except Exception as e:
            self.console.print(f"[red]Error: {str(e)}")