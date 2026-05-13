import os
import math
import time
import shutil
import argparse
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
                       | |                                        
                       |_|   [ENTROPY-WATCH v1.3]
                               By VampSecure Intelligence
"""

# ==========================================
# CONFIGURACIÓN POR DEFECTO
# ==========================================
DEFAULT_TARGET = "./test_zone"
QUARANTINE_DIR = "./quarantine" 
ENTROPY_THRESHOLD = 7.0          
POLLING_INTERVAL = 2             

def calculate_entropy(file_path):
    """
    Calcula la Entropía de Shannon del archivo.
    $H(X) = -\sum_{i=0}^{255} P(x_i) \log_2 P(x_i)$
    """
    try:
        if not os.path.isfile(file_path):
            return None
        with open(file_path, 'rb') as f:
            data = f.read()
        if not data:
            return 0
        file_size = len(data)
        byte_counts = {}
        for byte in data:
            byte_counts[byte] = byte_counts.get(byte, 0) + 1
        entropy = 0
        for count in byte_counts.values():
            p = count / file_size
            entropy -= p * math.log2(p)
        return entropy
    except Exception:
        return None

def isolate_file(file_path, file_name):
    if not os.path.exists(QUARANTINE_DIR):
        os.makedirs(QUARANTINE_DIR)
    destination = os.path.join(QUARANTINE_DIR, file_name)
    try:
        shutil.move(file_path, destination)
        os.chmod(destination, 0o444) 
        return True
    except Exception as e:
        print(f"[!] Error de aislamiento: {e}")
        return False

def monitor(target_path):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    
    # Asegurar que la ruta existe
    if not os.path.exists(target_path):
        os.makedirs(target_path)
        print(f"[*] Creado nuevo directorio de vigilancia: {target_path}")

    print(f"[*] ESTADO: VIGILANCIA ACTIVA")
    print(f"[*] RUTA: {os.path.abspath(target_path)}")
    print(f"[*] UMBRAL: {ENTROPY_THRESHOLD} | RELOJ: SINCRONIZADO")
    print("-" * 65)

    known_files = {}

    try:
        while True:
            files_in_dir = [f for f in os.listdir(target_path) 
                           if os.path.isfile(os.path.join(target_path, f))]
            
            for file_name in files_in_dir:
                path = os.path.join(target_path, file_name)
                
                # Evitar procesar la propia cuarentena si está dentro
                if "quarantine" in path: continue

                try:
                    mtime = os.path.getmtime(path)
                except FileNotFoundError:
                    continue
                
                if path not in known_files or known_files[path] != mtime:
                    h = calculate_entropy(path)
                    known_files[path] = mtime
                    
                    # Tiempo real del sistema (Local)
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    if h is not None:
                        if h > ENTROPY_THRESHOLD:
                            print(f"[{timestamp}] !! ALERTA !! {file_name} [H: {h:.4f}]")
                            if isolate_file(path, file_name):
                                print(f"    >> [SUCCESS] Amenaza aislada en /quarantine")
                        elif h > 0:
                            print(f"[{timestamp}] SAFE >> {file_name} (H: {h:.4f})")
            
            time.sleep(POLLING_INTERVAL)
    except KeyboardInterrupt:
        print(f"\n[*] [NODO OFFLINE] Sesión terminada el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    # Configuración de argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="VampSecure Entropy-Watch: Detector de Ransomware")
    parser.add_argument("-p", "--path", help="Ruta del directorio a monitorizar", default=DEFAULT_TARGET)
    
    args = parser.parse_args()
    
    monitor(args.path)
