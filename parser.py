from ply import yacc
from lexer import tokens, lexer
import sys

precedence = (
    ('right', 'UMINUS'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('left', 'EQUALS', 'NOTEQUALS'),
    ('left', 'GREATER', 'LESS', 'GREATEREQUAL', 'LESSEQUAL'),
    ('left', 'NOT'),
)

class CodeGenerator:
    def __init__(self):
        self.code = []
        self.temp_vars = set()
        self.label_map = {}
        self.current_line = 0
        
    def generate_python_code(self, tac_instructions):
        # Primeiro passo: identificar todas as variáveis temporárias e labels
        self._analyze_tac(tac_instructions)
        
        # Adiciona imports e setup inicial
        self._add_header()
        
        # Processa cada instrução TAC
        for instr in tac_instructions:
            self.current_line += 1
            if instr.endswith(':'):  # É um label
                self.label_map[instr[:-1]] = len(self.code)
                continue
                
            self._process_instruction(instr)
            
        return '\n'.join(self.code)
        
    def _analyze_tac(self, instructions):
        for instr in instructions:
            # Identifica variáveis temporárias (t0, t1, etc)
            parts = instr.split()
            for part in parts:
                if part.startswith('t') and part[1:].isdigit():
                    self.temp_vars.add(part)
                    
    def _add_header(self):
        # Adiciona imports necessários
        self.code.append("def main():")
        
        # Declara variáveis temporárias
        if self.temp_vars:
            temp_declarations = ", ".join(sorted(self.temp_vars))
            self.code.append(f"    {temp_declarations} = {', '.join(['None'] * len(self.temp_vars))}")
            
    def _process_instruction(self, instr):
        parts = instr.split()
        
        if instr.startswith('DECLARE'):
            # Declaração de variável
            var_name = parts[1]
            self.code.append(f"    {var_name} = None")
            
        elif instr.startswith('INPUT'):
            # Entrada de dados
            var_name = parts[1]
            self.code.append(f"    {var_name} = int(input())")
            
        elif instr.startswith('PRINT'):
            # Saída de dados
            value = ' '.join(parts[1:])
            self.code.append(f"    print({value})")
            
        elif instr.startswith('if not'):
            # Instrução de desvio condicional
            condition = parts[2]
            label = parts[4]
            self.code.append(f"    if not {condition}:")
            self.code.append(f"        goto .{label}")
            
        elif instr.startswith('goto'):
            # Desvio incondicional
            label = parts[1]
            self.code.append(f"    goto .{label}")
            
        elif '=' in instr:
            # Atribuição ou operação
            self.code.append(f"    {instr}")
            
    def save_to_file(self, filename, code):
        with open(filename, 'w') as f:
            # Adiciona imports necessários
            f.write("from goto import with_goto\n\n")
            # Adiciona decorador para suporte a goto
            f.write("@with_goto\n")
            # Escreve o código gerado
            f.write(code)
            # Adiciona chamada à função main
            f.write("\n\nif __name__ == '__main__':\n    main()\n")

    def optimize_code(self, code):
        """Realiza otimizações básicas no código gerado"""
        optimized = []
        for line in code.split('\n'):
            # Remove atribuições redundantes (x = x)
            if '=' in line:
                parts = line.split('=')
                if parts[0].strip() == parts[1].strip():
                    continue
            optimized.append(line)
        return '\n'.join(optimized)

class TACGenerator:
    def __init__(self):
        self.instructions = []
        self.temp_counter = 0
        self.label_counter = 0
        
    def new_temp(self):
        temp = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp
        
    def new_label(self):
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label
        
    def add_instruction(self, instruction):
        self.instructions.append(instruction)
        
    def print_instructions(self):
        for i, instr in enumerate(self.instructions):
            print(f"{i}: {instr}")

class Node:
    def __init__(self, type, children=None, leaf=None):
        self.type = type
        self.children = children if children else []
        self.leaf = leaf

    def generate_tac(self, generator):
        method_name = f'generate_tac_{self.type}'
        if hasattr(self, method_name):
            return getattr(self, method_name)(generator)
        return self.generic_generate_tac(generator)
        
    def generic_generate_tac(self, generator):
        results = []
        for child in self.children:
            if isinstance(child, Node):
                results.append(child.generate_tac(generator))
        return results[-1] if results else None

    def generate_tac_Program(self, generator):
        return self.children[1].generate_tac(generator)  # Generate TAC for statements

    def generate_tac_Declaration(self, generator):
        # For declarations, we'll just generate a DECLARE instruction
        for id_node in self.children[1:]:
            var_name = id_node.leaf
            generator.add_instruction(f"DECLARE {var_name}")
        return None

    def generate_tac_Assignment(self, generator):
        target = self.children[0].leaf
        value = self.children[1].generate_tac(generator)
        generator.add_instruction(f"{target} = {value}")
        return target

    def generate_tac_If(self, generator):
        condition = self.children[0].generate_tac(generator)
        
        # Gera labels para os blocos
        else_label = generator.new_label()
        end_label = generator.new_label()
        
        # Adiciona o desvio condicional
        generator.add_instruction(f"if not {condition} goto {else_label}")
        
        # Gera código para o bloco if
        self.children[1].generate_tac(generator)
        
        # Pula o bloco else
        generator.add_instruction(f"goto {end_label}")
        
        # Label para o bloco else
        generator.add_instruction(f"{else_label}:")
        
        # Se houver um bloco else, gera seu código
        if len(self.children) > 2:
            self.children[2].generate_tac(generator)
        
        # Label para o fim do if-else
        generator.add_instruction(f"{end_label}:")
        
        return None

    def generate_tac_BinOp(self, generator):
        left = self.children[0].generate_tac(generator)
        right = self.children[1].generate_tac(generator)
        result = generator.new_temp()
        generator.add_instruction(f"{result} = {left} {self.leaf} {right}")
        return result

    def generate_tac_RelationalOp(self, generator):
        left = self.children[0].generate_tac(generator)
        right = self.children[1].generate_tac(generator)
        result = generator.new_temp()
        generator.add_instruction(f"{result} = {left} {self.leaf} {right}")
        return result

    def generate_tac_While(self, generator):
        start_label = generator.new_label()
        end_label = generator.new_label()
        
        # Label for loop start
        generator.add_instruction(f"{start_label}:")
        
        # Generate condition code
        condition = self.children[0].generate_tac(generator)
        generator.add_instruction(f"if not {condition} goto {end_label}")
        
        # Generate loop body
        self.children[1].generate_tac(generator)
        
        # Jump back to start
        generator.add_instruction(f"goto {start_label}")
        
        # End label
        generator.add_instruction(f"{end_label}:")
        return None

    def generate_tac_Print(self, generator):
        for expr in self.children:
            value = expr.generate_tac(generator)
            generator.add_instruction(f"PRINT {value}")
        return None

    def generate_tac_Input(self, generator):
        for id_node in self.children:
            var_name = id_node.leaf
            generator.add_instruction(f"INPUT {var_name}")
        return None

    def generate_tac_ID(self, generator):
        return self.leaf

    def generate_tac_Literal(self, generator):
        return str(self.leaf)

    def __str__(self):
        if self.leaf is not None:
            return f"({self.type} {self.leaf})"
        children_str = ' '.join(str(child) for child in self.children)
        return f"({self.type} {children_str})"

    def print_tree(self, level=0):
        indent = "  " * level
        if self.leaf is not None:
            print(f"{indent}({self.type} {self.leaf})")
        else:
            print(f"{indent}({self.type}")
            for child in self.children:
                if isinstance(child, Node):
                    child.print_tree(level + 1)
                else:
                    print(f"{indent}  {child}")
            print(f"{indent})")

# Regras de produção
def p_program(p):
    'program : PROGRAM ID LBRACE statements RBRACE'
    p[0] = Node('Program', [Node('ID', leaf=p[2]), p[4], p[5]])

def p_declaration(p):
    '''declaration : type ID_list SEMICOLON
                  | CONST type ID ASSIGN literal SEMICOLON'''
    if len(p) > 4:
        p[0] = Node('ConstDecl', [p[2], p[5]], p[3])
    else:
        p[0] = Node('Declaration', [p[1]] + p[2])

def p_type(p):
    '''type : INT
            | FLOAT
            | STRING_TYPE
            | BOOL_TYPE'''
    p[0] = Node('Type', leaf=p[1])

def p_ID_list(p):
    '''ID_list : ID COMMA ID_list
               | ID'''
    if len(p) > 2:
        p[0] = [Node('ID', leaf=p[1])] + p[3]
    else:
        p[0] = [Node('ID', leaf=p[1])]

def p_statements(p):
    '''statements : statement statements
                 | statement'''
    if len(p) > 2:
        p[0] = Node('Statements', [p[1]] + p[2].children)
    else:
        p[0] = Node('Statements', [p[1]])

def p_statement(p):
    '''statement : assignment
                | if_statement
                | while_statement
                | break_statement
                | print_statement
                | input_statement
                | declaration'''
    p[0] = p[1]

def p_assignment(p):
    'assignment : ID ASSIGN expression SEMICOLON'
    p[0] = Node('Assignment', [Node('ID', leaf=p[1]), p[3]])

def p_if_statement(p):
    '''if_statement : IF LPAREN expression RPAREN LBRACE statements RBRACE
                   | IF LPAREN expression RPAREN LBRACE statements RBRACE ELSE LBRACE statements RBRACE'''
    if len(p) > 8:
        p[0] = Node('If', [p[3], p[6], p[10]])
    else:
        p[0] = Node('If', [p[3], p[6]])

def p_while_statement(p):
    'while_statement : WHILE LPAREN expression RPAREN LBRACE statements RBRACE'
    p[0] = Node('While', [p[3], p[6]])

def p_break_statement(p):
    'break_statement : BREAK SEMICOLON'
    p[0] = Node('Break')

def p_print_statement(p):
    '''print_statement : PRINT LPAREN print_args RPAREN SEMICOLON'''
    p[0] = Node('Print', p[3])

def p_print_args(p):
    '''print_args : expression
                 | expression COMMA print_args'''
    if len(p) > 2:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]

