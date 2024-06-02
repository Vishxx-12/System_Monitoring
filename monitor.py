import psutil
import requests
import socket

def collect_stats():
    stats = {
        "hostname": socket.gethostname(),
        "cpu_usage": psutil.cpu_percent(interval=1),
        "ram": psutil.virtual_memory()._asdict(),
        "disk": {part.mountpoint: psutil.disk_usage(part.mountpoint)._asdict() for part in psutil.disk_partitions()},
        "network": psutil.net_io_counters()._asdict(),
        "uptime": psutil.boot_time(),
        "power": psutil.sensors_battery()._asdict() if psutil.sensors_battery() else None
    }
    return stats

def send_stats(url, stats):
    try:
        response = requests.post(url, json=stats)
        if response.status_code != 200:
            print(f"Failed to send data: {response.text}")
    except Exception as e:
        print(f"Error sending data: {e}")

if __name__ == "__main__":
    url = "http://localhost:5000/collect"
    stats = collect_stats()
    send_stats(url, stats)
