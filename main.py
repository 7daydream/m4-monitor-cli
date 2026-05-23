import psutil
import platform
import time
import sys
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.live import Live

console = Console()

def get_system_status():
    """시스템 하드웨어 상태 정보를 가져옵니다."""
    # interval을 0.1로 줄여서 응답성을 높입니다.
    cpu_usage = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "cpu": cpu_usage,
        "memory_percent": memory.percent,
        "memory_used": f"{memory.used / (1024**3):.2f}GB",
        "memory_total": f"{memory.total / (1024**3):.2f}GB",
        "disk_percent": disk.percent,
        "boot_time": boot_time
    }

def generate_table(status):
    """실시간으로 업데이트될 테이블을 생성합니다."""
    table = Table(title="💻 M4 Mini System Monitor", highlight=True)
    
    table.add_column("Category", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    table.add_column("Progress", width=20)

    # CPU
    cpu_bar = "[green]" + "|" * int(status['cpu'] / 5) + "[/green]"
    table.add_row("CPU Usage", f"{status['cpu']}%", cpu_bar)

    # Memory
    mem_bar = "[blue]" + "|" * int(status['memory_percent'] / 5) + "[/blue]"
    table.add_row("Memory", f"{status['memory_used']} / {status['memory_total']}", mem_bar)

    # Disk
    disk_bar = "[yellow]" + "|" * int(status['disk_percent'] / 5) + "[/yellow]"
    table.add_row("Disk (Root)", f"{status['disk_percent']}%", disk_bar)
    
    table.add_row("System Boot", status['boot_time'], "")
    
    return table

def main():
    console.print("[yellow]Starting Monitor... (Press Ctrl+C to stop)[/yellow]")
    
    # 첫 데이터를 즉시 가져와서 화면에 뿌립니다.
    status = get_system_status()
    with Live(generate_table(status), refresh_per_second=4) as live:
        try:
            while True:
                time.sleep(0.5)  # 0.5초마다 갱신
                live.update(generate_table(get_system_status()))
        except KeyboardInterrupt:
            console.print("\n[bold red]Monitoring stopped by user.[/bold red]")

if __name__ == "__main__":
    main()