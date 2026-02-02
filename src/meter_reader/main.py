import typer
import json
import logging
from rich.console import Console
from rich.table import Table
from datetime import datetime
from typing import Optional, List, Any

from .clients import SocketClient, HttpClient
from .models import DeviceList, InstantaneousDemand, UsageData

app = typer.Typer(no_args_is_help=True)
console = Console()

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def get_client(address: str, protocol: str, username: Optional[str] = None, password: Optional[str] = None) -> Any:
    if protocol == 'socket':
        return SocketClient(address)
    elif protocol == 'http':
        if not username or not password:
            console.print("[red]Username and password required for HTTP protocol[/red]")
            raise typer.Exit(code=1)
        return HttpClient(address, username, password)
    else:
        console.print(f"[red]Invalid protocol: {protocol}[/red]")
        raise typer.Exit(code=1)

@app.command()
def list(
    address: str, 
    protocol: str = typer.Option("socket", help="Protocol: socket or http"),
    username: str = typer.Option(None, help="Username for HTTP"),
    password: str = typer.Option(None, help="Password for HTTP"),
    raw: bool = typer.Option(False, help="Show raw output")
):
    """List devices on gateway."""
    client = get_client(address, protocol, username, password)
    try:
        devices = client.list_devices()
        if raw:
            console.print_json(devices.model_dump_json(by_alias=True))
        else:
            table = Table(title="Connected Devices")
            table.add_column("MAC ID", style="cyan")
            table.add_column("Model", style="magenta")
            table.add_column("FW Version", style="green")
            table.add_column("HW Version", style="yellow")
            table.add_column("Manufacturer", style="blue")
            
            for d in devices.device_info:
                table.add_row(
                    d.device_mac_id, 
                    d.model_id or "Unknown",
                    d.fw_version or "N/A",
                    d.hw_version or "N/A",
                    d.manufacturer or "Unknown"
                )
            console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)

