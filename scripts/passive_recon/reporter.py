"""
reporter.py
-----------
Formateadores de salida: consola (rich), JSON y HTML.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from headers import HeaderReport
from sources import SourceResult


SEVERITY_STYLE = {
    "info":   "cyan",
    "low":    "yellow",
    "medium": "orange3",
    "high":   "red",
}
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2, "info": 3}


class Reporter:

    def __init__(self, console: Console | None = None):
        self.console = console or Console()

    # ------------------------------------------------------------------
    # Consola
    # ------------------------------------------------------------------

    def print_source_summary(self, source_results: List[SourceResult]) -> None:
        table = Table(title="Fuentes pasivas consultadas", show_lines=False)
        table.add_column("Fuente")
        table.add_column("Estado")
        table.add_column("Subdominios", justify="right")
        for r in source_results:
            status = "[green]OK[/]" if r.ok else f"[red]ERROR[/] {r.error}"
            table.add_row(r.name, status, str(len(r.subdomains)))
        self.console.print(table)

    def print_subdomains(self, domain: str, subdomains: Set[str]) -> None:
        tree = Tree(f"[bold blue]{domain}[/] ({len(subdomains)} subdominios)")
        for sub in sorted(subdomains):
            tree.add(sub)
        self.console.print(tree)

    def print_header_findings(self, reports: Dict[str, List[HeaderReport]]) -> None:
        if not reports:
            self.console.print("[yellow]Sin datos públicos de cabeceras para los hosts analizados.[/]")
            return

        for host, host_reports in sorted(reports.items()):
            self.console.print()
            self.console.rule(f"[bold]{host}[/]")
            for rep in host_reports:
                meta = f"[dim]fuente:[/] {rep.source}  [dim]status:[/] {rep.status}  [dim]obs:[/] {rep.observed_at}"
                self.console.print(Panel(meta, title=rep.url, expand=False))

                if not rep.findings:
                    self.console.print("[green]Sin hallazgos en esta muestra.[/]")
                    continue

                t = Table(show_lines=False)
                t.add_column("Sev.")
                t.add_column("Categoría")
                t.add_column("Cabecera")
                t.add_column("Detalle")
                t.add_column("Valor")
                sorted_findings = sorted(rep.findings, key=lambda f: SEVERITY_ORDER.get(f.severity, 99))
                for f in sorted_findings:
                    style = SEVERITY_STYLE.get(f.severity, "white")
                    t.add_row(
                        f"[{style}]{f.severity.upper()}[/]",
                        f.category,
                        f.header,
                        f.detail,
                        (f.value or "")[:60],
                    )
                self.console.print(t)

    # ------------------------------------------------------------------
    # JSON
    # ------------------------------------------------------------------

    def to_json(
        self,
        domain: str,
        subdomains: Set[str],
        source_results: List[SourceResult],
        header_reports: Dict[str, List[HeaderReport]],
    ) -> str:
        payload = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "target": domain,
            "subdomains": sorted(subdomains),
            "sources": [
                {"name": r.name, "count": len(r.subdomains), "error": r.error}
                for r in source_results
            ],
            "headers": {
                host: [
                    {
                        "url": rep.url,
                        "source": rep.source,
                        "status": rep.status,
                        "observed_at": rep.observed_at,
                        "headers": rep.headers,
                        "findings": [asdict(f) for f in rep.findings],
                    }
                    for rep in reps
                ]
                for host, reps in header_reports.items()
            },
        }
        return json.dumps(payload, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------------
    # HTML
    # ------------------------------------------------------------------

    def to_html(
        self,
        domain: str,
        subdomains: Set[str],
        source_results: List[SourceResult],
        header_reports: Dict[str, List[HeaderReport]],
    ) -> str:
        severity_color = {
            "info":   "#4A90E2",
            "low":    "#D4A017",
            "medium": "#E67E22",
            "high":   "#C0392B",
        }

        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

        def esc(s: str) -> str:
            return (str(s).replace("&", "&amp;").replace("<", "&lt;")
                    .replace(">", "&gt;").replace('"', "&quot;"))

        src_rows = "".join(
            f"<tr><td>{esc(r.name)}</td>"
            f"<td>{'OK' if r.ok else 'ERROR: ' + esc(r.error or '')}</td>"
            f"<td style='text-align:right'>{len(r.subdomains)}</td></tr>"
            for r in source_results
        )

        sub_list = "".join(f"<li>{esc(s)}</li>" for s in sorted(subdomains))

        header_sections = []
        for host, reps in sorted(header_reports.items()):
            blocks = []
            for rep in reps:
                if rep.findings:
                    find_rows = "".join(
                        f"<tr>"
                        f"<td style='color:{severity_color.get(f.severity, '#333')};font-weight:bold'>{f.severity.upper()}</td>"
                        f"<td>{esc(f.category)}</td>"
                        f"<td><code>{esc(f.header)}</code></td>"
                        f"<td>{esc(f.detail)}</td>"
                        f"<td><code>{esc((f.value or '')[:80])}</code></td>"
                        f"</tr>"
                        for f in sorted(rep.findings, key=lambda f: SEVERITY_ORDER.get(f.severity, 99))
                    )
                    findings_html = (
                        "<table><thead><tr><th>Sev</th><th>Categoría</th>"
                        "<th>Cabecera</th><th>Detalle</th><th>Valor</th></tr></thead>"
                        f"<tbody>{find_rows}</tbody></table>"
                    )
                else:
                    findings_html = "<p class='ok'>Sin hallazgos en esta muestra.</p>"

                hdr_rows = "".join(
                    f"<tr><td><code>{esc(k)}</code></td><td><code>{esc(v)}</code></td></tr>"
                    for k, v in rep.headers.items()
                )

                blocks.append(
                    f"<div class='snapshot'>"
                    f"<h4>{esc(rep.url)}</h4>"
                    f"<p class='meta'>Fuente: <b>{esc(rep.source)}</b> · "
                    f"Status: {rep.status} · Observado: {esc(rep.observed_at or 'n/a')}</p>"
                    f"{findings_html}"
                    f"<details><summary>Cabeceras en bruto ({len(rep.headers)})</summary>"
                    f"<table class='raw'><tbody>{hdr_rows}</tbody></table></details>"
                    f"</div>"
                )

            header_sections.append(
                f"<section><h3>{esc(host)}</h3>{''.join(blocks)}</section>"
            )

        headers_html = "".join(header_sections) or "<p>Sin datos públicos de cabeceras.</p>"

        return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>PassiveRecon · {esc(domain)}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          background:#0E2A47; color:#eee; margin:0; padding:2rem; }}
  header {{ border-bottom:2px solid #4A7AA8; padding-bottom:1rem; margin-bottom:2rem; }}
  h1 {{ color:#4A7AA8; margin:0; }}
  h2 {{ color:#4A7AA8; border-bottom:1px solid #4A7AA8; padding-bottom:.3rem; }}
  h3 {{ color:#fff; background:#123b63; padding:.5rem .8rem; border-radius:4px; }}
  table {{ width:100%; border-collapse:collapse; background:#123b63; margin:.5rem 0; }}
  th, td {{ padding:.4rem .6rem; border-bottom:1px solid #2d5580; text-align:left;
            vertical-align:top; font-size:.9rem; }}
  th {{ background:#0E2A47; color:#4A7AA8; }}
  code {{ background:#0a1f33; padding:.1rem .3rem; border-radius:3px; color:#9ecbff; }}
  .meta {{ color:#aac4e0; font-size:.85rem; }}
  .ok {{ color:#6fcf97; }}
  .snapshot {{ background:#0a1f33; padding:1rem; border-radius:6px; margin-bottom:1rem; }}
  details summary {{ cursor:pointer; color:#4A7AA8; margin-top:.5rem; }}
  .raw td {{ font-family:ui-monospace,monospace; font-size:.78rem; word-break:break-all; }}
  ul.subs {{ columns:3; font-family:ui-monospace,monospace; font-size:.85rem; }}
  footer {{ margin-top:3rem; color:#6a8bb0; font-size:.8rem; text-align:center; }}
</style>
</head>
<body>
  <header>
    <h1>PassiveRecon Report</h1>
    <p class="meta">Target: <b>{esc(domain)}</b> · Generado: {ts}</p>
  </header>

  <h2>Fuentes consultadas</h2>
  <table><thead><tr><th>Fuente</th><th>Estado</th><th>Subdominios</th></tr></thead>
    <tbody>{src_rows}</tbody></table>

  <h2>Subdominios descubiertos ({len(subdomains)})</h2>
  <ul class="subs">{sub_list}</ul>

  <h2>Análisis de cabeceras</h2>
  {headers_html}

  <footer>
    Generado pasivamente · No se envió tráfico al target · Datos de crt.sh, AlienVault OTX,
    HackerTarget, Wayback Machine, AnubisDB y urlscan.io.
  </footer>
</body>
</html>
"""
