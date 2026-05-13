// Solo como referencia, ya lo pasaremos a hex para el C
mov x0, #1          // stdout
adr x1, msg         // direccion del mensaje
mov x2, #5          // longitud
mov x8, #64         // syscall write
svc #0              // llamada al kernel

mov x0, #0          // status 0
mov x8, #93         // syscall exit
svc #0

msg: .ascii "VAMP\n"
