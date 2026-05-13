# VampSecure Shell Lab

Laboratorio de shellcode ARM64 en entorno seguro. Demuestra los conceptos de memoria ejecutable (`mmap RWX`), syscalls Linux directas y ensamblador inline en C — herramientas fundamentales para entender el funcionamiento de exploits de bajo nivel.

**Requiere Linux ARM64 (o QEMU ARM64). No funciona en x86.**

## Contenido

| Fichero | Descripción |
|---|---|
| `vamp_shell_lab.c` | Programa C que reserva memoria RWX e inyecta lógica ARM64 con `__asm__` |
| `vamp_msg.s` | Referencia del shellcode en ensamblador puro |

## Compilar y ejecutar

```bash
# En Linux ARM64 (ej. Raspberry Pi, Mac M1/M2 con Docker Linux)
gcc -o vamp_shell_lab vamp_shell_lab.c -z execstack
./vamp_shell_lab
```

Salida esperada:
```
--- VAMPSECURE M3 SHELL-LAB V4 (STABLE) ---
[*] Memoria RX lista en 0x7f8a3c0000. Inyectando lógica nativa...
VAMP
```

## Conceptos demostrados

### mmap RWX
```c
void *m = mmap(NULL, 1024, PROT_READ | PROT_WRITE | PROT_EXEC,
               MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);
```
Reserva un bloque de memoria con permisos de lectura, escritura **y ejecución** simultáneos. Base de cualquier técnica de inyección de shellcode.

### Syscalls ARM64 directas
```asm
mov x8, #64    // número de syscall write
mov x0, #1     // fd = stdout
adr x1, msg    // puntero al mensaje
mov x2, #5     // longitud
svc #0         // trap al kernel
```

Los registros `x0-x7` son argumentos, `x8` es el número de syscall, `svc #0` es la instrucción de trampa al kernel.

## Notas de seguridad

- `-z execstack` desactiva la protección NX/XD del linker. Solo para laboratorio.
- En producción, la memoria ejecutable sin NX es un vector de ataque conocido (CVE-2004-0495 y similares).
- El binario compilado (`vamp_shell_lab`) está en `.gitignore`.
