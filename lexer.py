from ply import lex

# Lista de tokens
tokens = [
    # Operadores
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'NOT',
    'EQUALS', 'NOTEQUALS', 'GREATER', 'LESS',
    'GREATEREQUAL', 'LESSEQUAL', 'ASSIGN',
    
    # Delimitadores
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'COMMA', 'SEMICOLON',
    
    # Identificadores e literais
    'ID', 'INTEGER', 'FLOAT', 'STRING', 'BOOL',
]

# Palavras reservadas
reserved = {
    'Program': 'PROGRAM',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'break': 'BREAK',
    'print': 'PRINT',
    'input': 'INPUT',
    'const': 'CONST',
    'int': 'INT',
    'float': 'FLOAT',
    'str': 'STRING_TYPE',
    'bool': 'BOOL_TYPE',
    'true': 'TRUE',
    'false': 'FALSE'
}

# Adiciona palavras reservadas à lista de tokens
tokens = tokens + list(reserved.values())

# Regras para tokens simples
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_NOT = r'!'
t_EQUALS = r'=='
t_NOTEQUALS = r'!='
t_GREATER = r'>'
t_LESS = r'<'
t_GREATEREQUAL = r'>='
t_LESSEQUAL = r'<='
t_ASSIGN = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COMMA = r','
t_SEMICOLON = r';'

# Regra para identificadores
def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

# Regra para números float
def t_FLOAT(t):
    r'\d*\.\d+'
    t.value = float(t.value)
    return t

# Regra para números inteiros
def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Regra para strings
def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"'
    return t

# Caracteres ignorados (espaços e tabs)
t_ignore = ' \t'

# Nova linha
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Tratamento de erros
def t_error(t):
    print(f"Caractere ilegal '{t.value[0]}' na linha {t.lineno}")
    t.lexer.skip(1)

# Comentários de uma linha
def t_COMMENT(t):
    r'//.*'
    pass

# Criação do lexer
lexer = lex.lex() 