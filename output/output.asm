section .data
    fmt_str db '%s', 0
    fmt_int db '%d', 0
    fmt_in db '%d', 0
    fmt_out db '%d', 10, 0
    str_0 db 'Insira o valor de x:', 0
    str_1 db 'Valor maior que 2', 0
    str_2 db 'Valor menor que 2', 0
    i dd 0
    x dd 0
    t0 dd 0

section .bss
    align 4
section .text
    global main
    extern printf
    extern scanf

main:
    push ebp
    mov ebp, esp
    sub esp, 8
    push ebx
    push ecx
    push edx
    push str_0
    push fmt_str
    call printf
    add esp, 8
    pop edx
    pop ecx
    pop ebx
    push ebx
    push ecx
    push edx
    push x
    push fmt_in
    call scanf
    add esp, 8
    pop edx
    pop ecx
    pop ebx
    push eax
    mov eax, [x]
    cmp eax, 2
    setg al
    movzx eax, al
    mov [t0], eax
    pop eax
    mov eax, [t0]
    cmp eax, 0
    je L0
    push ebx
    push ecx
    push edx
    push str_1
    push fmt_str
    call printf
    add esp, 8
    pop edx
    pop ecx
    pop ebx
    jmp L1
L0:
    push ebx
    push ecx
    push edx
    push str_2
    push fmt_str
    call printf
    add esp, 8
    pop edx
    pop ecx
    pop ebx
L1:
    mov esp, ebp
    pop ebp
    ret