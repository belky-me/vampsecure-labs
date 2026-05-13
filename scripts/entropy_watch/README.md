# Entropy Watch

Detector de ransomware basado en entropía de Shannon. Monitoriza un directorio en tiempo real y mueve automáticamente a cuarentena cualquier fichero cuya entropía supere el umbral configurado (por defecto 7.0 bits/byte), patrón característico de ficheros cifrados o comprimidos maliciosamente.

## Uso

```bash
# Monitorizar directorio por defecto (./test_zone)
python entropy_watch.py

# Monitorizar ruta personalizada
python entropy_watch.py -p /ruta/a/vigilar
```

## Requisitos

Solo biblioteca estándar de Python. Sin dependencias externas.

## Configuración

| Constante | Default | Descripción |
|---|---|---|
| `ENTROPY_THRESHOLD` | `7.0` | Umbral de Shannon en bits/byte (0–8) |
| `POLLING_INTERVAL` | `2` | Segundos entre ciclos de escaneo |
| `QUARANTINE_DIR` | `./quarantine` | Destino de ficheros aislados |

## Cómo funciona

La entropía de Shannon mide la aleatoriedad de un fichero:

```
H(X) = -Σ P(xᵢ) · log₂ P(xᵢ)
```

- Texto plano → H ≈ 4–5 bits/byte
- Binario ejecutable → H ≈ 5–6 bits/byte  
- Fichero cifrado / comprimido → H ≈ 7.5–8 bits/byte ← **ALERTA**

Al detectar un fichero sospechoso:
1. Lo mueve a `./quarantine/`
2. Cambia permisos a `0o444` (solo lectura)
3. Registra el evento con timestamp

## Ejemplo de salida

```
[2026-05-13 08:41:22] SAFE >> documento.pdf (H: 5.8821)
[2026-05-13 08:41:24] !! ALERTA !! nota.txt.enc [H: 7.9934]
    >> [SUCCESS] Amenaza aislada en /quarantine
```
