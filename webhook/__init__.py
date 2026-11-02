"""Pacote Webhook — Integração com n8n e sistemas externos."""
from .payload import gerar_payload_n8n, disparar_webhook

__all__ = ["gerar_payload_n8n", "disparar_webhook"]
