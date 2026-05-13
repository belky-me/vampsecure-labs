# PassiveRecon

Motor de reconocimiento **pasivo** para mapeo de subdominios y detección de fugas de información en cabeceras HTTP.

Todas las consultas se realizan contra fuentes públicas de terceros. **El script no envía tráfico al dominio objetivo.**

## Fuentes utilizadas

### Subdominios
- **crt.sh** — Certificate Transparency logs
- **AlienVault OTX** — Passive DNS
- **HackerTarget** — Host search API
- **AnubisDB** — Agregador multi-fuente
- **Wayback Machine** — URLs archivadas
- **urlscan.io** — Histórico de escaneos públicos

### Cabeceras HTTP (sin tocar el target)
- **urlscan.io** — Cabeceras capturadas en escaneos anteriores
- **Wayback Machine** — Cabeceras originales preservadas con el prefijo `X-Archive-Orig-*`

## Instalación

```bash
cd passive_recon
python -m venv .venv
source .venv/bin/activate       # o .venv\Scripts\activate en Windows
pip install -r requirements.txt
cp .env.example .env            # añade tu OTX_API_KEY para mayor cobertura
```

## Variables de entorno

| Variable | Descripción |
|---|---|
| `OTX_API_KEY` | AlienVault OTX key (opcional). Aumenta el rate limit. Registro gratuito en https://otx.alienvault.com/api |

Copia `.env.example` a `.env` y rellena. El fichero `.env` nunca se sube al repositorio.

## Uso

```bash
# Enumeración + análisis de cabeceras
python main.py -d ejemplo.com

# Sólo enumeración de subdominios, volcarla a fichero
python main.py -d ejemplo.com --no-headers --subs-out subs.txt

# Reporte completo en JSON y HTML
python main.py -d ejemplo.com --json out.json --html out.html

# Ampliar cobertura de cabeceras a 40 hosts
python main.py -d ejemplo.com --max-hosts 40 --concurrency 10
```

## Detecciones en cabeceras

El analizador revisa cada respuesta capturada pasivamente y marca:

| Categoría                     | Ejemplos                                                |
|-------------------------------|---------------------------------------------------------|
| Information Disclosure        | `Server`, `X-Powered-By`, `X-AspNet-Version`, `Via`     |
| Missing Security Header       | HSTS, CSP, X-Frame-Options, X-Content-Type-Options, ... |
| Weak Security Header          | HSTS con `max-age` inferior a 1 año                     |
| Insecure Cookie               | Cookies sin `Secure` / `HttpOnly` / `SameSite`          |
| CORS Misconfiguration         | `Access-Control-Allow-Origin: *`                        |

La severidad se eleva automáticamente si se detectan versiones explícitas (p. ej. `Apache/2.4.29`).

## Salidas

- **Consola**: árboles, tablas y paneles con colores (vía `rich`).
- **JSON** (`--json`): estructura completa, apta para ingesta en SIEM / pipelines.
- **HTML** (`--html`): reporte standalone con paleta corporativa oscura.
- **TXT** (`--subs-out`): lista plana de subdominios para pipes con otras herramientas.

## Notas operativas

- Algunas fuentes públicas limitan peticiones por IP (p. ej. HackerTarget). Si una fuente falla, el resto continúa.
- `crt.sh` puede devolver respuestas muy grandes para dominios populares; el timeout por defecto es de 30 s.
- El análisis de cabeceras depende de que exista información pública previa del host en urlscan.io o Wayback. Hosts internos o recientes pueden aparecer sin datos.
- Si se requiere cobertura total (incluidos hosts sin histórico público), debería añadirse una fase activa — deliberadamente fuera del alcance de esta herramienta.

## Estructura

```
passive_recon/
├── main.py           # CLI
├── sources.py        # Enumeración pasiva de subdominios
├── headers.py        # Recolección pasiva y análisis de cabeceras
├── reporter.py       # Formateadores consola / JSON / HTML
└── requirements.txt
```
