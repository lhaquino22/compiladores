from parser import parse_file

def analyze_file(filename):
    try:
        # Chama o parser que vai gerar a AST
        ast = parse_file(filename)
        print(ast)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{filename}' não encontrado.")
    except Exception as e:
        print(f"Erro ao processar arquivo: {str(e)}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Uso: python main.py arquivo.lps")
    else:
        analyze_file(sys.argv[1])