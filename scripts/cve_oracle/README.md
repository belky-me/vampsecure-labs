# Vamp CVE Oracle

Analizador e informador de CVEs con inteligencia de amenazas enriquecida. Consulta NIST NVD para datos CVSS y AlienVault OTX para pulsos de actividad activa. Genera reportes en consola o fichero de texto con PoC template automático.

## Uso

```bash
# Análisis básico
python vamp_cve_oracle.py CVE-2021-44228

# Guardar reporte en fichero
python vamp_cve_oracle.py CVE-2022-3602 -o reporte_openssl.txt

# Con OTX API key para inteligencia enriquecida
OTX_API_KEY=tu_key python vamp_cve_oracle.py CVE-2024-3094
```

## Requisitos

```bash
pip install requests
```

## Variables de entorno

| Variable | Descripción |
|---|---|
| `OTX_API_KEY` | API key de AlienVault OTX (opcional, mejora la inteligencia) |

Registro gratuito en https://otx.alienvault.com/api

## Salida

- **CVSS v3.1**: score y vector completo
- **Descripción técnica** del NVD
- **Pulsos OTX**: actividad en la comunidad de threat intelligence
- **PoC template**: estrategia de prueba adaptada al tipo de vulnerabilidad (path traversal, JNDI/Log4j, RCE...)
- **Timestamp regional**: hora local del sistema

## Ejemplo

```
[+] SEVERIDAD (CVSS v3.1): 10.0
[+] VECTOR: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H
[!] Detectados 3 pulsos de actividad.
- Amenaza: Log4Shell Exploitation | Tags: log4j, rce, exploit
```
