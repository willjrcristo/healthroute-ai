"""
llm/melhorias.py — Análise de gargalos e sugestões de melhoria no processo logístico.
"""
from typing import Any, Dict, List

CAPACIDADE_VEICULO = 45.0


def sugerir_melhorias_processo(
    rotas_detalhadas: List[Dict[str, Any]],
    historico_fitness: List[float],
) -> str:
    """
    Analisa os resultados da otimização e gera sugestões de melhoria.

    Identifica:
    - Veículo mais sobrecarregado
    - Desequilíbrio de carga entre veículos
    - Tendência de convergência do AG
    - Parâmetros sugeridos para próxima execução
    """
    if not rotas_detalhadas:
        return "Sem dados de rotas para análise."

    # Análise de carga
    cargas = [(r["identificador"], r["carga_kg"]) for r in rotas_detalhadas]
    cargas.sort(key=lambda x: x[1], reverse=True)
    max_carga = cargas[0][1] if cargas else 0
    min_carga = cargas[-1][1] if cargas else 0
    desequilibrio = ((max_carga - min_carga) / max_carga * 100) if max_carga > 0 else 0

    # Análise de distância
    distancias = [(r["identificador"], r["distancia_km"]) for r in rotas_detalhadas]
    distancias.sort(key=lambda x: x[1], reverse=True)

    # Análise de convergência
    total_ger = len(historico_fitness)
    ponto_conv = total_ger
    if total_ger > 10:
        for i in range(10, total_ger):
            variacao = abs(historico_fitness[i] - historico_fitness[i - 10]) / (historico_fitness[i - 10] + 1e-9)
            if variacao < 0.005:
                ponto_conv = i
                break

    sugestoes = []

    # 1. Desequilíbrio de carga
    if desequilibrio > 20:
        sugestoes.append(
            f"⚠️  DESEQUILÍBRIO DE CARGA ({desequilibrio:.0f}%): "
            f"{cargas[0][0]} carrega {max_carga:.0f}kg vs {cargas[-1][0]} com {min_carga:.0f}kg. "
            "Sugestão: Redistribuir 1-2 pontos de entrega do veículo mais carregado."
        )
    else:
        sugestoes.append(
            f"✅ CARGA BALANCEADA: Desequilíbrio de {desequilibrio:.0f}% — dentro do limite aceitável (20%)."
        )

    # 2. Veículo mais sobrecarregado
    if max_carga > CAPACIDADE_VEICULO * 0.90:
        sugestoes.append(
            f"🔴 ATENÇÃO: {cargas[0][0]} opera com {max_carga:.0f}kg "
            f"({max_carga / CAPACIDADE_VEICULO * 100:.0f}% da capacidade). "
            "Considerar adicionar um 4º veículo para rotas futuras."
        )

    # 3. Rota mais longa
    sugestoes.append(
        f"📍 ROTA MAIS LONGA: {distancias[0][0]} percorre {distancias[0][1]:.1f} km. "
        "Avaliar depósito intermediário na região leste do grid para reduzir deslocamento."
    )

    # 4. Convergência do AG
    if ponto_conv < total_ger * 0.5:
        sugestoes.append(
            f"🧬 CONVERGÊNCIA ANTECIPADA: AG convergiu na geração {ponto_conv}/{total_ger} "
            f"({ponto_conv / total_ger * 100:.0f}% do total). "
            "Sugestão: Aumentar taxa de mutação (0.15 → 0.25) ou reduzir gerações para economizar tempo."
        )
    else:
        sugestoes.append(
            f"🧬 CONVERGÊNCIA TARDIA: AG ainda melhorava até a geração {ponto_conv}/{total_ger}. "
            "Sugestão: Aumentar gerações (100 → 150) ou tamanho da população (50 → 80) "
            "para explorar mais o espaço de soluções."
        )

    # 5. Otimização futura
    sugestoes.append(
        "💡 MELHORIA FUTURA: Implementar janelas de tempo (time windows) por ponto de entrega "
        "para modelar restrições de horário hospitalar (ex: UTI — entregas apenas até 8h)."
    )

    linhas = [
        "=" * 65,
        "  HEALTHROUTE AI — SUGESTÕES DE MELHORIA NO PROCESSO",
        "=" * 65,
        "",
    ]
    for i, s in enumerate(sugestoes, start=1):
        linhas.append(f"  {i}. {s}")
        linhas.append("")
    linhas.append("=" * 65)

    return "\n".join(linhas)