@app.command()
def demand(
    address: str,
    protocol: str = typer.Option("socket", help="Protocol: socket or http"),
    username: str = typer.Option(None, help="Username for HTTP"),
    password: str = typer.Option(None, help="Password for HTTP"),
    raw: bool = typer.Option(False, help="Show raw JSON")
):
    """Get instantaneous demand."""
    client = get_client(address, protocol, username, password)
    try:
        data = client.get_instantaneous_demand()
        if raw:
            console.print_json(data.model_dump_json(by_alias=True))
        else:
            console.print(f"Timestamp: [green]{data.timestamp}[/green]")
            console.print(f"Demand: [bold]{data.panic_demand:.3f} kW[/bold]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)

@app.command()
def summation(
    address: str,
    protocol: str = typer.Option("socket", help="Protocol: socket or http"),
    username: str = typer.Option(None, help="Username for HTTP"),
    password: str = typer.Option(None, help="Password for HTTP"),
    raw: bool = typer.Option(False, help="Show raw JSON")
):
    """Get summation values."""
    client = get_client(address, protocol, username, password)
    try:
        data = client.get_current_summation()
        if raw:
            console.print_json(data.model_dump_json(by_alias=True))
        else:
            console.print(f"Timestamp: [green]{data.timestamp}[/green]")
            console.print(f"Delivered: [bold]{data.delivered_kwh:.3f} kWh[/bold]")
            console.print(f"Received: [bold]{data.received_kwh:.3f} kWh[/bold]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)

@app.command()
def usage(
    address: str,
    protocol: str = typer.Option("socket", help="Protocol: socket or http"),
    username: str = typer.Option(None, help="Username for HTTP"),
    password: str = typer.Option(None, help="Password for HTTP"),
    raw: bool = typer.Option(False, help="Show raw JSON")
):
    """Get usage summary (Demand + Summation)."""
    client = get_client(address, protocol, username, password)
    try:
        data = client.get_usage_data()
        if raw:
            console.print_json(data.model_dump_json(by_alias=True))
        else:
            table = Table(title="Usage Data")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")
            
            table.add_row("Timestamp", str(data.timestamp))
            table.add_row("Demand", f"{data.demand} {data.demand_units}")
            table.add_row("Delivered", f"{data.summation_delivered} {data.summation_units}")
            table.add_row("Received", f"{data.summation_received} {data.summation_units}")
            table.add_row("Status", data.meter_status)
            console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)

@app.command()
def history(
    address: str,
    hours: int = typer.Option(1, help="Number of hours to look back"),
    protocol: str = typer.Option("socket", help="Protocol: socket or http"),
    username: str = typer.Option(None, help="Username for HTTP"),
    password: str = typer.Option(None, help="Password for HTTP"),
    raw: bool = typer.Option(False, help="Show raw JSON"),
):
    """Get historical summation data over time."""
    from datetime import datetime, timedelta, timezone
    
    if protocol != "socket":
        console.print("[red]History command only supports socket protocol[/red]")
        raise typer.Exit(code=1)
    
    client = get_client(address, protocol, username, password)
    try:
        start = datetime.now(timezone.utc) - timedelta(hours=hours)
        end = datetime.now(timezone.utc)
        data = client.get_history_data(start_time=start, end_time=end)
        
        if raw:
            import json
            console.print_json(json.dumps([d.model_dump(by_alias=True) for d in data], default=str))
        else:
            if not data:
                console.print("[yellow]No historical data available for this time range[/yellow]")
                return
                
            table = Table(title=f"Historical Data (Last {hours} hour{'s' if hours != 1 else ''})")
            table.add_column("Timestamp", style="cyan")
            table.add_column("Delivered (kWh)", style="green", justify="right")
            table.add_column("Received (kWh)", style="magenta", justify="right")
            
            for d in data:
                table.add_row(
                    str(d.timestamp),
                    f"{d.delivered_kwh:.3f}",
                    f"{d.received_kwh:.3f}"
                )
            console.print(table)
            console.print(f"\n[dim]Total readings: {len(data)}[/dim]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)

@app.command()
def watch(
    address: str,
    interval: int = typer.Option(5, help="Update interval in seconds"),
    protocol: str = typer.Option("socket", help="Protocol: socket or http"),
    username: str = typer.Option(None, help="Username for HTTP"),
    password: str = typer.Option(None, help="Password for HTTP"),
    mode: str = typer.Option("usage", help="What to watch: demand, summation, or usage"),
):
    """Continuously monitor demand/summation values (Ctrl+C to stop)."""
    import time
    from rich.live import Live
    from rich.panel import Panel
    
    client = get_client(address, protocol, username, password)
    
    def generate_display():
        """Generate the display content based on mode."""
        try:
            if mode == "demand":
                data = client.get_instantaneous_demand()
                return f"[green]Timestamp:[/green] {data.timestamp}\n[bold cyan]Demand:[/bold cyan] {data.panic_demand:.3f} kW"
            elif mode == "summation":
                data = client.get_current_summation()
                return f"[green]Timestamp:[/green] {data.timestamp}\n[bold cyan]Delivered:[/bold cyan] {data.delivered_kwh:.3f} kWh\n[bold magenta]Received:[/bold magenta] {data.received_kwh:.3f} kWh"
            else:  # usage
                data = client.get_usage_data()
                table = Table(show_header=False, box=None, padding=(0, 1))
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="bold")
                table.add_row("Timestamp", str(data.timestamp))
                table.add_row("Demand", f"{data.demand} {data.demand_units}")
                table.add_row("Delivered", f"{data.summation_delivered} {data.summation_units}")
                table.add_row("Received", f"{data.summation_received} {data.summation_units}")
                table.add_row("Status", data.meter_status)
                return table
        except Exception as e:
            return f"[red]Error: {e}[/red]"
    
    console.print(f"[green]Watching {mode} every {interval} seconds... (Press Ctrl+C to stop)[/green]\n")
    
    try:
        with Live(Panel(generate_display(), title=f"Live {mode.capitalize()} Monitor"), refresh_per_second=1) as live:
            while True:
                live.update(Panel(generate_display(), title=f"Live {mode.capitalize()} Monitor"))
                time.sleep(interval)
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopped monitoring[/yellow]")

if __name__ == "__main__":
    app()

