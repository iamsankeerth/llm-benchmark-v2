import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from src.ollama_client import OllamaClient
from config import CORE_MODELS

console = Console()

def main():
    client = OllamaClient()
    
    console.print(Panel("[bold green]Local AI Assistant CLI[/bold green]\nHardware: RTX 2050 4GB VRAM", expand=False))
    
    console.print("Available models:")
    for role, tag in CORE_MODELS.items():
        console.print(f"  [cyan]{role}[/cyan]: {tag}")
        
    print()
    role = input("Select role [chat, reasoning, coding]: ").strip().lower()
    
    if role not in CORE_MODELS:
        console.print("[bold red]Invalid role selected. Exiting.[/bold red]")
        return
        
    model_tag = CORE_MODELS[role]
    console.print(f"Loaded model: [bold yellow]{model_tag}[/bold yellow]\nType 'quit' to exit.")
    
    while True:
        prompt = input(f"\nUser > ")
        if prompt.lower() in ["quit", "exit"]:
            break
            
        with console.status("[bold blue]Generating...[/bold blue]"):
            result = client.generate_benchmark(model_tag, prompt)
            
        if result.error:
            console.print(f"[bold red]Error:[/bold red] {result.error}")
        else:
            console.print(Panel(Markdown(result.content), title="Assistant Response"))
            console.print(f"[dim]TPS: {result.tps:.2f} | TTFT: {result.ttft:.2f}s | Latency: {result.latency:.2f}s | Tokens: {result.eval_count}[/dim]")

if __name__ == "__main__":
    main()
