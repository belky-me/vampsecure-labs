#include <stdio.h>
#include <sys/mman.h>
#include <string.h>
#include <unistd.h>

void print_banner() {
    printf("--- VAMPSECURE M3 SHELL-LAB V4 (STABLE) ---\n");
}

int main() {
    print_banner();

    // Reservamos memoria ejecutable
    void *m = mmap(NULL, 1024, PROT_READ | PROT_WRITE | PROT_EXEC, 
                   MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);

    printf("[*] Memoria RX lista en %p. Inyectando lógica nativa...\n", m);

    /* En lugar de bytes manuales, usamos una función de C que contiene
       ensamblador puro de ARM64. Esto evita errores de alineación.
    */
    __asm__ (
        "mov x0, #1          \n"  // stdout
        "adr x1, message     \n"  // El compilador calcula el offset exacto
        "mov x2, #5          \n"  // Longitud de "VAMP\n"
        "mov x8, #64         \n"  // Syscall write (Linux ARM64)
        "svc #0              \n"  // Ejecutar
        "mov x0, #0          \n"  // Status 0
        "mov x8, #93         \n"  // Syscall exit
        "svc #0              \n"
        "message: .ascii \"VAMP\\n\" \n"
    );

    return 0;
}
