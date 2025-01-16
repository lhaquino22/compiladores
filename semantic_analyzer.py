from parser import Node

class Symbol:
    def __init__(self, name, type, is_const=False, value=None):
        self.name = name
        self.type = type
        self.is_const = is_const
        self.value = value

class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.scopes = [{}]  # Stack of scopes
        
    def enter_scope(self):
        self.scopes.append({})
        
    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()
            
    def declare(self, name, type, is_const=False, value=None):
        if name in self.scopes[-1]:
            raise SemanticError(f"Váriavel '{name}' ja declarada.")
        self.scopes[-1][name] = Symbol(name, type, is_const, value)
        
    def lookup(self, name):
        # Search from inner to outer scope
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise SemanticError(f"Variável '{name}' não declarada.")

class SemanticError(Exception):
    pass

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        
    def analyze(self, ast):
        try:
            self.visit(ast)
            if self.errors:
                return False, self.errors
            return True, []
        except SemanticError as e:
            self.errors.append(str(e))
            return False, self.errors
            
    def visit(self, node):
        if node is None:
            return None
            
        method_name = f'visit_{node.type}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
        
    def generic_visit(self, node):
        for child in node.children:
            if isinstance(child, Node):
                self.visit(child)
    
    def visit_Program(self, node):
        # Visit all statements in the program
        self.visit(node.children[1])  # statements node
        
    def visit_Declaration(self, node):
        type_node = node.children[0]
        var_type = type_node.leaf
        
        # Process all variables in declaration
        for id_node in node.children[1:]:
            var_name = id_node.leaf
            self.symbol_table.declare(var_name, var_type)
            
    def visit_ConstDecl(self, node):
        type_node = node.children[0]
        var_type = type_node.leaf
        var_name = node.leaf
        value_node = node.children[1]
        
        # Check if literal type matches declared type
        if not self.check_type_compatibility(var_type, value_node):
            raise SemanticError(f"Erro de atribuiução de tipo para '{var_name}'")
            
        self.symbol_table.declare(var_name, var_type, is_const=True, value=value_node.leaf)
        
    def visit_Assignment(self, node):
        var_name = node.children[0].leaf
        expr_node = node.children[1]
        
        # Check if variable exists
        symbol = self.symbol_table.lookup(var_name)
        
        # Check if trying to assign to constant
        if symbol.is_const:
            raise SemanticError(f"'{var_name}' é uma constante e não pode ser alterada")
            
        # Check type compatibility
        expr_type = self.get_expression_type(expr_node)
        if not self.check_type_compatibility(symbol.type, expr_type):
            raise SemanticError(f"Erro de tipo em '{var_name}'")
            
    def visit_If(self, node):
        # Check condition type
        condition_type = self.get_expression_type(node.children[0])
        if condition_type != 'bool':
            raise SemanticError("'IF' deve ser booleano")
            
        # Create new scope for if body
        self.symbol_table.enter_scope()
        self.visit(node.children[1])  # Visit if body
        self.symbol_table.exit_scope()
        
        # If there's an else clause
        if len(node.children) > 2:
            self.symbol_table.enter_scope()
            self.visit(node.children[2])  # Visit else body
            self.symbol_table.exit_scope()
            
    def visit_While(self, node):
        # Check condition type
        condition_type = self.get_expression_type(node.children[0])
        if condition_type != 'bool':
            raise SemanticError("While deve ser booleano")
            
        # Create new scope for while body
        self.symbol_table.enter_scope()
        self.visit(node.children[1])  # Visit while body
        self.symbol_table.exit_scope()
        
    def get_expression_type(self, node):
        if node.type == 'Literal':
            return self.get_literal_type(node.leaf)
        elif node.type == 'ID':
            symbol = self.symbol_table.lookup(node.leaf)
            return symbol.type
        elif node.type in ['BinOp', 'UnaryOp']:
            return self.get_operation_type(node)
        elif node.type in ['LogicalOp', 'RelationalOp']:
            return 'bool'
        raise SemanticError(f"Tipo desconhecido: {node.type}")
        
    def get_literal_type(self, value):
        if isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, str):
            return 'str'
        elif value in ['true', 'false']:
            return 'bool'
        raise SemanticError(f"Tipo literal desconhecido para o valor: {value}")
        
    def get_operation_type(self, node):
        if node.type == 'UnaryOp':
            if node.leaf == '-':
                operand_type = self.get_expression_type(node.children[0])
                if operand_type in ['int', 'float']:
                    return operand_type
                raise SemanticError("Menos unário aplicado a tipo inválido")
            elif node.leaf == '!':
                return 'bool'
                
        # Binary operations
        left_type = self.get_expression_type(node.children[0])
        right_type = self.get_expression_type(node.children[1])
        
        if node.leaf in ['+', '-', '*', '/']:
            if left_type == right_type and left_type in ['int', 'float']:
                return left_type
            if 'float' in [left_type, right_type] and left_type in ['int', 'float'] and right_type in ['int', 'float']:
                return 'float'
            raise SemanticError(f"Tipo de operando inválido para o operador '{node.leaf}'")
            
    def check_type_compatibility(self, expected_type, actual_type):
        if expected_type == actual_type:
            return True
        # Allow int to float conversion
        if expected_type == 'float' and actual_type == 'int':
            return True
        return False
