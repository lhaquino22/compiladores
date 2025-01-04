from lexer import lexer

def analyze_file(filename):
    try:
        with open(filename, 'r') as file:
            data = file.read()
        
        lexer.input(data)
        
        # Tokenização
        while True:
            tok = lexer.token()
            if not tok:
                break
            print(f"<{tok.type}, {tok.value}>")
            
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