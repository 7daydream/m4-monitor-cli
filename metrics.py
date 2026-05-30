import psutil
import time
from datetime import datetime

def get_top_processes():
    """지금 CPU를 가장 많이 사용 중인 프로세스 상위 5개를 가져옵니다."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            cpu = proc.info['cpu_percent']
            mem = proc.info['memory_percent']
            if cpu is not None and mem is not None:
                if cpu > 0: 
                    processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    top_5 = sorted(processes, key=lambda x: x.get('cpu_percent') or 0.0, reverse=True)[:5]
    return top_5

def get_system_status(last_net_in, last_net_out, last_time):
    """시스템 하드웨어 상태 정보 및 실시간 네트워크 I/O 속도, TOP 5 프로세스를 가져옵니다."""
    cpu_usage = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    
    net_io = psutil.net_io_counters()
    current_time = time.time()
    time_delta = current_time - last_time
    if time_delta == 0:  
        time_delta = 1
        
    net_in_speed = (net_io.bytes_recv - last_net_in) / time_delta / 1024
    net_out_speed = (net_io.bytes_sent - last_net_out) / time_delta / 1024
    
    top_proc = get_top_processes()
    
    return {
        "cpu": cpu_usage,
        "memory_percent": memory.percent,
        "memory_used": f"{memory.used / (1024**3):.2f}GB",
        "memory_total": f"{memory.total / (1024**3):.2f}GB",
        "disk_percent": disk.percent,
        "boot_time": boot_time,
        "net_in": f"{net_in_speed:.1f} KB/s",
        "net_out": f"{net_out_speed:.1f} KB/s",
        "top_processes": top_proc,
        "raw_net_in": net_io.bytes_recv,
        "raw_net_out": net_io.bytes_sent,
        "raw_time": current_time
    }