import requests

# Probamos las rutas más probables en 2026
endpoints = [
    "https://services.nvd.nist.gov/rest/json/cves/2.1",  # Posible actualización
    "https://services.nvd.nist.gov/rest/json/cves/2.0",  # La que falla
    "https://api.nvd.nist.gov/rest/json/cves/2.0",       # Cambio de subdominio
    "https://services.nvd.nist.gov/api/v3/cves",         # Salto a v3
]

headers = {'User-Agent': 'Mozilla/5.0 (VampSecure_Intel_Node_2026)'}

print("[*] ESCANEANDO PUERTOS DE ENLACE NIST...")

for url in endpoints:
    try:
        # Petición simple de un solo resultado para testear la ruta
        r = requests.get(f"{url}?resultsPerPage=1", headers=headers, timeout=10)
        print(f"[{r.status_code}] -> {url}")
        if r.status_code == 200:
            print(f"!!! NODO ENCONTRADO EN: {url} !!!")
            break
    except Exception as e:
        print(f"[ERROR] -> {url}: {e}")
