"""Pacote LLM — Integração com IA Generativa para manifestos, relatórios e Q&A."""
from .manifesto import gerar_manifesto_local, formatar_passo, construir_dados_veiculo
from .prompts import PROMPT_SISTEMA, construir_payload_llm
from .relatorio import gerar_relatorio_eficiencia
from .melhorias import sugerir_melhorias_processo
from .qa_interface import iniciar_qa_interativo, responder_pergunta

__all__ = [
    "gerar_manifesto_local", "formatar_passo", "construir_dados_veiculo",
    "PROMPT_SISTEMA", "construir_payload_llm",
    "gerar_relatorio_eficiencia",
    "sugerir_melhorias_processo",
    "iniciar_qa_interativo", "responder_pergunta",
]
