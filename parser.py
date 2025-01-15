from ply import yacc
from lexer import tokens, lexer
import sys

precedence = (
    ('right', 'UMINUS'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('left', 'EQUALS', 'NOTEQUALS'),
    ('left', 'GREATER', 'LESS', 'GREATEREQUAL', 'LESSEQUAL'),
)

class Node:
    def __init__(self, type, children=None, leaf=None):
        self.type = type
        self.children = children if children else []
        self.leaf = leaf
        
    def __str__(self):
        if self.leaf is not None:
            return f"({self.type} {self.leaf})"
        return f"({self.type} {' '.join(str(child) for child in self.children)})"

# Regras de produção
def p_program(p):
    'program : PROGRAM ID LBRACE declarations statements RBRACE'
    p[0] = Node('Program', [Node('ID', leaf=p[2]), p[4], p[5]])

def p_declarations(p):
    '''declarations : declaration declarations
                   | declaration'''
    if len(p) > 2:
        p[0] = Node('Declarations', [p[1]] + p[2].children)
    else:
        p[0] = Node('Declarations', [p[1]])

def p_declarations_empty(p):
    'declarations : '
    p[0] = Node('Declarations', [])

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

def p_statements_empty(p):
    'statements : '
    p[0] = Node('Statements', [])

def p_statement(p):
    '''statement : assignment
                | if_statement
                | while_statement
                | break_statement
                | print_statement
                | input_statement'''
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
                   | NOT logical_term
                   | MINUS logical_term %prec UMINUS'''
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
    if len(p) > 2:
        p[0] = Node('BinOp', [p[1], p[3]], p[2])
    else:
        p[0] = p[1]

def p_term(p):
    '''term : factor
            | term TIMES factor
            | term DIVIDE factor'''
    if len(p) > 2:
        p[0] = Node('BinOp', [p[1], p[3]], p[2])
    else:
        p[0] = p[1]

def p_factor(p):
    '''factor : LPAREN expression RPAREN
              | ID
              | literal'''
    if len(p) > 2:
        p[0] = p[2]
    else:
        if isinstance(p[1], Node):
            p[0] = p[1]
        else:
            p[0] = Node('ID', leaf=p[1])

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
        """ if result:
            print(result) """
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