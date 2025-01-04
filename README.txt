Analisador Léxico LPMS
======================

Este é um analisador léxico para a linguagem LPMS implementado em Python usando PLY.

Requisitos:
- Python 3.6 ou superior
- PLY (Python Lex-Yacc)

Instalação:
1. Instale o PLY usando pip:
   pip install ply

Execução:
1. Para executar o analisador léxico:
   python main.py arquivo.lps

O programa irá ler o arquivo de entrada e imprimir na saída padrão cada token encontrado
no formato <tipo_token, valor_token>.

Exemplo de saída:
<PROGRAM, Program>
<ID, Fatorial>
<LBRACE, {>
...

Referências utilizadas:
- Documentação do PLY: https://www.dabeaz.com/ply/
- Livro do Dragão (Compilers: Principles, Techniques, and Tools) 