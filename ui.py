from rich.table import Table

def generate_table(status):
    """순수하게 데이터만 넘겨받아 종합 모니터링 표를 그립니다."""
    table = Table(title="💻 M4 Mini Comprehensive Monitor", highlight=True)
    
    table.add_column("Category", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    table.add_column("Progress / Trend", width=25)

    # 1. CPU
    cpu_bar = "[green]" + "|" * int(status['cpu'] / 5) + "[/green]"
    table.add_row("CPU Usage", f"{status['cpu']}%", cpu_bar)

    # 2. Memory
    mem_bar = "[blue]" + "|" * int(status['memory_percent'] / 5) + "[/blue]"
    table.add_row("Memory", f"{status['memory_used']} / {status['memory_total']}", mem_bar)

    # 3. Disk
    disk_bar = "[yellow]" + "|" * int(status['disk_percent'] / 5) + "[/yellow]"
    table.add_row("Disk (Root)", f"{status['disk_percent']}%", disk_bar)
    
    # 4. Net Download
    net_in_kb = float(status['net_in'].split()[0])
    net_in_bar = "[aquamarine1]" + "▶" * min(int(net_in_kb / 500), 20) + "[/aquamarine1]"
    table.add_row("Net Download", status['net_in'], net_in_bar)
    
    # [신규 추가] 총 다운로드 누적량 표시
    table.add_row(" └ Total Rx", status['total_in'], "", style="dim")

    # 5. Net Upload (실시간 속도)
    net_out_kb = float(status['net_out'].split()[0])
    net_out_bar = "[orange1]" + "◀" * min(int(net_out_kb / 500), 20) + "[/orange1]"
    table.add_row("Net Upload", status['net_out'], net_out_bar)

    # [신규 추가] 총 업로드 누적량 표시
    table.add_row(" └ Total Tx", status['total_out'], "", style="dim")

    # 6. System Boot
    table.add_row("System Boot", status['boot_time'], "")

    # 하단 빌런 프로세스 TOP 5 서브 테이블
    table.add_row("", "", "") 
    table.add_row("[bold red]🔥 Top 5 CPU Processes[/bold red]", "[bold]PID[/bold]", "[bold]CPU% (MEM%)[/bold]")    
    
    for proc in status['top_processes']:
        raw_name = proc.get('name') or "Unknown"
        proc_name = raw_name[:18] 
        table.add_row(
            f" └ {proc_name}", 
            f"{proc['pid']}", 
            f"[red]{proc['cpu_percent']:.1f}%[/red] ({proc['memory_percent']:.1f}%)"
        )

    return table