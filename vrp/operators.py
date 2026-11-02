"""
vrp/operators.py — Operadores genéticos: Crossover OX1 e Mutação Swap.
"""
import random
from typing import List, Optional


def crossover_ox1(pai1: List[int], pai2: List[int]) -> List[int]:
    """
    Ordered Crossover (OX1).

    Preserva sub-rotas relativas sem duplicar genes:
    1. Copia segmento aleatório de pai1 para o filho.
    2. Preenche o restante com os genes de pai2 na ordem em que aparecem.
    """
    tamanho = len(pai1)
    a, b = sorted(random.sample(range(tamanho), 2))

    filho: List[Optional[int]] = [None] * tamanho
    filho[a:b + 1] = pai1[a:b + 1]

    pos_filho = (b + 1) % tamanho
    for gene in pai2:
        if gene not in filho:
            filho[pos_filho] = gene
            pos_filho = (pos_filho + 1) % tamanho

    return [g for g in filho if g is not None]


def mutacao_swap(cromossomo: List[int], taxa_mutacao: float = 0.15) -> List[int]:
    """
    Swap Mutation.

    Com probabilidade `taxa_mutacao`, troca a posição de dois genes aleatórios.
    """
    copia = list(cromossomo)
    if random.random() < taxa_mutacao:
        idx1, idx2 = random.sample(range(len(copia)), 2)
        copia[idx1], copia[idx2] = copia[idx2], copia[idx1]
    return copia
