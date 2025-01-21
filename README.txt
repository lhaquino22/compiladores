Analisador Léxico LPMS
======================

Este é um analisador léxico para a linguagem LPMS implementado em Python usando PLY.

Requisitos:
- Python 3.6 ou superior
- PLY (Python Lex-Yacc)

Instalação:
1. Instale os requirementos usando pip:
   pip install -r requirements.txt

Execução:
1. Para executar o compilador:
   python main.py arquivo.lps

O programa irá ler o arquivo de entrada e imprimir na saída padrão a árvore de derivação e o codigo de três Endereços.

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