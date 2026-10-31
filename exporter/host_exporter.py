import os
import re
import time
import psutil
from prometheus_client import start_http_server, Gauge

PORT = int(os.environ.get("HOST_EXPORTER_PORT", "9105"))
INTERVAL = int(os.environ.get("HOST_EXPORTER_INTERVAL", "5"))

CPU_PERCENT = Gauge("host_cpu_percent", "Host CPU utilization percentage")
MEM_PERCENT = Gauge("host_memory_percent", "Host Memory utilization percentage")
MEM_USED_BYTES = Gauge("host_memory_used_bytes", "Host Memory used bytes")
MEM_TOTAL_BYTES = Gauge("host_memory_total_bytes", "Host Memory total bytes")
DISK_PERCENT = Gauge("host_disk_percent", "Host Root Disk utilization percentage")
DISK_USED_BYTES = Gauge("host_disk_used_bytes", "Host Root Disk used bytes")
DISK_TOTAL_BYTES = Gauge("host_disk_total_bytes", "Host Root Disk total bytes")
NET_SENT_BYTES = Gauge("host_network_sent_bytes_total", "Host Network bytes sent total")
NET_RECV_BYTES = Gauge("host_network_recv_bytes_total", "Host Network bytes recv total")

def collect():
    CPU_PERCENT.set(psutil.cpu_percent(interval=None))
    vm = psutil.virtual_memory()
    MEM_PERCENT.set(vm.percent)
    MEM_USED_BYTES.set(vm.used)
    MEM_TOTAL_BYTES.set(vm.total)
    
    du = psutil.disk_usage("/")
    DISK_PERCENT.set(du.percent)
    DISK_USED_BYTES.set(du.used)
    DISK_TOTAL_BYTES.set(du.total)
    
    net = psutil.net_io_counters()
    NET_SENT_BYTES.set(net.bytes_sent)
    NET_RECV_BYTES.set(net.bytes_recv)

def main():
    print(f"Starting Host Metrics Exporter on port {PORT}...")
    start_http_server(PORT)
    # Prime cpu_percent
    psutil.cpu_percent(interval=None)
    while True:
        try:
            collect()
        except Exception:
            pass
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
