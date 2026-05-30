import time
import psutil
from rich.console import Console
from rich.live import Live

# 우리가 새로 만든 모듈에서 함수를 쏙쏙 뽑아옵니다.
from metrics import get_system_status
from ui import generate_table

console = Console()

def main():
    console.print("[yellow]Starting Monitor... (Press Ctrl+C to stop)[/yellow]")
    
    init_net = psutil.net_io_counters()
    last_in = init_net.bytes_recv
    last_out = init_net.bytes_sent
    last_time = time.time()
    
    # metrics 모듈에서 데이터 가져오기
    status = get_system_status(last_in, last_out, last_time)
    
    # ui 모듈에서 만든 테이블로 실시간 화면 그리기
    with Live(generate_table(status), refresh_per_second=4) as live:
        try:
            while True:
                time.sleep(0.5)  
                
                status = get_system_status(last_in, last_out, last_time)
                
                last_in = status["raw_net_in"]
                last_out = status["raw_net_out"]
                last_time = status["raw_time"]
                
                live.update(generate_table(status))
                
        except KeyboardInterrupt:
            console.print("\n[bold red]Monitoring stopped by user.[/bold red]")

if __name__ == "__main__":
    main()