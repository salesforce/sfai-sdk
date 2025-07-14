import typer
import webbrowser
import time
import subprocess
import requests
import re
import threading
from typing import Optional
from rich.console import Console
from rich.status import Status
from sfai.app.open import open
from sfai.constants import (
    ERROR_EMOJI,
    SUCCESS_EMOJI,
    PORT_EMOJI,
    UPDATE_EMOJI,
    WEB_EMOJI,
    LINK_EMOJI,
    TUNNEL_EMOJI,
    LIGHT_BULB_EMOJI,
)
from sfai.platform.switch import switch

app = typer.Typer()
console = Console()

MAX_RETRIES = 10
RETRY_DELAY = 2


def start_cloudflare_tunnel(port: int, path: str) -> tuple[str, subprocess.Popen]:
    """
    Start a Cloudflare tunnel for a service.

    Args:
        port: int
            The port to forward
        path: str
            The path to open
    Returns:
        tuple[str, subprocess.Popen]
    """
    proc = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    url_holder = {"url": None}

    def parse():
        for line in iter(proc.stdout.readline, ""):
            match = re.search(r"https://[^\s]+\.trycloudflare\.com", line)
            if match:
                candidate = match.group(0).rstrip("/") + path
                try:
                    if requests.get(candidate, timeout=5).status_code == 200:
                        url_holder["url"] = candidate
                        break
                except requests.RequestException:
                    continue

    threading.Thread(target=parse, daemon=True).start()

    with Status(f"{UPDATE_EMOJI} Finding tunnel URL...", console=console):
        for _ in range(MAX_RETRIES):
            if url_holder["url"] or proc.poll() is not None:
                break
            time.sleep(RETRY_DELAY)

    if not url_holder["url"]:
        proc.terminate()
        raise RuntimeError(f"{ERROR_EMOJI} Tunnel URL failed after retries.")

    return url_holder["url"], proc


@app.callback(invoke_without_command=True, help="Open the current app in your browser")
def open_cmd(
    platform: Optional[str] = typer.Option(None, help="Platform to open"),
    path: str = typer.Option("/docs", help="API path to open"),
    port: int = typer.Option(8080, help="Local port"),
    tunnel: bool = typer.Option(False, help="Use Cloudflare tunnel"),
    url: str = typer.Option(None, help="URL to open"),
):
    """
    Open the current app in your browser.

    Args:
        path: str
            The path to open
            default: /docs
        port: int
            The port to open
            default: 8080
        tunnel: bool
            Whether to use a tunnel
            default: False
        url: str
            The URL to open
    Returns:
        dict[str, Any]
    """
    if platform:
        result = switch(platform)
        if result.success:
            console.print(f"{SUCCESS_EMOJI} Using {platform} platform")
        else:
            console.print(
                f"{ERROR_EMOJI} Platform '{platform}' is not initialized yet."
            )
            console.print(f"{LIGHT_BULB_EMOJI} Run: sfai platform init {platform}")
            return
    result = open(path=path, port=port, tunnel=tunnel, url=url)

    if not result.success:
        console.print(f"{ERROR_EMOJI} [red]{result.error}[/]")
        raise typer.Exit(1)

    if result.url:
        console.print(
            f"{PORT_EMOJI} Opening {result.platform} app: [bold blue]{result.url}[/]"
        )
        webbrowser.open(result.url)
        return

    # Port-forward confirmed
    app_name = result.app_name
    console.print(
        f"{PORT_EMOJI} Port-forwarding svc/{app_name}-service → http://localhost:{port}"
    )
    time.sleep(3)
    if result.pf_proc.poll() is not None:
        console.print(f"{ERROR_EMOJI} Port-forwarding failed. Check service status.")
        return
    console.print(f"{SUCCESS_EMOJI} Port forwarding established.")

    tunnel_proc = None
    if tunnel:
        try:
            url, tunnel_proc = start_cloudflare_tunnel(port, path)
            console.print(f"{LINK_EMOJI} Tunnel ready: [bold blue]{url}[/]")
            webbrowser.open(url)
            console.print(f"{TUNNEL_EMOJI} Press Ctrl+C to stop...")
            tunnel_proc.wait()
        finally:
            if tunnel_proc and tunnel_proc.poll() is None:
                tunnel_proc.terminate()
    elif result["platform"] != "local" and result["tunnel"]:
        console.print(f"{ERROR_EMOJI} Tunnel is only supported for local apps")
    else:
        url = f"http://localhost:{port}{path}"
        console.print(f"{WEB_EMOJI} Opening [bold blue]{url}[/]")
        webbrowser.open(url)
        result["pf_proc"].wait()

    if result["pf_proc"].poll() is None:
        result["pf_proc"].terminate()
