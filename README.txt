Compilador LPMS
======================

Este é um analisador léxico para a linguagem LPMS implementado em Python usando PLY.

O compilador funciona em sistemas Linux. Utilizamos o NASM para gerar o executável a partir de um código assembly.

Requisitos:
- Python 3.6 ou superior
- PLY (Python Lex-Yacc)
- sudo apt-get install nasm build-essential
- sudo apt-get install gcc-multilib

Instalação:
1. Instale os requirementos usando pip:
   pip install -r requirements.txt

Execução:
1. Para executar o compilador:
   python main.py programs/teste1.lps

O programa irá ler o arquivo de entrada e imprimir na saída padrão a árvore de derivação, codigo de três Endereços e informações sobre
a compilação.

Os códigos e executáveis vão para a pasta /output e os programas de teste estão na pasta /programs

******** Nos nossos testes somente o arquivo "teste1.lps" nos rendeu um executável totalmente funcional. ********

Exemplo de saída:

0: DECLARE a
1: DECLARE b
2: INPUT a
3: INPUT b
4: DECLARE result
5: t0 = b * 2.5
6: t1 = a + t0
7: result = t1
8: PRINT result

Referências utilizadas:
- Documentação do PLY: https://www.dabeaz.com/ply/
- Livro do Dragão (Compilers: Principles, Techniques, and Tools) 