from parser import parse_file

from parser import parse_file
from semantic_analyzer import SemanticAnalyzer

def analyze_file(filename):
    try:
        # Parse do arquivo para gerar a AST
        ast = parse_file(filename)
        
        # Análise semântica
        analyzer = SemanticAnalyzer()
        success, errors = analyzer.analyze(ast)
        
        if not success:
            print("Erros semânticos encontrados:")
            for error in errors:
                print(f"- {error}")
        else:
            print("Análise semântica concluída com sucesso!")
            ast.print_tree()
            
    except Exception as e:
        print(f"Erro ao processar arquivo: {str(e)}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Uso: python main.py arquivo.lps")
    else:
        analyze_file(sys.argv[1])