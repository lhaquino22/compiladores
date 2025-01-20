from parser import CodeGenerator, TACGenerator, parse_file

from semantic_analyzer import SemanticAnalyzer


def analyze_file(filename):
    try:
        ast = parse_file(filename)
        analyzer = SemanticAnalyzer()
        success, errors = analyzer.analyze(ast)

        if not success:
            print("Erros semânticos encontrados:")
            for error in errors:
                print(f"- {error}")
        else:
            print("Análise semântica concluída com sucesso!")
            ast.print_tree()

            # Gerar TAC
            print("\nCódigo de Três Endereços:")
            generator = TACGenerator()
            ast.generate_tac(generator)
            generator.print_instructions()

    except Exception as e:
        print(f"Erro ao processar arquivo: {str(e)}")
        
def compile_file(input_file, output_file):
    # Parse o arquivo fonte
    ast = parse_file(input_file)
    
    # Análise semântica
    analyzer = SemanticAnalyzer()
    success, errors = analyzer.analyze(ast)
    
    if not success:
        print("Erros semânticos encontrados:")
        for error in errors:
            print(f"- {error}")
        return
        
    # Gera TAC
    tac_gen = TACGenerator()
    ast.generate_tac(tac_gen)
    
    # Gera código Python
    code_gen = CodeGenerator()
    python_code = code_gen.generate_python_code(tac_gen.instructions)
    
    # Otimiza o código
    optimized_code = code_gen.optimize_code(python_code)
    
    # Salva o código gerado
    code_gen.save_to_file(output_file, optimized_code)
    print(f"Código gerado em {output_file}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Uso: python main.py arquivo.lps")
    else:
        analyze_file(sys.argv[1])
        compile_file(sys.argv[1], "output.py")
