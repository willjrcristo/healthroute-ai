"""
vrp/fitness.py — Função de avaliação (fitness) do VRP com penalidades ponderadas.
"""
from typing import List
import numpy as np

from .data import PONTOS, NUM_VEICULOS, CAPACIDADE_VEICULO, AUTONOMIA_VEICULO, MATRIZ_DISTANCIAS, PESOS_PENALIDADE


def calcular_fitness(cromossomo: List[int]) -> float:
    """
    Avalia a sequência de entregas dividindo-a igualmente entre os veículos.

    Retorna a distância total percorrida pela frota somada a penalidades por:
    - Estouro de capacidade (kg)
    - Estouro de autonomia (km)
    - Pontos críticos atendidos em posições tardias da rota
    """
    distancia_total = 0.0
    penalidade_capacidade = 0.0
    penalidade_autonomia = 0.0
    penalidade_prioridade = 0.0

    entregas = [p for p in cromossomo if p != 0]
    rotas_veiculos = np.array_split(entregas, NUM_VEICULOS)

    for rota in rotas_veiculos:
        if len(rota) == 0:
            continue

        carga_atual = 0.0
        distancia_rota = 0.0
        ponto_atual = 0  # Parte do depósito central

        for ordem_entrega, proximo_ponto in enumerate(rota):
            distancia_rota += MATRIZ_DISTANCIAS[ponto_atual][proximo_ponto]
            carga_atual += PONTOS[proximo_ponto]["demanda"]

            # Penalidade: ponto crítico atendido em posição avançada
            if PONTOS[proximo_ponto]["critico"]:
                penalidade_prioridade += ordem_entrega * PESOS_PENALIDADE["prioridade"]

            ponto_atual = proximo_ponto

        # Retorno ao depósito
        distancia_rota += MATRIZ_DISTANCIAS[ponto_atual][0]
        distancia_total += distancia_rota

        # Penalidade por estouro de restrições
        if carga_atual > CAPACIDADE_VEICULO:
            penalidade_capacidade += (carga_atual - CAPACIDADE_VEICULO) * PESOS_PENALIDADE["capacidade"]
        if distancia_rota > AUTONOMIA_VEICULO:
            penalidade_autonomia += (distancia_rota - AUTONOMIA_VEICULO) * PESOS_PENALIDADE["autonomia"]

    return distancia_total + penalidade_capacidade + penalidade_autonomia + penalidade_prioridade
