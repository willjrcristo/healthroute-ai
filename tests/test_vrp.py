"""
tests/test_vrp.py — Testes automatizados do módulo VRP.
"""
import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
import numpy as np

from vrp.data import PONTOS, MATRIZ_DISTANCIAS, NUM_VEICULOS, CAPACIDADE_VEICULO, AUTONOMIA_VEICULO, gerar_matriz_distancias
from vrp.fitness import calcular_fitness
from vrp.operators import crossover_ox1, mutacao_swap
from vrp.genetic_algorithm import executar_ag


# ─── Fixtures ─────────────────────────────────────────────────────────────── #

@pytest.fixture
def clientes():
    """Lista de IDs de clientes (todos os pontos exceto o depósito 0)."""
    return [p for p in PONTOS.keys() if p != 0]


@pytest.fixture
def cromossomo_valido(clientes):
    """Um cromossomo válido gerado aleatoriamente."""
    random.seed(42)
    return random.sample(clientes, len(clientes))


# ─── Testes de Dados ─────────────────────────────────────────────────────── #

def test_pontos_tem_deposito():
    """O ponto 0 deve existir e ser o depósito central."""
    assert 0 in PONTOS
    assert PONTOS[0]["demanda"] == 0
    assert PONTOS[0]["critico"] is False


def test_matriz_distancias_shape():
    """A matriz de distâncias deve ser quadrada e ter dimensão = num_pontos."""
    n = len(PONTOS)
    assert MATRIZ_DISTANCIAS.shape == (n, n)


def test_matriz_distancias_diagonal_zero():
    """A diagonal principal da matriz deve ser zero (distância de um ponto para si mesmo)."""
    for i in range(len(PONTOS)):
        assert MATRIZ_DISTANCIAS[i][i] == pytest.approx(0.0)


def test_matriz_distancias_simetrica():
    """A matriz deve ser simétrica: dist(A, B) == dist(B, A)."""
    n = len(PONTOS)
    for i in range(n):
        for j in range(n):
            assert MATRIZ_DISTANCIAS[i][j] == pytest.approx(MATRIZ_DISTANCIAS[j][i], abs=1e-9)


def test_gerar_matriz_distancias_custom():
    """Testa gerar_matriz_distancias com um conjunto mínimo de pontos."""
    pontos_teste = {
        0: {"pos": (0, 0), "demanda": 0, "critico": False, "nome": "Dep"},
        1: {"pos": (3, 4), "demanda": 10, "critico": False, "nome": "A"},
    }
    m = gerar_matriz_distancias(pontos_teste)
    assert m.shape == (2, 2)
    assert m[0][1] == pytest.approx(5.0)  # hipotenusa 3-4-5
    assert m[0][0] == pytest.approx(0.0)


# ─── Testes de Fitness ───────────────────────────────────────────────────── #

def test_fitness_retorna_float_positivo(cromossomo_valido):
    """A função fitness deve retornar um float não-negativo."""
    resultado = calcular_fitness(cromossomo_valido)
    assert isinstance(resultado, float)
    assert resultado >= 0.0


def test_fitness_cobre_todos_os_clientes(cromossomo_valido, clientes):
    """O cromossomo passado para fitness deve cobrir todos os clientes."""
    assert sorted(cromossomo_valido) == sorted(clientes)


# ─── Testes dos Operadores Genéticos ────────────────────────────────────── #

def test_crossover_ox1_sem_duplicatas(cromossomo_valido, clientes):
    """O filho do crossover OX1 não deve ter genes duplicados."""
    random.seed(99)
    pai2 = random.sample(clientes, len(clientes))
    filho = crossover_ox1(cromossomo_valido, pai2)
    assert len(filho) == len(set(filho)), "Filho OX1 contém genes duplicados"


def test_crossover_ox1_mesmo_tamanho(cromossomo_valido, clientes):
    """O filho deve ter o mesmo tamanho que os pais."""
    random.seed(7)
    pai2 = random.sample(clientes, len(clientes))
    filho = crossover_ox1(cromossomo_valido, pai2)
    assert len(filho) == len(cromossomo_valido)


def test_crossover_ox1_contem_todos_clientes(cromossomo_valido, clientes):
    """O filho deve conter exatamente os mesmos genes dos pais."""
    random.seed(13)
    pai2 = random.sample(clientes, len(clientes))
    filho = crossover_ox1(cromossomo_valido, pai2)
    assert sorted(filho) == sorted(clientes)


def test_mutacao_swap_mesmo_tamanho(cromossomo_valido):
    """A mutação não deve alterar o tamanho do cromossomo."""
    random.seed(5)
    resultado = mutacao_swap(cromossomo_valido, taxa_mutacao=1.0)
    assert len(resultado) == len(cromossomo_valido)


def test_mutacao_swap_mesmos_genes(cromossomo_valido, clientes):
    """A mutação deve preservar o conjunto de genes."""
    random.seed(3)
    resultado = mutacao_swap(cromossomo_valido, taxa_mutacao=1.0)
    assert sorted(resultado) == sorted(clientes)


# ─── Testes do Algoritmo Genético ───────────────────────────────────────── #

def test_ag_retorna_todos_os_clientes(clientes):
    """O AG deve retornar uma solução que contém todos os clientes."""
    random.seed(0)
    melhor, custo, historico = executar_ag(tam_populacao=10, geracoes=5)
    assert sorted(melhor) == sorted(clientes)


def test_ag_retorna_float_positivo():
    """O custo retornado pelo AG deve ser um float positivo."""
    random.seed(1)
    _, custo, _ = executar_ag(tam_populacao=10, geracoes=5)
    assert isinstance(custo, float)
    assert custo >= 0.0


def test_ag_retorna_historico_fitness():
    """O AG deve retornar o histórico de fitness com comprimento igual ao número de gerações."""
    random.seed(2)
    geracoes = 10
    _, _, historico = executar_ag(tam_populacao=10, geracoes=geracoes)
    assert len(historico) == geracoes


def test_ag_fitness_nao_piora():
    """O melhor fitness nunca deve piorar de uma geração para a próxima."""
    random.seed(42)
    _, _, historico = executar_ag(tam_populacao=20, geracoes=20)
    for i in range(1, len(historico)):
        assert historico[i] <= historico[i - 1] + 1e-9, (
            f"Fitness piorou na geração {i}: {historico[i-1]:.4f} → {historico[i]:.4f}"
        )
