import os
import glob
import pandas as pd
from rich.console import Console
from config import REPORTS_DIR, RESULTS_DIR

console = Console()

class ModelComparator:
    def __init__(self):
        os.makedirs(REPORTS_DIR, exist_ok=True)
        self.report_path = os.path.join(REPORTS_DIR, "model_comparison_report.md")

    def run_offline_report(self):
        """
        Phase 3: Assembles the report from scattered CSVs left by the Ephemeral Loop.
        """
        console.print("[bold yellow]Generating Offline Model Comparison Report...[/bold yellow]")
        
        csv_files = glob.glob(os.path.join(RESULTS_DIR, "phase1", "*.csv"))
        if not csv_files:
            console.print("[red]No Phase 1 CSV records found! Run benchmarks first.[/red]")
            return
            
        dfs = []
        for file in csv_files:
            try:
                df = pd.read_csv(file)
                dfs.append(df)
            except Exception as e:
                console.print(f"[red]Error reading {file}: {e}[/red]")
                
        if not dfs:
            return
            
        combined_df = pd.concat(dfs, ignore_index=True)
        
        # Aggregate performance metrics
        summary = combined_df.groupby('model').agg({
            'tps': 'mean',
            'ttft': 'mean',
            'latency': 'mean',
            'peak_vram_mb': 'max'
        }).reset_index()

        with open(self.report_path, "w") as f:
            f.write("# Final Model Mega-Comparison Report\n\n")
            f.write(f"Generated natively on RTX 2050 (4GB VRAM) evaluating {len(summary)} distinct models.\n\n")
            
            f.write("## 1. Executive Setup\n")
            f.write("Models were gracefully handled using an Ephemeral loop (`ollama pull` -> `Test` -> `ollama rm`) resolving disk threshold bottlenecks natively.\n\n")
            
            f.write("## 2. Global Performance Metrics\n")
            f.write(summary.round(2).to_markdown(index=False))
            f.write("\n\n")
            
            # Category Breakdown
            f.write("## 3. Average TPS by Category\n")
            try:
                cat_summary = combined_df.pivot_table(values='tps', index='model', columns='category', aggfunc='mean')
                f.write(cat_summary.round(2).to_markdown())
            except Exception:
                f.write("Insufficient variance to calculate pivot table.\n")
            f.write("\n\n")
            
            f.write("## 4. Analysis & Conclusion\n")
            f.write("For an exact breakdown matching JSON validity via Python parsing, review the generated artifacts inside `results/phase2` locally. Dashboard integration scales dynamically.\n")

        # Step 4: Export JSON for dashboard dynamic fetching
        dashboard_data = {
            "summary": summary.to_dict(orient="records"),
            "category_summary": cat_summary.to_dict() if 'cat_summary' in locals() else {}
        }
        import json
        with open(os.path.join(REPORTS_DIR, "dashboard_data.json"), "w") as json_file:
            json.dump(dashboard_data, json_file, indent=2)

        console.print(f"[bold green]Report exported to {self.report_path}[/bold green]")
        console.print(f"[bold cyan]Dashboard Data exported to {os.path.join(REPORTS_DIR, 'dashboard_data.json')}[/bold cyan]")
