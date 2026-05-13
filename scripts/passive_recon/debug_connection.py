import requests

urls = [
    "https://services.nvd.nist.gov/rest/json/cves/2.0",  # Base
    "https://services.nvd.nist.gov/rest/json/cve/2.0",   # Posible typo
    "https://nvd.nist.gov/vuln/data-feeds"               # Web normal
]

for url in urls:
    try:
        r = requests.get(url, timeout=5)
        print(f"URL: {url} | STATUS: {r.status_code}")
    except Exception as e:
        print(f"URL: {url} | FALLO: {e}")
