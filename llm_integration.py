from dataclasses import dataclass
from typing import Any, Dict, List

# ==============================================================================
# 1. MODELOS DE DADOS E CONTRATOS
# ==============================================================================

CAPACIDADE_MAXIMA_KG = 45.0

PROMPT_SISTEMA = (
    "Você é o assistente de inteligência artificial logística 'HealthRoute AI'. "
    "Sua função é converter dados brutos de otimização de rotas hospitalares em "
    "instruções claras, organizadas e empáticas para os motoristas da frota médica."
)

ROTAS_OTIMIZADAS: Dict[str, Dict[str, Any]] = {
    "Veiculo_1": {
        "motorista": "Carlos Silva",
        "veiculo_id": "V-101",
        "destinos": [
            {"nome": "Depósito Central", "tipo": "Origem", "critico": False, "demanda_kg": 0},
            {"nome": "Clínica F", "tipo": "Entrega", "critico": True, "demanda_kg": 12, "item": "Vacinas Termossensíveis"},
            {"nome": "Posto D", "tipo": "Entrega", "critico": False, "demanda_kg": 25, "item": "Kits de Curativo"},
            {"nome": "Depósito Central", "tipo": "Retorno", "critico": False, "demanda_kg": 0},
        ],
        "distancia_total_km": 25.55,
        "carga_total_kg": 37.0,
    },
    "Veiculo_2": {
        "motorista": "Ana Souza",
        "veiculo_id": "V-102",
        "destinos": [
            {"nome": "Depósito Central", "tipo": "Origem", "critico": False, "demanda_kg": 0},
            {"nome": "Hospital C (Emergência)", "tipo": "Entrega", "critico": True, "demanda_kg": 10, "item": "Bolsas de Sangue O-"},
            {"nome": "Posto B", "tipo": "Entrega", "critico": False, "demanda_kg": 20, "item": "Medicamentos Gerais"},
            {"nome": "Depósito Central", "tipo": "Retorno", "critico": False, "demanda_kg": 0},
        ],
        "distancia_total_km": 21.81,
        "carga_total_kg": 30.0,
    },
    "Veiculo_3": {
        "motorista": "Roberto Lima",
        "veiculo_id": "V-103",
        "destinos": [
            {"nome": "Depósito Central", "tipo": "Origem", "critico": False, "demanda_kg": 0},
            {"nome": "Hospital A (UTI)", "tipo": "Entrega", "critico": True, "demanda_kg": 15, "item": "Anestésicos Críticos"},
            {"nome": "Hospital E", "tipo": "Entrega", "critico": False, "demanda_kg": 30, "item": "Soro Fisiológico"},
            {"nome": "Depósito Central", "tipo": "Retorno", "critico": False, "demanda_kg": 0},
        ],
        "distancia_total_km": 15.01,
        "carga_total_kg": 45.0,
    },
}

# ==============================================================================
# 2. GERADOR DETERMINÍSTICO DE MANIFESTOS (FALLBACK / MOCK LOCAL)
# ==============================================================================

def formatar_passo(indice: int, destino: Dict[str, Any], carga_total: float) -> str:
    tipo = destino["tipo"]
    nome = destino["nome"]

    if tipo == "Origem":
        return (
            f"{indice}. 🏬 **Partida ({nome}):** Conferir carregamento total "
            f"({carga_total:.1f} kg) e temperatura da câmara fria."
        )

    if tipo == "Retorno":
        return f"{indice}. 🏬 **Retorno ao {nome}:** Estacionar na baia de carga e dar baixa no sistema."

    # Entregas regulares ou críticas
    eh_critico = destino.get("critico", False)
    alerta = "🚨 **[ALERTA DE PRIORIDADE CRÍTICA]** " if eh_critico else "📦 [ENTREGA REGULAR] "
    item = destino.get("item", "Não especificado")
    demanda = destino.get("demanda_kg", 0)

    protocolo = (
        "Despacho urgente. Entregar em mãos ao chefe de plantão com assinatura digital."
        if eh_critico
        else "Entrega padrão no almoxarifado hospitalar."
    )

    return (
        f"{indice}. {alerta}**Parada em {nome}:**\n"
        f"   - **Insumo:** {item} ({demanda} kg)\n"
        f"   - **Protocolo:** {protocolo}"
    )


def gerar_manifesto_local(dados_veiculo: Dict[str, Any]) -> str:
    """Gera o manifesto usando formatação determinística local."""
    veiculo = dados_veiculo["veiculo_id"]
    motorista = dados_veiculo["motorista"]
    distancia = dados_veiculo["distancia_total_km"]
    carga = dados_veiculo["carga_total_kg"]
    ocupacao = (carga / CAPACIDADE_MAXIMA_KG) * 100

    linhas = [
        f"📋 **MANIFESTO DE TRANSPORTE MÉDICO - VEÍCULO {veiculo}**",
        f"👤 **Motorista Responsável:** {motorista}",
        f"📊 **Resumo de Rota:** {distancia:.1f} km | Carga: {carga:.1f} kg (Capacidade: {ocupacao:.0f}%)",
        "-" * 50,
        "🗺️ **INSTRUÇÕES OPERACIONAIS PASSO A PASSO:\n",
    ]

    for i, destino in enumerate(dados_veiculo["destinos"], start=1):
        linhas.append(formatar_passo(i, destino, carga))

    return "\n".join(linhas)

# ==============================================================================
# 3. CAMADA DE PROMPT PARA LLM (PRODUÇÃO)
# ==============================================================================

def construir_payload_llm(dados_veiculo: Dict[str, Any]) -> Dict[str, str]:
    """
    Estrutura a mensagem pronta para ser enviada a APIs como OpenAI, Gemini ou Claude.
    """
    prompt_usuario = (
        f"Gere o manifesto de rota operacional a partir destes dados de telemetria:\n"
        f"- Veículo: {dados_veiculo['veiculo_id']}\n"
        f"- Motorista: {dados_veiculo['motorista']}\n"
        f"- Distância prevista: {dados_veiculo['distancia_total_km']} km\n"
        f"- Peso alocado: {dados_veiculo['carga_total_kg']} kg (Máx: {CAPACIDADE_MAXIMA_KG} kg)\n"
        f"- Pontos e paradas: {dados_veiculo['destinos']}\n\n"
        f"Instruções: Priorize visualmente alertas críticos para o motorista."
    )

    return {
        "system": PROMPT_SISTEMA,
        "user": prompt_usuario,
    }

# ==============================================================================
# 4. EXECUÇÃO
# ==============================================================================

if __name__ == "__main__":
    for v_id, dados in ROTAS_OTIMIZADAS.items():
        print(gerar_manifesto_local(dados))
        print("\n" + "=" * 50 + "\n")