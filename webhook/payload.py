"""
webhook/payload.py — Geração e envio de payload JSON para n8n / sistemas externos.
"""
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


def gerar_payload_n8n(
    rotas_detalhadas: List[Dict[str, Any]],
    custo_fitness: float,
    historico_fitness: List[float],
) -> Dict[str, Any]:
    """
    Gera o payload JSON estruturado compatível com o nó Webhook do n8n.
    """
    dist_total = sum(r.get("distancia_km", 0) for r in rotas_detalhadas)
    carga_total = sum(r.get("carga_kg", 0) for r in rotas_detalhadas)
    ocup_media = sum(r.get("ocupacao_pct", 0) for r in rotas_detalhadas) / max(len(rotas_detalhadas), 1)

    rotas_payload = []
    for r in rotas_detalhadas:
        rotas_payload.append({
            "veiculo": int(r.get("veiculo", 0)),
            "identificador": str(r.get("identificador", "")),
            "motorista": str(r.get("motorista", "")),
            "caminho_ids": [int(x) for x in r.get("caminho", [])],
            "pontos_nomes": [str(x) for x in r.get("pontos_nomes", [])],
            "distancia_km": float(r.get("distancia_km", 0)),
            "carga_kg": float(r.get("carga_kg", 0)),
            "ocupacao_pct": float(r.get("ocupacao_pct", 0)),
        })

    return {
        "timestamp": datetime.now().isoformat(),
        "fonte": "HealthRoute AI — GA VRP Optimizer",
        "algoritmo": {
            "nome": "GA_VRP_OX1_Swap",
            "geracoes": len(historico_fitness),
            "fitness_inicial": round(historico_fitness[0], 4) if historico_fitness else None,
            "fitness_final": round(custo_fitness, 4),
        },
        "metricas": {
            "distancia_total_km": round(dist_total, 2),
            "carga_total_kg": round(carga_total, 1),
            "ocupacao_media_pct": round(ocup_media, 1),
            "num_veiculos": len(rotas_detalhadas),
        },
        "rotas": rotas_payload,
    }


def disparar_webhook(
    payload: Dict[str, Any],
    url: Optional[str] = None,
    timeout_s: int = 10,
) -> bool:
    """
    Envia o payload via HTTP POST para o webhook do n8n.
    """
    webhook_url = url or os.getenv("N8N_WEBHOOK_URL", "")

    if not webhook_url:
        print("[webhook] N8N_WEBHOOK_URL não configurada. Payload gerado mas não enviado.")
        print("[webhook] Configure a variável N8N_WEBHOOK_URL no arquivo .env")
        _salvar_payload_local(payload)
        return False

    try:
        import urllib.request
        import urllib.error

        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            status = resp.getcode()
            print(f"[webhook] ✅ Payload enviado com sucesso! Status HTTP: {status}")
            print(f"[webhook] URL: {webhook_url}")
            return True

    except Exception as e:
        print(f"[webhook] ⚠️ Falha ao enviar webhook: {e}")
        print("[webhook] Salvando payload localmente como fallback...")
        _salvar_payload_local(payload)
        return False


def _salvar_payload_local(payload: Dict[str, Any]) -> None:
    """Salva o payload em output/webhook_payload.json como fallback."""
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    caminho = os.path.join(output_dir, "webhook_payload.json")
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"[webhook] Payload salvo em: {caminho}")