def p_input_statement(p):
    'input_statement : INPUT LPAREN input_args RPAREN SEMICOLON'
    p[0] = Node('Input', p[3])

def p_input_args(p):
    '''input_args : ID
                  | ID COMMA input_args'''
    if len(p) > 2:
        p[0] = [Node('ID', leaf=p[1])] + p[3]
    else:
        p[0] = [Node('ID', leaf=p[1])]

def p_expression(p):
    '''expression : logical_term
                 | expression logical_operator logical_term
                 | MINUS expression %prec UMINUS'''
    if len(p) == 3:
        p[0] = Node('UnaryOp', [p[2]], p[1])
    elif len(p) == 4:
        p[0] = Node('LogicalOp', [p[1], p[3]], p[2])
    else:
        p[0] = p[1]

def p_logical_operator(p):
    '''logical_operator : EQUALS
                       | NOTEQUALS'''
    p[0] = p[1]

def p_logical_term(p):
    '''logical_term : relational_expression
                   | NOT logical_term'''
    if len(p) == 3:
        p[0] = Node('UnaryOp', [p[2]], p[1])
    else:
        p[0] = p[1]

def p_relational_expression(p):
    '''relational_expression : arithmetic_expression
                            | arithmetic_expression comparison_operator arithmetic_expression'''
    if len(p) > 2:
        p[0] = Node('RelationalOp', [p[1], p[3]], p[2])
    else:
        p[0] = p[1]

