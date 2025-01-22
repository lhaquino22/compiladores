import subprocess
from nasm_generator import NASMGenerator
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
        
def compile_to_nasm(input_file, output_file):
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
    
    # Gera código NASM
    nasm_gen = NASMGenerator()
    nasm_code = nasm_gen.generate_nasm(tac_gen.instructions)
    
    # Salva o código NASM
    asm_file = output_file + '.asm'
    nasm_gen.save_to_file(asm_file, nasm_code)
    asm_file = 'output/' + asm_file
    
    # Compila o código NASM para um executável
    obj_file = 'output/' + output_file + '.o'
    exe_file = 'output/' + output_file
    
    try:
        # Compila o arquivo assembly para objeto
        subprocess.run(['nasm', '-f', 'elf32', asm_file, '-o', obj_file], check=True)
        
        # Liga o arquivo objeto para criar o executável
        # Modificado para incluir a libc e usar gcc como linker
        subprocess.run([
            'gcc',
            '-m32',
            obj_file,
            '-o', 
            exe_file,
            '-no-pie'  # Desabilita PIE para compatibilidade
        ], check=True)
        
        print(f"Executável gerado com sucesso: {exe_file}")
        
    except subprocess.CalledProcessError as e:
        print(f"Erro ao compilar: {str(e)}")
    except Exception as e:
        print(f"Erro: {str(e)}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Uso: python main.py arquivo.lps")
    else:
        analyze_file(sys.argv[1])
        compile_to_nasm(sys.argv[1], "output")
