import sys
import time
from scapy.all import sniff, ARP
from datetime import datetime

IP_MAC_MAP = {}
LOCKED = False  # Nueva bandera de estado

def get_timestamp():
    return datetime.now().astimezone().strftime('%H:%M:%S')

def process_arp_packet(pkt):
    global LOCKED
    if pkt.haslayer(ARP) and pkt[ARP].op == 2:
        ip_src = pkt[ARP].psrc
        mac_src = pkt[ARP].hwsrc

        if ip_src in IP_MAC_MAP:
            if IP_MAC_MAP[ip_src] != mac_src:
                print(f"\n[!] ALERTA: SPOOFING DETECTADO en {ip_src}")
                print(f"    ORIGINAL: {IP_MAC_MAP[ip_src]} | NUEVA: {mac_src}")
        else:
            if not LOCKED:
                IP_MAC_MAP[ip_src] = mac_src
                print(f"[*] Aprendido: {ip_src} es {mac_src}")
            else:
                print(f"[?] Intento de nueva conexión bloqueado: {ip_src} intenta ser {mac_src}")

def main():
    global LOCKED
    import argparse
    parser = argparse.ArgumentParser(description="ARP-Sentinel: detector de ARP spoofing")
    parser.add_argument("-i", "--iface", default="eth0", help="Interfaz de red (default: eth0)")
    parser.add_argument("-t", "--timeout", type=int, default=5, help="Segundos de fase de aprendizaje (default: 5)")
    args = parser.parse_args()

    print("--- ARP-SENTINEL v1.1 (M3 STABLE) ---")
    print(f"[1] Iniciando FASE DE APRENDIZAJE ({args.timeout} segundos) en {args.iface}...")

    sniff(iface=args.iface, filter="arp", prn=process_arp_packet, store=0, timeout=args.timeout)

    LOCKED = True
    print("\n[2] FASE DE BLOQUEO ACTIVADA. La red está sellada.")
    print("[*] Vigilando cambios en las MACs conocidas...")

    sniff(iface=args.iface, filter="arp", prn=process_arp_packet, store=0)

if __name__ == "__main__":
    main()
