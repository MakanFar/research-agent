from ..config.default_vars import DEFAULT_CONFIG
import yaml
from typing import Dict, Any
from ..logger.logger import Logger
from rich.console import Console
import typer

console = Console()
# Initialize logger
logger = Logger().get_logger()

class config:
    def __init__(self):
        pass

    @classmethod
    def load_config(cls, config_path: str | None) -> Dict[str, Any]:
        try:
            if config_path is None:
                return DEFAULT_CONFIG
            
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

            required_keys = ['OPENAI_API_KEY', 'NCBI_API_KEY']
            missing_keys = [key for key in required_keys if key not in config]

            if missing_keys:
                msg = f"Missing required configuration keys: {', '.join(missing_keys)}"
                logger.error(msg)
                console.print("[yellow]Warning: "+msg)
                #raise typer.Exit(code=1)

            return config

        except FileNotFoundError:
            msg = f"Configuration file not found: {config_path}"
            logger.error(msg)
            console.print(f"[bold red]Error:{msg}[/bold red]")

            raise typer.Exit(code=1)
        
        except yaml.YAMLError as e:
            msg = f"Error parsing configuration file: {str(e)}"
            logger.exception(msg)
            console.print(f"[bold red]Error parsig configuration file")
            
            raise typer.Exit(code=1)

