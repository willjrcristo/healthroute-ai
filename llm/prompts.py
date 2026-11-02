"""
llm/prompts.py — System prompt e construção de payload para APIs LLM.
"""
from typing import Any, Dict

PROMPT_SISTEMA = (
    "Você é o assistente de inteligência artificial logística 'HealthRoute AI'. "
    "Sua função é converter dados brutos de otimização de rotas hospitalares em "
    "instruções claras, organizadas e empáticas para os motoristas da frota médica. "
    "Priorize sempre os pontos críticos e use linguagem direta e profissional."
)

CAPACIDADE_MAXIMA_KG = 45.0


def construir_payload_llm(dados_veiculo: Dict[str, Any]) -> Dict[str, str]:
    """
    Estrutura a mensagem pronta para ser enviada a APIs como OpenAI, Gemini ou Groq.

    Retorna um dict com chaves 'system' e 'user'.
    """
    prompt_usuario = (
        f"Gere o manifesto de rota operacional a partir destes dados de telemetria:\n"
        f"- Veículo: {dados_veiculo['veiculo_id']}\n"
        f"- Motorista: {dados_veiculo['motorista']}\n"
        f"- Distância prevista: {dados_veiculo['distancia_total_km']} km\n"
        f"- Peso alocado: {dados_veiculo['carga_total_kg']} kg (Máx: {CAPACIDADE_MAXIMA_KG} kg)\n"
        f"- Pontos e paradas: {dados_veiculo['destinos']}\n\n"
        "Instruções: Priorize visualmente alertas críticos para o motorista. "
        "Use emojis e formatação em markdown para facilitar a leitura no terminal."
    )

    return {
        "system": PROMPT_SISTEMA,
        "user": prompt_usuario,
    }
