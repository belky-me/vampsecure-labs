# ICMP Shadow — Canal encubierto ICMP

Implementación educativa de un canal de comunicación encubierto usando paquetes ICMP Echo Request. Los datos se ofuscan con cifrado XOR + codificación Base64 antes de ser embebidos en el payload del paquete ICMP.

**Uso exclusivo en laboratorio y CTF. Ilegal en redes sin autorización.**

## Uso

```bash
# EMISOR: enviar mensaje encubierto
sudo python covert_icmp.py -m send -t 192.168.1.10 -d "mensaje secreto" -k MI_CLAVE

# RECEPTOR: escuchar en interfaz
sudo python covert_icmp.py -m listen -i eth0 -k MI_CLAVE
```

## Argumentos

| Flag | Descripción | Default |
|---|---|---|
| `-m` | Modo: `send` o `listen` | requerido |
| `-t` | IP destino (modo send) | — |
| `-d` | Mensaje a enviar | — |
| `-i` | Interfaz de red | `eth0` |
| `-k` | Clave XOR de ofuscación | `VAMP_KEY_2026` |

## Requisitos

```bash
pip install scapy
```

Requiere **privilegios de root** (raw sockets para envío/recepción ICMP).

## Funcionamiento técnico

1. **Cifrado**: XOR byte a byte entre el mensaje y la clave (repetida cíclicamente)
2. **Transporte**: resultado codificado en Base64 → embebido en campo `Raw` del ICMP
3. **Recepción**: filtro Scapy captura ICMP tipo 8 (Echo Request) con payload Raw
4. **Descifrado**: Base64 decode → XOR con misma clave → texto plano

```
"secreto" + XOR(VAMP_KEY_2026) → bytes → base64 → [ICMP payload]
```

## Por qué ICMP traversa firewalls

ICMP tipo 8 (ping) suele estar permitido en políticas de red estándar, lo que lo convierte en un vector histórico de exfiltración de datos en entornos con reglas de firewall restrictivas.
