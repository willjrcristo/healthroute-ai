"""Pacote VRP — Motor de Otimização de Rotas Médicas."""
from .data import PONTOS, NUM_VEICULOS, CAPACIDADE_VEICULO, AUTONOMIA_VEICULO, MATRIZ_DISTANCIAS
from .fitness import calcular_fitness
from .operators import crossover_ox1, mutacao_swap
from .genetic_algorithm import executar_ag

__all__ = [
    "PONTOS", "NUM_VEICULOS", "CAPACIDADE_VEICULO", "AUTONOMIA_VEICULO",
    "MATRIZ_DISTANCIAS", "calcular_fitness", "crossover_ox1", "mutacao_swap",
    "executar_ag",
]
