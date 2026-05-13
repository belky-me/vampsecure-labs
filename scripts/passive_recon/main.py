#!/usr/bin/env python3
"""
PassiveRecon
============
Motor de reconocimiento pasivo para mapeo de subdominios y detección
de fugas de información en cabeceras HTTP.

Todas las consultas se realizan contra fuentes públicas de terceros:
    * Certificate Transparency (crt.sh)
    * AlienVault OTX · HackerTarget · AnubisDB
    * Internet Archive (Wayback Machine)
    * urlscan.io

El script NO envía tráfico al dominio objetivo.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path


def _load_dotenv() -> None:
    """
    Carga un fichero .env situado junto al script (si existe).

    Formato soportado: `CLAVE=valor` por línea, admite comillas y
    comentarios iniciados con '#'. No sobrescribe variables ya definidas
    en el entorno (para que `docker run -e` tenga prioridad).
    """
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.is_file():
        return
    try:
        for raw in env_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
    except Exception:
        # Un .env mal formateado no debe romper la ejecución.
        pass


_load_dotenv()

from rich.console import Console
from rich.panel import Panel

from headers import HeaderAnalyzer
from reporter import Reporter
from sources import SubdomainEnumerator


BANNER = r"""
  ___                _          ___                    
 | _ \__ _ ______ __(_)_ _____ | _ \___ __ ___ _ _    
 |  _/ _` (_-<_-</ V  \ V / -_)|   / -_) _/ _ \ ' \   
 |_| \__,_/__/__/_|\_/\___/ |_|_\___\__\___/_||_|  
         Motor de reconocimiento pasivo · v1.0
		Belky - VampireBBS -
"""


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="passive-recon",
        description="Mapeo pasivo de subdominios y análisis de cabeceras HTTP.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Ejemplos:
  passive-recon -d ejemplo.com
  passive-recon -d ejemplo.com --headers --max-hosts 20
  passive-recon -d ejemplo.com --json salida.json --html salida.html
        """,
    )
    p.add_argument("-d", "--domain", required=True, help="Dominio raíz objetivo.")
    p.add_argument("--no-headers", action="store_true",
                   help="Omitir fase de análisis de cabeceras.")
    p.add_argument("--max-hosts", type=int, default=15,
                   help="Máximo de hosts a analizar para cabeceras (default 15).")
    p.add_argument("--concurrency", type=int, default=5,
                   help="Peticiones simultáneas en fase de cabeceras (default 5).")
    p.add_argument("--json", metavar="FILE",
                   help="Escribir reporte completo en JSON.")
    p.add_argument("--html", metavar="FILE",
                   help="Escribir reporte HTML.")
    p.add_argument("--subs-out", metavar="FILE",
                   help="Escribir sólo la lista plana de subdominios.")
    p.add_argument("--quiet", action="store_true",
                   help="Suprimir banner y salida decorativa.")
    return p.parse_args()


async def run(args: argparse.Namespace) -> int:
    console = Console()
    reporter = Reporter(console)

    if not args.quiet:
        console.print(f"[bold blue]{BANNER}[/]")
        console.print(Panel.fit(
            f"Objetivo: [bold]{args.domain}[/]\n"
            "Modo: pasivo (sin tráfico al target)",
            border_style="blue",
        ))

    # 1. Enumeración de subdominios
    console.print("\n[bold]>> Fase 1: enumeración pasiva de subdominios[/]\n")
    enumerator = SubdomainEnumerator()
    with console.status("[cyan]Consultando fuentes públicas...[/]", spinner="dots"):
        subs, src_results = await enumerator.enumerate(args.domain)

    reporter.print_source_summary(src_results)
    console.print()
    if subs:
        reporter.print_subdomains(args.domain, subs)
    else:
        console.print("[yellow]No se descubrieron subdominios.[/]")

    # 2. Análisis de cabeceras
    header_reports = {}
    if not args.no_headers and subs:
        console.print("\n[bold]>> Fase 2: análisis pasivo de cabeceras HTTP[/]\n")
        hosts = sorted(subs)
        # Incluir el apex explícitamente y limitar
        if args.domain not in hosts:
            hosts = [args.domain] + hosts
        hosts = hosts[: args.max_hosts]
        analyzer = HeaderAnalyzer()
        with console.status(f"[cyan]Recolectando cabeceras de {len(hosts)} hosts...[/]"):
            header_reports = await analyzer.analyze_hosts(
                hosts,
                max_per_host=1,
                concurrency=args.concurrency,
            )
        reporter.print_header_findings(header_reports)

    # 3. Salidas a fichero
    if args.subs_out:
        Path(args.subs_out).write_text("\n".join(sorted(subs)) + "\n", encoding="utf-8")
        console.print(f"\n[green]✓[/] Subdominios guardados en {args.subs_out}")

    if args.json:
        Path(args.json).write_text(
            reporter.to_json(args.domain, subs, src_results, header_reports),
            encoding="utf-8",
        )
        console.print(f"[green]✓[/] Reporte JSON en {args.json}")

    if args.html:
        Path(args.html).write_text(
            reporter.to_html(args.domain, subs, src_results, header_reports),
            encoding="utf-8",
        )
        console.print(f"[green]✓[/] Reporte HTML en {args.html}")

    return 0


def main() -> None:
    args = parse_args()
    try:
        exit_code = asyncio.run(run(args))
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario.", file=sys.stderr)
        sys.exit(130)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
