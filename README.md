Este repositório apresenta uma implementação em Python de uma simulação de gerenciamento de brinquedos e filas em um parque de diversões, utilizando o algoritmo A* (A-star) como heurística principal para tomada de decisões.

O sistema simula o fluxo de visitantes entre diferentes brinquedos do parque, considerando fatores como distância, tempo de espera nas filas e custo total de deslocamento, buscando sempre o caminho mais eficiente para otimizar a experiência dos usuários e o uso dos recursos do parque.

Algoritmo Utilizado
A* (A-star)
Função de custo:
f(n) = g(n) + h(n)
Onde:
g(n) representa o custo real (tempo de deslocamento + tempo de fila)
h(n) representa uma heurística estimada (distância ou tempo estimado até o próximo brinquedo)
O algoritmo é utilizado para definir a melhor rota entre brinquedos, reduzindo tempo de espera e melhorando o balanceamento das filas.

Funcionalidades

Simulação de um parque de diversões com múltiplos brinquedos
Modelagem de filas de espera para cada atração
Gerenciamento do fluxo de visitantes
Cálculo do melhor caminho entre brinquedos usando A*
Análise de custo baseada em tempo e distância
Estrutura modular e extensível para novas atrações e regras

Tecnologias Utilizadas
Python 3
Estruturas de Dados (listas, filas, grafos)
Algoritmos de Busca Heurística
Programação Orientada a Objetos

Objetivo do Projeto
Aplicar conceitos de Inteligência Artificial
Implementar o algoritmo A* em um cenário prático
Simular problemas reais de otimização e tomada de decisão
Consolidar conhecimentos em estruturas de dados e algoritmos
