# ARP-Sentinel

Herramienta educativa de defensa y ataque ARP para laboratorio. Detecta ARP spoofing en tiempo real mediante una fase de aprendizaje seguida de monitorización continua. Incluye un módulo de ataque (PoC) para validar la detección.

## Componentes

| Fichero | Descripción |
|---|---|
| `vamp_arp_sentinel.py` | Monitor defensivo: aprende la red y detecta cambios de MAC |
| `vamp_arp_attacker.py` | PoC ofensivo: envenena la caché ARP (solo uso en lab) |

## Uso

```bash
# Defensa — fase aprendizaje 5s + monitorización continua
sudo python vamp_arp_sentinel.py -i eth0 -t 5

# Ataque PoC (entorno controlado)
sudo python vamp_arp_attacker.py 192.168.1.10 192.168.1.1 -i eth0
```

## Requisitos

```bash
pip install scapy
```

Requiere **privilegios de root** para sniffing de paquetes ARP.

## Cómo funciona

1. **Fase de aprendizaje** (`LOCKED=False`): registra el mapa IP→MAC real de la red durante N segundos
2. **Fase de bloqueo** (`LOCKED=True`): cualquier cambio en el mapa dispara una alerta
3. El **attacker** envía paquetes ARP `is-at` fraudulentos para envenenar cachés de otros equipos

## Advertencia

Este software es para uso exclusivo en entornos de laboratorio controlados. El uso de `vamp_arp_attacker.py` en redes sin autorización puede ser ilegal.