def p_comparison_operator(p):
    '''comparison_operator : GREATER
                         | LESS
                         | GREATEREQUAL
                         | LESSEQUAL'''
    p[0] = p[1]

def p_arithmetic_expression(p):
    '''arithmetic_expression : term
                           | arithmetic_expression PLUS term
                           | arithmetic_expression MINUS term'''
    if len(p) == 4:  # Expressão binária
        p[0] = Node('BinOp', children=[p[1], p[3]], leaf=p[2])
    else:  # Apenas um termo
        p[0] = p[1]

def p_term(p):
    '''term : factor
            | term TIMES factor
            | term DIVIDE factor'''
    if len(p) == 4:  # Expressão binária
        p[0] = Node('BinOp', children=[p[1], p[3]], leaf=p[2])
    else:  # Apenas um fator
        p[0] = p[1]

def p_factor(p):
    '''factor : LPAREN arithmetic_expression RPAREN
              | ID
              | literal'''
    if len(p) == 4:  # Parênteses
        p[0] = p[2]  # Retorna a subexpressão dentro dos parênteses
    elif p.slice[1].type == 'ID':  # Identificador
        p[0] = Node('ID', leaf=p[1])
    else:  # Literal
        p[0] = p[1]

def p_literal(p):
    '''literal : INTEGER
               | FLOAT
               | STRING
               | boolean'''
    p[0] = Node('Literal', leaf=p[1])

def p_boolean(p):
    '''boolean : TRUE
               | FALSE'''
    p[0] = Node('Boolean', leaf=p[1])

def p_error(p):
    if p:
        print(f"Erro sintático na linha {p.lineno} próximo a '{p.value}'")
    else:
        print("Erro sintático no final do arquivo")

# Criação do parser
parser = yacc.yacc()

def parse_file(filename):
    try:
        with open(filename, 'r') as file:
            data = file.read()
        result = parser.parse(data, lexer=lexer)
        return result
    except FileNotFoundError:
        print(f"Erro: Arquivo '{filename}' não encontrado.")
    except Exception as e:
        print(f"Erro ao processar arquivo: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python parser.py arquivo.lps")
    else:
        parse_file(sys.argv[1])