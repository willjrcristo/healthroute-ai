"""
llm/manifesto.py — Geração de manifestos detalhados e briefings operacionais para motoristas,
com controle de flags de envio/compartilhamento e rastreamento de versões.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

CAPACIDADE_MAXIMA_KG = 45.0
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

MOTORISTAS = {
    1: {"nome": "Carlos Silva",  "veiculo_id": "V-101", "modelo": "Renault Kangoo", "placa": "BRA-2E19"},
    2: {"nome": "Ana Souza",     "veiculo_id": "V-102", "modelo": "Fiat Fiorino",   "placa": "RIO-4F32"},
    3: {"nome": "Roberto Lima",  "veiculo_id": "V-103", "modelo": "Mercedes-Benz Sprinter", "placa": "ESP-8H77"},
}

ITENS_ENTREGA = {
    1: "Anestésicos Críticos",
    2: "Medicamentos Gerais",
    3: "Bolsas de Sangue O-",
    4: "Kits de Curativo",
    5: "Soro Fisiológico",
    6: "Vacinas Termossensíveis",
}


def formatar_passo(indice: int, destino: Dict[str, Any], carga_total: float) -> str:
    """Formata um passo da rota como instrução textual para o motorista."""
    tipo = destino["tipo"]
    nome = destino["nome"]

    if tipo == "Origem":
        return (
            f"{indice}. 🏬 **Partida ({nome}):** Conferir carregamento total "
            f"({carga_total:.1f} kg) e temperatura da câmara fria. "
            "Verificar EPI e documentação do veículo."
        )

    if tipo == "Retorno":
        return (
            f"{indice}. 🏬 **Retorno ao {nome}:** "
            "Estacionar na baia de carga e dar baixa no sistema. "
            "Registrar quilometragem final e condição da carga."
        )

    # Entrega regular ou crítica
    eh_critico = destino.get("critico", False)
    alerta = "🚨 **[ALERTA DE PRIORIDADE CRÍTICA]** " if eh_critico else "📦 [ENTREGA REGULAR] "
    item = destino.get("item", "Não especificado")
    demanda = destino.get("demanda_kg", 0)

    protocolo = (
        "Despacho URGENTE. Entregar em mãos ao chefe de plantão com assinatura digital. "
        "Tempo máximo de espera: 5 minutos. Em caso de ausência, acionar supervisor imediatamente."
        if eh_critico
        else "Entrega padrão no almoxarifado hospitalar. Aguardar conferência e assinar recibo eletrônico."
    )

    condicao = (
        "⚠️ Manter refrigeração até a entrega. Não expor a temperaturas acima de 8°C."
        if eh_critico
        else "📋 Conferir integridade das embalagens antes da entrega."
    )

    return (
        f"{indice}. {alerta}**Parada em {nome}:**\n"
        f"   - **Insumo:** {item} ({demanda} kg)\n"
        f"   - **Protocolo:** {protocolo}\n"
        f"   - **Condição:** {condicao}"
    )


def construir_dados_veiculo(
    idx_veiculo: int,
    rota: List[int],
    pontos: Dict[int, dict],
    distancia_km: float,
) -> Dict[str, Any]:
    """
    Monta o dicionário de dados de um veículo a partir da rota otimizada pelo AG.
    """
    info = MOTORISTAS.get(idx_veiculo, {
        "nome": f"Motorista {idx_veiculo}",
        "veiculo_id": f"V-{100 + idx_veiculo}",
        "modelo": "Furgão",
        "placa": "ABC-1234",
    })
    carga_total = sum(pontos[p]["demanda"] for p in rota if p != 0)

    destinos = []
    for i, pid in enumerate(rota):
        if i == 0:
            destinos.append({"nome": pontos[pid]["nome"], "tipo": "Origem", "critico": False, "demanda_kg": 0})
        elif i == len(rota) - 1:
            destinos.append({"nome": pontos[pid]["nome"], "tipo": "Retorno", "critico": False, "demanda_kg": 0})
        else:
            destinos.append({
                "nome": pontos[pid]["nome"],
                "tipo": "Entrega",
                "critico": pontos[pid]["critico"],
                "demanda_kg": pontos[pid]["demanda"],
                "item": ITENS_ENTREGA.get(pid, "Suprimento Médico"),
            })

    return {
        "veiculo_id": info["veiculo_id"],
        "motorista": info["nome"],
        "modelo": info.get("modelo", "Furgão"),
        "placa": info.get("placa", "PAD-0000"),
        "distancia_total_km": round(distancia_km, 2),
        "carga_total_kg": round(carga_total, 1),
        "destinos": destinos,
    }


def gerar_manifesto_local(dados_veiculo: Dict[str, Any]) -> str:
    """
    Gera o manifesto de transporte médico usando formatação determinística local.
    """
    veiculo = dados_veiculo["veiculo_id"]
    motorista = dados_veiculo["motorista"]
    distancia = dados_veiculo["distancia_total_km"]
    carga = dados_veiculo["carga_total_kg"]
    ocupacao = (carga / CAPACIDADE_MAXIMA_KG) * 100

    status_carga = "⚠️ ATENÇÃO: Próximo do limite!" if ocupacao > 90 else "✅ Dentro dos limites"

    linhas = [
        "=" * 60,
        f"📋 MANIFESTO DE TRANSPORTE MÉDICO — VEÍCULO {veiculo}",
        "=" * 60,
        f"👤 Motorista Responsável : {motorista}",
        f"📍 Distância Prevista   : {distancia:.1f} km",
        f"⚖️  Carga Total          : {carga:.1f} kg / {CAPACIDADE_MAXIMA_KG:.0f} kg ({ocupacao:.0f}%) {status_carga}",
        "-" * 60,
        "🗺️  INSTRUÇÕES OPERACIONAIS PASSO A PASSO:\n",
    ]

    for i, destino in enumerate(dados_veiculo["destinos"], start=1):
        linhas.append(formatar_passo(i, destino, carga))
        linhas.append("")

    linhas += [
        "-" * 60,
        "⚕️  PROTOCOLOS DE SEGURANÇA:",
        "   • Em caso de acidente: ligar 192 (SAMU) e supervisor imediatamente",
        "   • Temperatura máxima câmara fria: 8°C (verificar a cada parada)",
        "   • Documentação obrigatória: CNH, CRLV, Guia de Remessa Hospitalar",
        "=" * 60,
    ]

    return "\n".join(linhas)


# ==============================================================================
# CONTROLE DE FLAGS E BRIEFING OPERACIONAL PARA MOTORISTAS
# ==============================================================================

@dataclass
class RegistroStatusBriefing:
    veiculo_id: str
    motorista: str
    status: str = "PENDENTE"    # "PENDENTE", "ENVIADO", "RE-ENVIADO"
    timestamp_envio: Optional[str] = None
    versao: int = 0
    caminho_arquivo: Optional[str] = None


class ControladorBriefings:
    """
    Controla o ciclo de vida dos briefings dos motoristas:
    - Rastreia se o briefing está PENDENTE, ENVIADO ou RE-ENVIADO
    - Formata o briefing operacional detalhado individual
    - Exporta arquivos txt dedicados por condutor
    - Permite reenvio/reimpressão a qualquer momento com atualização de flags
    """

    def __init__(self):
        self.registros: Dict[str, RegistroStatusBriefing] = {}
        self._inicializar_padrao()

    def _inicializar_padrao(self) -> None:
        for idx, dados in MOTORISTAS.items():
            vid = dados["veiculo_id"]
            self.registros[vid] = RegistroStatusBriefing(
                veiculo_id=vid,
                motorista=dados["nome"],
                status="PENDENTE",
                versao=0,
            )

    def atualizar_frota(self, rotas_detalhadas: List[Dict[str, Any]]) -> None:
        """Sincroniza o controlador com os veículos presentes nas rotas ativas."""
        for r in rotas_detalhadas:
            vid = r.get("veiculo_id") or f"V-{100 + r.get('veiculo', 1)}"
            mot = r.get("motorista", "Condutor")
            if vid not in self.registros:
                self.registros[vid] = RegistroStatusBriefing(
                    veiculo_id=vid,
                    motorista=mot,
                    status="PENDENTE",
                    versao=0,
                )

    def gerar_briefing_motorista(
        self,
        dados_v: Dict[str, Any],
        google_maps_url: str = "",
        status_info: Optional[RegistroStatusBriefing] = None,
    ) -> str:
        """Gera o documento de briefing operacional individual e estruturado."""
        vid = dados_v.get("veiculo_id", "V-101")
        mot = dados_v.get("motorista", "Motorista")
        modelo = dados_v.get("modelo", "Furgão")
        placa = dados_v.get("placa", "PAD-0000")
        dist = dados_v.get("distancia_total_km") or dados_v.get("distancia_km", 0.0)
        carga = dados_v.get("carga_total_kg") or dados_v.get("carga_kg", 0.0)
        ocup = (carga / CAPACIDADE_MAXIMA_KG) * 100
        url_maps = google_maps_url or dados_v.get("google_maps_url") or "https://maps.google.com"

        destinos = dados_v.get("destinos", [])
        paradas_entrega = [d for d in destinos if d.get("tipo") == "Entrega"]
        num_criticos = sum(1 for d in paradas_entrega if d.get("critico"))

        # Cabeçalho de Status
        if status_info and status_info.status == "ENVIADO":
            badge_status = f"📱 [ENVIADO AO MOTORISTA em {status_info.timestamp_envio} - Rev. {status_info.versao}]"
        elif status_info and status_info.status == "RE-ENVIADO":
            badge_status = f"🔄 [RE-ENVIADO AO MOTORISTA em {status_info.timestamp_envio} - Rev. {status_info.versao}]"
        else:
            badge_status = "⚪ [PENDENTE DE ENVIO / AGUARDANDO DESPACHO]"

        linhas = [
            "=" * 75,
            "📋 BRIEFING OPERACIONAL DE TRANSPORTE MÉDICO — HEALTHROUTE AI",
            "=" * 75,
            f"STATUS DO DESPACHO: {badge_status}",
            "-" * 75,
            "🚚 DADOS DO CONDUTOR E VEÍCULO:",
            f"   • Motorista Designado : {mot}",
            f"   • Veículo / Placa     : {vid} | {modelo} ({placa})",
            f"   • Carga Total         : {carga:.1f} kg / {CAPACIDADE_MAXIMA_KG:.0f} kg ({ocup:.0f}% ocupação)",
            f"   • Distância Prevista  : {dist:.1f} km (~{int(dist * 1.8)} min de percurso estimado)",
            f"   • Paradas Programadas : {len(paradas_entrega)} entregas ({num_criticos} com prioridade crítica)",
            "-" * 75,
            "🗺️ NAVEGAÇÃO GPS GOOGLE MAPS (Clique no link para iniciar no celular/painel):",
            f"   {url_maps}",
            "-" * 75,
            "📦 CONFERÊNCIA DE EMBARQUE & INSUMOS (Checklist antes da saída):",
        ]

        for idx, d in enumerate(paradas_entrega, start=1):
            crit = "🚨 URGENTE" if d.get("critico") else "🟢 Regular"
            item = d.get("item", "Suprimentos Médicos")
            kg = d.get("demanda_kg", 0)
            temp = "2°C a 8°C (Câmara Fria)" if d.get("critico") else "Ambiente (<25°C)"
            linhas.append(f"   [ ] {idx}. {item} ({kg:.1f} kg) → {d['nome']} | Temp: {temp} [{crit}]")

        linhas += [
            "-" * 75,
            "🧭 ITINERÁRIO PASSO A PASSO:",
        ]

        for i, dest in enumerate(destinos, start=1):
            linhas.append(formatar_passo(i, dest, carga))
            linhas.append("")

        linhas += [
            "-" * 75,
            "🛡️ PROCEDIMENTOS DE SEGURANÇA E EMERGÊNCIA:",
            "   1. Em caso de sinistro ou pane mecânica, ligue imediatamente para a",
            "      Central de Despacho Logístico: (27) 3636-8000 ou Canal VHF 4.",
            "   2. Emergência com vítimas ou socorro imediato: SAMU 192.",
            "   3. Monitore o termômetro do baú a cada parada (tolerância máx: 8°C).",
            "=" * 75,
        ]

        return "\n".join(linhas)

    def compartilhar_briefing(
        self,
        alvo: str,
        rotas_detalhadas: List[Dict[str, Any]],
    ) -> Tuple[str, str, bool]:
        """
        Imprime/compartilha o briefing do motorista selecionado e atualiza a flag de status.
        Entende nomes de motoristas, IDs de veículos e referências contextuais.
        """
        self.atualizar_frota(rotas_detalhadas)
        dados_v = self._localizar_veiculo(alvo, rotas_detalhadas)

        if not dados_v:
            motoristas_disponiveis = ", ".join(
                f"{r.get('identificador', r.get('motorista'))}" for r in rotas_detalhadas
            )
            return (
                "",
                f"⚠️ Não encontrei o condutor ou veículo '{alvo}'.\n"
                f"Motoristas disponíveis na escala: {motoristas_disponiveis}",
                False,
            )

        vid = dados_v.get("veiculo_id") or f"V-{100 + dados_v.get('veiculo', 1)}"
        mot = dados_v.get("motorista", "Motorista")
        dados_v["veiculo_id"] = vid
        dados_v["motorista"] = mot
        registro = self.registros.get(vid)
        if not registro:
            registro = RegistroStatusBriefing(veiculo_id=vid, motorista=mot)
            self.registros[vid] = registro

        agora_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        registro.timestamp_envio = agora_str
        registro.versao += 1

        if registro.versao == 1:
            registro.status = "ENVIADO"
            msg_flag = f"📱 **[ENVIADO / COMPARTILHADO]** às {agora_str} (Versão 1)"
        else:
            registro.status = "RE-ENVIADO"
            msg_flag = f"🔄 **[RE-ENVIADO / RE-IMPRESSO]** às {agora_str} (Revisão {registro.versao})"

        # Gera o arquivo individual em output/
        slug_mot = re.sub(r"\s+", "_", mot.lower())
        nome_arquivo = f"briefing_{vid}_{slug_mot}.txt"
        caminho_arq = os.path.join(OUTPUT_DIR, nome_arquivo)
        registro.caminho_arquivo = caminho_arq

        google_maps_url = dados_v.get("google_maps_url", "")
        texto_briefing = self.gerar_briefing_motorista(dados_v, google_maps_url, registro)

        with open(caminho_arq, "w", encoding="utf-8") as f:
            f.write(texto_briefing)

        self.salvar_status_json()

        confirmacao = (
            f"✅ **Briefing do condutor {mot} ({vid}) processado com sucesso!**\n"
            f"   • Flag de Rastreamento : {msg_flag}\n"
            f"   • Arquivo Exportado    : `{caminho_arq}`\n"
            f"   • Link Google Maps     : {dados_v.get('google_maps_url', 'Disponível no arquivo')}"
        )

        return texto_briefing, confirmacao, True

    def compartilhar_todos(self, rotas_detalhadas: List[Dict[str, Any]]) -> str:
        """Compartilha/imprime os briefings de todos os condutores da frota."""
        linhas = [
            "=======================================================================",
            "📢 DESPACHO GERAL — COMPARTILHANDO BRIEFINGS COM TODA A FROTA",
            "=======================================================================",
        ]
        for r in rotas_detalhadas:
            vid = r.get("veiculo_id", "")
            _, confirmacao, ok = self.compartilhar_briefing(vid, rotas_detalhadas)
            if ok:
                linhas.append(f"🚐 {r.get('identificador', vid)}:\n{confirmacao}\n")
        linhas.append(self.gerar_painel_status(rotas_detalhadas))
        return "\n".join(linhas)

    def gerar_painel_status(self, rotas_detalhadas: Optional[List[Dict[str, Any]]] = None) -> str:
        """Exibe o painel de status de envio dos briefings para todos os motoristas."""
        if rotas_detalhadas:
            self.atualizar_frota(rotas_detalhadas)

        linhas = [
            "=" * 75,
            "📋 PAINEL DE CONTROLE DE BRIEFINGS DOS MOTORISTAS — HEALTHROUTE AI",
            "=" * 75,
            f"{'Veículo':<8} | {'Motorista':<20} | {'Status de Envio':<22} | {'Último Despacho':<16} | {'Versão'}",
            "-" * 75,
        ]

        for vid, reg in self.registros.items():
            if reg.status == "ENVIADO":
                badge = "📱 ENVIADO"
            elif reg.status == "RE-ENVIADO":
                badge = "🔄 RE-ENVIADO"
            else:
                badge = "⚪ PENDENTE"

            hora = reg.timestamp_envio[11:19] if reg.timestamp_envio else "--"
            data = reg.timestamp_envio[:5] if reg.timestamp_envio else ""
            despacho_str = f"{data} {hora}".strip() or "--"
            versao_str = f"Rev. {reg.versao}" if reg.versao > 0 else "--"

            linhas.append(
                f"{vid:<8} | {reg.motorista[:20]:<20} | {badge:<22} | {despacho_str:<16} | {versao_str}"
            )

        linhas += [
            "=" * 75,
            "💡 Comandos rápidos:",
            "   • 'imprimir briefing <motorista>'     : Exibe e salva o briefing do condutor",
            "   • 'compartilhar briefing <motorista>' : Envia/compartilha e atualiza a flag",
            "   • Em linguagem natural: 'Imprima o briefing do motorista Carlos',",
            "     'Compartilhar rota com a motorista Ana', 'Reimprimir briefing do Roberto'",
        ]

        return "\n".join(linhas)

    def salvar_status_json(self) -> str:
        caminho = os.path.join(OUTPUT_DIR, "briefings_status.json")
        dados = {
            vid: {
                "veiculo_id": reg.veiculo_id,
                "motorista": reg.motorista,
                "status": reg.status,
                "timestamp_envio": reg.timestamp_envio,
                "versao": reg.versao,
                "caminho_arquivo": reg.caminho_arquivo,
            }
            for vid, reg in self.registros.items()
        }
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        return caminho

    def _localizar_veiculo(self, termo: str, rotas: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        t = termo.lower().strip()
        t_limpo = re.sub(
            r"\b(?:o|a|do|da|de|com|para|ao|motorista|condutor|condutora|ve[íi]culo|carro|van)\b",
            "",
            t,
        ).strip(" ?.!,")

        for r in rotas:
            vid = str(r.get("veiculo_id", "")).lower()
            mot = str(r.get("motorista", "")).lower()
            ident = str(r.get("identificador", "")).lower()
            v_num = str(r.get("veiculo", ""))

            if t in [vid, mot, ident, f"v{v_num}", v_num]:
                return r
            if t_limpo and (t_limpo in mot or t_limpo in vid or t_limpo in ident):
                return r
            # Checa primeiro ou último nome
            partes = mot.split()
            if any(p.lower() == t_limpo for p in partes):
                return r

        return None


# Instância global singleton do controlador de briefings
CONTROLADOR_BRIEFINGS = ControladorBriefings()

