"""
vrp/data.py — Dados estáticos do problema VRP: pontos, parâmetros e matriz de distâncias.
"""
from typing import Dict
import numpy as np

# ==============================================================================
# PONTOS DE ENTREGA
# Estrutura: id -> {"pos": (x, y), "demanda": kg, "critico": bool, "nome": str}
# ==============================================================================

PONTOS: Dict[int, dict] = {
    0: {"pos": (0, 0), "demanda": 0,  "critico": False, "nome": "Depósito Central"},
    1: {"pos": (2, 5), "demanda": 15, "critico": True,  "nome": "Hospital A (UTI)"},
    2: {"pos": (6, 3), "demanda": 20, "critico": False, "nome": "Posto B"},
    3: {"pos": (8, 7), "demanda": 10, "critico": True,  "nome": "Hospital C (Emergência)"},
    4: {"pos": (1, 8), "demanda": 25, "critico": False, "nome": "Posto D"},
    5: {"pos": (5, 2), "demanda": 30, "critico": False, "nome": "Hospital E"},
    6: {"pos": (7, 9), "demanda": 12, "critico": True,  "nome": "Clínica F"},
}

# ==============================================================================
# PARÂMETROS OPERACIONAIS DA FROTA
# ==============================================================================

NUM_VEICULOS: int = 3
CAPACIDADE_VEICULO: float = 45.0   # kg máximos por veículo
AUTONOMIA_VEICULO: float = 35.0    # km máximos por veículo

MOTORISTAS = {
    1: {"nome": "Carlos Silva", "veiculo_id": "V-101"},
    2: {"nome": "Ana Souza",    "veiculo_id": "V-102"},
    3: {"nome": "Roberto Lima", "veiculo_id": "V-103"},
}

ITENS_ENTREGA = {
    1: "Anestésicos Críticos",
    2: "Medicamentos Gerais",
    3: "Bolsas de Sangue O-",
    4: "Kits de Curativo",
    5: "Soro Fisiológico",
    6: "Vacinas Termossensíveis",
}

# Pesos de Penalização (Fitness)
PESOS_PENALIDADE = {
    "capacidade": 1000.0,
    "autonomia":  1000.0,
    "prioridade":   50.0,
}

# ==============================================================================
# MATRIZ DE DISTÂNCIAS (PRÉ-CALCULADA)
# ==============================================================================

def gerar_matriz_distancias(pontos: Dict[int, dict]) -> np.ndarray:
    """Calcula a matriz euclidiana de distâncias entre todos os pontos."""
    n = len(pontos)
    matriz = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            p1 = np.array(pontos[i]["pos"])
            p2 = np.array(pontos[j]["pos"])
            matriz[i][j] = np.linalg.norm(p1 - p2)
    return matriz


MATRIZ_DISTANCIAS = gerar_matriz_distancias(PONTOS)
