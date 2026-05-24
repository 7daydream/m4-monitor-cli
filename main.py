import psutil
import platform
import time
import sys
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.live import Live

console = Console()

def get_system_status(last_net_in, last_net_out, last_time):
    """
    [변경 이유: 네트워크 속도 계산을 위해 과거 상태(이전 트래픽 값, 이전 측정 시간)를 인자로 전달받음]
    시스템 하드웨어 상태 정보 및 실시간 네트워크 I/O 속도를 계산하여 가져옵니다.
    """
    # 응답성을 위해 interval은 기존 감성(0.1초) 그대로 유지합니다.
    cpu_usage = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    
    # --- [추가] 실시간 네트워크 속도 계산 로직 ---
    net_io = psutil.net_io_counters()
    current_time = time.time()
    time_delta = current_time - last_time
    if time_delta == 0:  # 0 나누기 오류 방지
        time_delta = 1
        
    # (현재 누적 데이터 - 1초 전 누적 데이터) / 흐른 시간 / 1024 = KB/s 단위를 구해냅니다.
    net_in_speed = (net_io.bytes_recv - last_net_in) / time_delta / 1024
    net_out_speed = (net_io.bytes_sent - last_net_out) / time_delta / 1024
    # ----------------------------------------------
    
    return {
        "cpu": cpu_usage,
        "memory_percent": memory.percent,
        "memory_used": f"{memory.used / (1024**3):.2f}GB",
        "memory_total": f"{memory.total / (1024**3):.2f}GB",
        "disk_percent": disk.percent,
        "boot_time": boot_time,
        # 메인 루프에 그려질 가공된 속도 데이터 문자열
        "net_in": f"{net_in_speed:.1f} KB/s",
        "net_out": f"{net_out_speed:.1f} KB/s",
        # 다음 루프 때 '과거 데이터'로 쓰기 위해 원본 생 데이터도 함께 포장하여 리턴
        "raw_net_in": net_io.bytes_recv,
        "raw_net_out": net_io.bytes_sent,
        "raw_time": current_time
    }

def generate_table(status):
    """
    [변경 이유: 복잡한 UI 코드 오염을 막기 위해, 순수하게 데이터만 넘겨받아 표를 그리는 정석 분리 구조 유지]
    실시간으로 업데이트될 테이블을 생성합니다. 기존의 텍스트 프로그레스 바 스타일을 완벽히 계승합니다.
    """
    table = Table(title="💻 M4 Mini System Monitor", highlight=True)
    
    table.add_column("Category", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    table.add_column("Progress / Trend", width=20) # 네트워크 표현을 위해 컬럼명 소폭 확장

    # 1. CPU (기존 감성 유지)
    cpu_bar = "[green]" + "|" * int(status['cpu'] / 5) + "[/green]"
    table.add_row("CPU Usage", f"{status['cpu']}%", cpu_bar)

    # 2. Memory (기존 감성 유지)
    mem_bar = "[blue]" + "|" * int(status['memory_percent'] / 5) + "[/blue]"
    table.add_row("Memory", f"{status['memory_used']} / {status['memory_total']}", mem_bar)

    # 3. Disk (기존 감성 유지)
    disk_bar = "[yellow]" + "|" * int(status['disk_percent'] / 5) + "[/yellow]"
    table.add_row("Disk (Root)", f"{status['disk_percent']}%", disk_bar)
    
    # 4. Net Download (신규 고도화)
    # 다운로드 속도에 따라 동적으로 바가 늘어나는 UI 연출 (최대 10MB/s 기준)
    net_in_kb = float(status['net_in'].split()[0])
    net_in_bar = "[aquamarine1]" + "▶" * min(int(net_in_kb / 500), 20) + "[/aquamarine1]"
    table.add_row("Net Download", status['net_in'], net_in_bar)
    
    # 5. Net Upload (신규 고도화)
    net_out_kb = float(status['net_out'].split()[0])
    net_out_bar = "[orange1]" + "◀" * min(int(net_out_kb / 500), 20) + "[/orange1]"
    table.add_row("Net Upload", status['net_out'], net_out_bar)
    
    # 6. System Boot
    table.add_row("System Boot", status['boot_time'], "")
    
    return table

def main():
    console.print("[yellow]Starting Monitor... (Press Ctrl+C to stop)[/yellow]")
    
    # [변경 이유: 네트워크 속도를 구하기 위해, 프로그램이 켜진 최초 시점의 '기준 데이터'를 먼저 셋팅해 둡니다.]
    init_net = psutil.net_io_counters()
    last_in = init_net.bytes_recv
    last_out = init_net.bytes_sent
    last_time = time.time()
    
    # 첫 데이터를 즉시 가져와서 화면에 뿌립니다.
    status = get_system_status(last_in, last_out, last_time)
    
    with Live(generate_table(status), refresh_per_second=4) as live:
        try:
            while True:
                time.sleep(0.5)  # 0.5초마다 갱신
                
                # 1. 0.5초 전의 '과거 기록'들을 밀어 넣어 새로운 시스템 상태를 수집합니다.
                status = get_system_status(last_in, last_out, last_time)
                
                # 2. 다음 0.5초 뒤 루프를 위해, 이번 타이밍에 수집된 데이터를 새로운 '과거 기록'으로 갱신(백업)해 둡니다.
                last_in = status["raw_net_in"]
                last_out = status["raw_net_out"]
                last_time = status["raw_time"]
                
                # 3. 완벽하게 분리된 UI 함수에 데이터만 넘겨서 화면을 갱신합니다.
                live.update(generate_table(status))
                
        except KeyboardInterrupt:
            console.print("\n[bold red]Monitoring stopped by user.[/bold red]")

if __name__ == "__main__":
    main()