"""
vrp/genetic_algorithm.py — Algoritmo Genético principal para o VRP médico.
"""
import random
from typing import List, Tuple

from .data import PONTOS, NUM_VEICULOS
from .fitness import calcular_fitness
from .operators import crossover_ox1, mutacao_swap


def executar_ag(
    tam_populacao: int = 50,
    geracoes: int = 100,
    elitismo_k: int = 5,
) -> Tuple[List[int], float, List[float]]:
    """
    Executa o Algoritmo Genético para o VRP.

    Retorna:
        melhor_solucao  : sequência ótima de entregas
        melhor_fitness  : custo total (distância + penalidades)
        historico_fitness: melhor fitness encontrado a cada geração (para gráfico)
    """
    clientes = [p for p in PONTOS.keys() if p != 0]
    populacao = [random.sample(clientes, len(clientes)) for _ in range(tam_populacao)]

    melhor_solucao: List[int] = []
    melhor_fitness = float("inf")
    historico_fitness: List[float] = []

    for _ in range(geracoes):
        # --- Avaliação ---
        avaliados = [(ind, calcular_fitness(ind)) for ind in populacao]
        avaliados.sort(key=lambda item: item[1])

        # --- Atualiza melhor global ---
        if avaliados[0][1] < melhor_fitness:
            melhor_fitness = avaliados[0][1]
            melhor_solucao = list(avaliados[0][0])

        historico_fitness.append(melhor_fitness)

        # --- Elitismo: preserva os K melhores ---
        nova_populacao = [ind for ind, _ in avaliados[:elitismo_k]]

        # --- Reprodução por Torneio ---
        pool_torneio = avaliados[:max(elitismo_k * 2, 10)]
        while len(nova_populacao) < tam_populacao:
            candidatos_p1 = random.sample(pool_torneio, 2)
            pai1 = min(candidatos_p1, key=lambda x: x[1])[0]

            candidatos_p2 = random.sample(pool_torneio, 2)
            pai2 = min(candidatos_p2, key=lambda x: x[1])[0]

            filho = crossover_ox1(pai1, pai2)
            filho = mutacao_swap(filho)
            nova_populacao.append(filho)

        populacao = nova_populacao

    return melhor_solucao, melhor_fitness, historico_fitness
