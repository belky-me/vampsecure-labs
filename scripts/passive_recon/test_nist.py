import requests
from datetime import datetime, timedelta

def check_nist_v2026():
    # 1. Definimos una ventana de tiempo segura para evitar "el futuro"
    # Inicio: hace 25 horas | Fin: hace 10 minutos
    now = datetime.utcnow()
    start_time = now - timedelta(hours=25)
    end_time = now - timedelta(minutes=10)

    # 2. Formato estricto con la 'Z' de UTC
    # NIST v2.0 prefiere: YYYY-MM-DDTHH:mm:ss.000Z
    start_str = start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    end_str = end_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')

    # 3. URL Base
    base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    
    # 4. Parámetros (dejamos que requests los maneje pero con la Z ya puesta)
    params = {
        'pubStartDate': start_str,
        'pubEndDate': end_str,
        'resultsPerPage': 5
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }

    print(f"[*] INICIANDO VENTANA SEGURA...")
    print(f"[*] DESDE: {start_str}")
    print(f"[*] HASTA: {end_str}")

    try:
        # Probamos primero con los parámetros automáticos
        response = requests.get(base_url, params=params, headers=headers, timeout=30)
        
        # Si falla con 404, intentamos la URL "en bruto" como último recurso
        if response.status_code == 404:
            print("[!] 404 detectado. Reintentando con bypass de codificación...")
            raw_url = f"{base_url}?pubStartDate={start_str}&pubEndDate={end_str}&resultsPerPage=5"
            response = requests.get(raw_url, headers=headers, timeout=30)

        if response.status_code == 200:
            data = response.json()
            total = data.get('totalResults', 0)
            print(f"[+] [200 OK] ¡NODO NIST DESBLOQUEADO!")
            print(f"[+] CVEs ENCONTRADOS: {total}")
            
            for v in data.get('vulnerabilities', []):
                print(f"    -> {v['cve']['id']} ({v['cve']['published']})")
        else:
            print(f"[!] [ERROR {response.status_code}]")
            print(f"[*] Respuesta: {response.text[:200]}")

    except Exception as e:
        print(f"[!] FALLO DE SISTEMA: {e}")

if __name__ == "__main__":
    check_nist_v2026()
