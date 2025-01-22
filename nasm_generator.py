class NASMGenerator:
    def __init__(self):
        self.code = []
        self.data = []
        self.vars = set()
        self.temp_vars = set()
        self.string_literals = {}
        self.string_counter = 0
        self.bss = [
        "section .bss",
        "    align 4"  # Garantir alinhamento de 4 bytes
    ]
        
    def generate_nasm(self, tac_instructions):
        # Primeiro passo: análise das instruções para identificar variáveis e literais
        self._analyze_tac(tac_instructions)
        
        # Gera seção de dados
        self._generate_data_section()
        
        # Gera seção de código
        self._generate_code_section()
        
        # Processa cada instrução TAC
        for instr in tac_instructions:
            if instr.endswith(':'):  # É um label
                self.code.append(instr)
                continue
            self._process_instruction(instr)
            
        return self._get_full_code()
        
    def _analyze_tac(self, instructions):
        for instr in instructions:
            parts = instr.split()
            if not parts:
                continue
                
            if parts[0] == 'DECLARE':
                self.vars.add(parts[1])
            elif parts[0] == 'PRINT' and parts[1].startswith('"'):
                value = ' '.join(parts[1:])
                if value not in self.string_literals:
                    label = f"str_{self.string_counter}"
                    self.string_literals[value] = label
                    self.string_counter += 1
            elif 't' in instr and '=' in instr:
                # Captura variáveis temporárias (t0, t1, etc)
                temp = instr.split('=')[0].strip()
                if temp.startswith('t'):
                    self.temp_vars.add(temp)
                        
    def _generate_data_section(self):
        self.data = [
            "section .data",
            "    fmt_str db '%s', 0",
            "    fmt_int db '%d', 0",
            "    fmt_in db '%d', 0",
            "    fmt_out db '%d', 10, 0"  # 10 é o \n
        ]
        
        # Strings literais
        for string, label in self.string_literals.items():
            clean_string = string.strip('"')
            self.data.append(f"    {label} db '{clean_string}', 0")
            
        # Variáveis e temporários
        for var in self.vars:
            self.data.append(f"    {var} dd 0")
        for temp in self.temp_vars:
            self.data.append(f"    {temp} dd 0")
            
        self.data.append("")  # Linha em branco para separação
        
    def _generate_code_section(self):
        self.code = [
            "section .text",
            "    global main",
            "    extern printf",
            "    extern scanf",
            "",
            "main:",
            "    push ebp",          # Preservar frame pointer
            "    mov ebp, esp",      # Setup novo frame
            "    sub esp, 8"         # Reservar espaço para variáveis locais
        ]
        
    def _process_instruction(self, instr):
        parts = instr.split()
        
        if not parts:
            return
            
        command = parts[0]
        
        if command == 'DECLARE':
            pass  # Já tratado na seção .data
            
        elif command == 'INPUT':
            var = parts[1]
            self.code.extend([
                "    push ebx",                # Preserva registradores
                "    push ecx",
                "    push edx",
                f"    push {var}",             # Endereço da variável
                "    push fmt_in",             # Format string
                "    call scanf",              # Chama scanf
                "    add esp, 8",              # Limpa argumentos (2 * 4 bytes)
                "    pop edx",                 # Restaura registradores
                "    pop ecx",
                "    pop ebx"
            ])
            
        elif command == 'PRINT':
            if parts[1].startswith('"'):
                value = ' '.join(parts[1:])
                label = self.string_literals[value]
                self.code.extend([
                    "    push ebx",
                    "    push ecx",
                    "    push edx",
                    f"    push {label}",
                    "    push fmt_str",
                    "    call printf",
                    "    add esp, 8",
                    "    pop edx",
                    "    pop ecx",
                    "    pop ebx"
                ])
            else:
                value = parts[1]
                self.code.extend([
                    "    push ebx",
                    "    push ecx",
                    "    push edx",
                    f"    mov eax, [{value}]",
                    "    push eax",
                    "    push fmt_out",
                    "    call printf",
                    "    add esp, 8",
                    "    pop edx",
                    "    pop ecx",
                    "    pop ebx"
                ])
                
        elif command == 'if' and parts[1] == 'not':
            condition = parts[2]
            label = parts[4]
            self.code.extend([
                f"    mov eax, [{condition}]",
                "    cmp eax, 0",
                f"    je {label}"
            ])
            
        elif command == 'goto':
            label = parts[1]
            self.code.append(f"    jmp {label}")
            
        elif '=' in instr:
            dest = parts[0]
            if '>' in instr:  # Comparação específica para x > 0
                left = parts[2]
                right = parts[4]
                # Adicionar verificação de valor válido
                if not right.isdigit() and not right.startswith('['):
                    right = f"[{right}]"
                
                self.code.extend([
                    "    push eax",  # Preservar eax
                    f"    mov eax, [{left}]",
                    f"    cmp eax, {right}",
                    "    setg al",
                    "    movzx eax, al",
                    f"    mov [{dest}], eax",
                    "    pop eax"    # Restaurar eax
                ])
            

    def _add_exit_code(self):
        self.code.extend([
            "",
            "    push ebp",      # Salvar frame pointer atual
            "    mov ebp, esp",  # Estabelecer novo frame pointer
            "    mov esp, ebp",  # Restaura o stack pointer
            "    pop ebp",       # Restaura o frame pointer
            "    xor eax, eax",  # Return 0
            "    ret"           # Retornar do procedimento
        ])
    
    def _get_full_code(self):
        return '\n'.join(
            self.data +
            self.bss +              # Adicionar seção BSS
            self.code + [
                "    mov esp, ebp",  # Restaurar stack
                "    pop ebp",       # Restaurar frame pointer
                "    ret"           # Retorno limpo
            ]
        )

    def save_to_file(self, filename, code):
        filename = 'output/' + filename
        with open(filename, 'w') as f:
            f.write(code)