"""
vrp/orders.py — Gerenciador de Pedidos, Lotes, Frota e Parâmetros em Linguagem Natural e CSV.
Permite catalogar demandas hospitalares, ajustar parâmetros da base, veículos e despachos expressos.
"""
from __future__ import annotations

import csv
import os
import random
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .data import (
    PONTOS,
    NUM_VEICULOS,
    CAPACIDADE_VEICULO,
    AUTONOMIA_VEICULO,
    MOTORISTAS,
    ITENS_ENTREGA,
    PESOS_PENALIDADE,
)
from .knowledge_base import (
    BaseConhecimento,
    DestinoReal,
    VeiculoCadastro,
    InsumoCatalogo,
    calcular_distancia_haversine,
    resolver_link_google_maps,
)


@dataclass
class PedidoEntrega:
    id: int
    hospital: str
    insumo: str
    demanda_kg: float
    critico: bool = False
    pos: Tuple[float, float] = (0.0, 0.0)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    ultra_critico: bool = False
    protocolo_emergencia: str = ""

    def to_ponto_dict(self) -> dict:
        return {
            "pos": self.pos,
            "demanda": self.demanda_kg,
            "critico": self.critico or self.ultra_critico,
            "nome": self.hospital,
            "insumo": self.insumo,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "ultra_critico": self.ultra_critico,
        }


class GerenciadorLotes:
    """Gerencia pedidos, base operacional, frota dinâmica e regras clínicas em linguagem natural."""

    def __init__(self):
        self.pedidos: List[PedidoEntrega] = []
        self.kb = BaseConhecimento()
        self.carregar_pedidos_iniciais()

    def carregar_pedidos_iniciais(self) -> None:
        """Carrega os pedidos padrão como lote inicial."""
        self.pedidos = []
        for pid in sorted(PONTOS.keys()):
            if pid == 0:
                continue
            dados = PONTOS[pid]
            insumo = ITENS_ENTREGA.get(pid, "Suprimentos Gerais")
            self.pedidos.append(
                PedidoEntrega(
                    id=pid,
                    hospital=dados["nome"],
                    insumo=insumo,
                    demanda_kg=float(dados["demanda"]),
                    critico=bool(dados["critico"]),
                    pos=tuple(dados["pos"]),
                )
            )

    def abrir_novo_lote(self) -> None:
        """Esvazia o lote atual para receber novos pedidos."""
        self.pedidos = []

    def adicionar_pedido(self, pedido: PedidoEntrega) -> None:
        pedido.id = len(self.pedidos) + 1
        self.pedidos.append(pedido)

    def remover_pedido(self, pedido_id: int) -> bool:
        tam_antes = len(self.pedidos)
        self.pedidos = [p for p in self.pedidos if p.id != pedido_id]
        # Re-indexa IDs
        for i, p in enumerate(self.pedidos, start=1):
            p.id = i
        return len(self.pedidos) < tam_antes

    def ajustar_volume_pedido(self, pedido_id: int, nova_demanda_kg: float) -> bool:
        for p in self.pedidos:
            if p.id == pedido_id:
                p.demanda_kg = round(float(nova_demanda_kg), 1)
                return True
        return False

    def ajustar_base_operacional(self, titulo: str, latitude: float, longitude: float, endereco: str = "") -> None:
        self.kb.salvar_base_operacional(titulo, latitude, longitude, endereco)

    def cadastrar_veiculo(
        self,
        veiculo_id: str,
        motorista: str,
        modelo: str,
        placa: str,
        capacidade_kg: float,
        autonomia_km: float,
        consumo_kml: float = 10.0,
        hodometro_km: float = 0.0,
    ) -> VeiculoCadastro:
        return self.kb.adicionar_ou_atualizar_veiculo(
            veiculo_id=veiculo_id,
            motorista=motorista,
            modelo=modelo,
            placa=placa,
            capacidade_kg=capacidade_kg,
            autonomia_km=autonomia_km,
            consumo_kml=consumo_kml,
            hodometro_km=hodometro_km,
        )

    def remover_veiculo(self, veiculo_id_ou_placa: str) -> bool:
        return self.kb.remover_veiculo(veiculo_id_ou_placa)

    def interpretar_pedido_texto(self, texto: str) -> Tuple[Optional[PedidoEntrega], Optional[Dict[str, Any]]]:
        """
        Interpreta pedidos em linguagem natural e detecta emergências médicas agudas.
        Retorna (pedido, info_emergencia).
        """
        t = texto.strip()
        t_lower = t.lower()

        # 1. Checa primeiro por Emergência Clínica Aguda (Ex: Picada de cascavel)
        info_emergencia = self.kb.diagnosticar_emergencia_clinica(t)
        if info_emergencia:
            dest_real: DestinoReal = info_emergencia["destino_sugerido"]
            # Converte lat/lon para coordenadas no grid relativo à base
            base_lat = self.kb.base_operacional.get("latitude", -20.3167)
            base_lon = self.kb.base_operacional.get("longitude", -40.3083)
            dist_km = calcular_distancia_haversine(base_lat, base_lon, dest_real.latitude, dest_real.longitude)

            # Posiciona no grid proporcional (1-9)
            gx = min(9.0, max(1.0, round(abs(dest_real.longitude - base_lon) * 20.0 + 3.0, 1)))
            gy = min(9.0, max(1.0, round(abs(dest_real.latitude - base_lat) * 25.0 + 3.0, 1)))

            pedido = PedidoEntrega(
                id=len(self.pedidos) + 1,
                hospital=f"{dest_real.nome} ({dest_real.municipio})",
                insumo=info_emergencia["insumo_sugerido"],
                demanda_kg=info_emergencia["demanda_kg"],
                critico=True,
                ultra_critico=True,
                pos=(gx, gy),
                latitude=dest_real.latitude,
                longitude=dest_real.longitude,
                protocolo_emergencia=info_emergencia["protocolo"],
            )
            return pedido, info_emergencia

        # 2. Detecção de Link do Google Maps (ex: maps.app.goo.gl ou google.com/maps)
        info_maps = resolver_link_google_maps(t)
        if info_maps:
            base_lat = self.kb.base_operacional.get("latitude", -20.3167)
            base_lon = self.kb.base_operacional.get("longitude", -40.3083)
            m_lat = info_maps["latitude"]
            m_lon = info_maps["longitude"]

            gx = min(9.0, max(1.0, round(abs(m_lon - base_lon) * 20.0 + 3.0, 1)))
            gy = min(9.0, max(1.0, round(abs(m_lat - base_lat) * 25.0 + 3.0, 1)))

            # Extração de peso se presente no texto ao redor do link
            match_peso = re.search(r"(\d+(?:[\.,]\d+)?)\s*(?:kg|quilos|kilos)", t_lower)
            demanda_kg = float(match_peso.group(1).replace(",", ".")) if match_peso else 20.0

            # Criticidade
            palavras_criticas = {"crítico", "critico", "urgente", "emergência", "emergencia", "uti", "sangue", "vacina"}
            eh_critico = any(palavra in t_lower for palavra in palavras_criticas)

            # Insumo extraído do texto complementar
            t_sem_url = re.sub(r"https?://[^\s]+", "", t).strip()
            insumo = "Suprimento Hospitalar"
            partes_prod = re.split(r"precisando de|precisa de|solicita|necessita de|insumo|produto", t_sem_url, flags=re.IGNORECASE)
            if len(partes_prod) > 1 and len(partes_prod[1].strip()) > 2:
                prod_limpo = re.sub(r"\b\d+(?:[\.,]\d+)?\s*(?:kg|quilos|kilos)?\b", "", partes_prod[1], flags=re.IGNORECASE).strip(" .;,")
                if len(prod_limpo) > 2:
                    insumo = prod_limpo.title()

            pedido = PedidoEntrega(
                id=len(self.pedidos) + 1,
                hospital=info_maps["nome"],
                insumo=insumo,
                demanda_kg=demanda_kg,
                critico=eh_critico,
                pos=(gx, gy),
                latitude=m_lat,
                longitude=m_lon,
            )
            return pedido, None

        # 2. Padrões regulares de solicitação
        padroes_intencao = [
            r"precisando de", r"precisa de", r"solicita", r"pedido de",
            r"necessita de", r"enviar para", r"entregar em", r"demanda de"
        ]
        if not any(re.search(padrao, t_lower) for padrao in padroes_intencao):
            return None, None

        # Criticidade
        palavras_criticas = {"crítico", "critico", "urgente", "emergência", "emergencia", "uti", "sangue", "vacina"}
        eh_critico = any(palavra in t_lower for palavra in palavras_criticas)

        # Demanda em kg
        match_peso = re.search(r"(\d+(?:[\.,]\d+)?)\s*(?:kg|quilos|kilos)", t_lower)
        if match_peso:
            demanda_kg = float(match_peso.group(1).replace(",", "."))
        else:
            match_num = re.search(r"\b(\d+)\b", t)
            demanda_kg = float(match_num.group(1)) if match_num else 15.0

        # Hospital / Destino
        nome_hospital = "Destino Médico"
        match_hosp = re.search(
            r"(?:o|a)?\s*(hospital\s+[^,]+?|posto\s+[^,]+?|cl[íi]nica\s+[^,]+?|upa\s+[^,]+?|centro\s+[^,]+?|farm[áa]cia\s+[^,]+?)\s+(?:est[áa]\s+)?(?:precisando|precisa|solicita|necessita)",
            t, re.IGNORECASE
        )
        if match_hosp:
            nome_hospital = match_hosp.group(1).strip().title()
        else:
            partes = re.split(r"precisando de|precisa de|solicita|necessita de", t, flags=re.IGNORECASE)
            if len(partes) > 1 and len(partes[0].strip()) > 3:
                nome_candidato = re.sub(r"^(?:o|a|para|ao)\s+", "", partes[0].strip(), flags=re.IGNORECASE)
                nome_hospital = nome_candidato.title()

        # Insumo
        insumo = "Suprimento Médico"
        partes_produto = re.split(r"precisando de|precisa de|solicita|necessita de", t, flags=re.IGNORECASE)
        if len(partes_produto) > 1:
            prod_texto = partes_produto[1].strip()
            prod_limpo = re.sub(r"\b\d+(?:[\.,]\d+)?\s*(?:kg|quilos|kilos)?\b", "", prod_texto, flags=re.IGNORECASE)
            prod_limpo = re.sub(r"\b(?:cr[íi]tico|urgente|emerg[êe]ncia|uti)\b", "", prod_limpo, flags=re.IGNORECASE)
            prod_limpo = re.sub(r"[()\[\]]", "", prod_limpo).strip(" .;,")
            if len(prod_limpo) > 2:
                insumo = prod_limpo.title()

        # Coordenadas
        match_coords = re.search(r"(?:coordenadas?|pos|posi[çc][aã]o)\s*[:=]?\s*\(?(\d+(?:\.\d+)?)\s*[,;\s]\s*(\d+(?:\.\d+)?)\)?", t_lower)
        if match_coords:
            pos = (float(match_coords.group(1)), float(match_coords.group(2)))
        else:
            seed_val = sum(ord(c) for c in nome_hospital)
            rng = random.Random(seed_val)
            pos = (round(rng.uniform(1.0, 9.0), 1), round(rng.uniform(1.0, 9.0), 1))

        pedido = PedidoEntrega(
            id=len(self.pedidos) + 1,
            hospital=nome_hospital,
            insumo=insumo,
            demanda_kg=round(demanda_kg, 1),
            critico=eh_critico,
            pos=pos,
        )
        return pedido, None

    def importar_csv(self, caminho_csv: str) -> int:
        if not os.path.exists(caminho_csv):
            raise FileNotFoundError(f"Arquivo CSV não encontrado: {caminho_csv}")

        novos_pedidos = []
        with open(caminho_csv, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                nome = row.get("hospital") or row.get("nome", "Hospital")
                insumo = row.get("insumo") or row.get("produto", "Medicamentos")
                demanda = float(row.get("demanda_kg") or row.get("demanda", 15))
                critico_str = str(row.get("critico", "false")).strip().lower()
                critico = critico_str in {"true", "1", "sim", "s", "critico", "crítico"}
                pos_x = float(row.get("pos_x", random.uniform(1, 9)))
                pos_y = float(row.get("pos_y", random.uniform(1, 9)))

                novos_pedidos.append(
                    PedidoEntrega(
                        id=len(self.pedidos) + len(novos_pedidos) + 1,
                        hospital=nome.strip(),
                        insumo=insumo.strip(),
                        demanda_kg=demanda,
                        critico=critico,
                        pos=(round(pos_x, 1), round(pos_y, 1)),
                    )
                )

        self.pedidos.extend(novos_pedidos)
        return len(novos_pedidos)

    def carregar_cenario_robusto(self) -> int:
        """
        Carrega um cenário expandido e realista com 16 destinos hospitalares da Grande Vitória
        e Região Serrana com insumos médicos especializados, prioridades clínicas e posições reais.
        """
        self.abrir_novo_lote()
        self.kb.carregar_tudo()

        base_lat = self.kb.base_operacional.get("latitude", -20.3167)
        base_lon = self.kb.base_operacional.get("longitude", -40.3083)

        cenario = [
            ("Hospital Estadual Dr. Jayme Santos Neves", "Bolsas de Sangue O- Negativo", 14.0, True),
            ("Hospital Infantil Nossa Senhora da Gloria", "Vacinas Termossensíveis Pediátricas", 12.0, True),
            ("Unidade Mista de Saude Santa Leopoldina", "Soro Anticrotálico (Cascavel)", 8.0, True),
            ("Posto de Saude Rural Barra de Mangarai", "Soro Antibotrópico (Jararaca)", 6.0, True),
            ("Farmacia Popular Centro de Vitoria", "Medicamentos Gerais e Anti-hipertensivos", 22.0, False),
            ("UPA 24h Carapina", "Kits de Sutura e Curativo Estéril", 18.0, False),
            ("Hospital Estadual de Urgencia e Emergencia (HEUE)", "Anestésicos Injetáveis Críticos", 15.0, True),
            ("Posto de Saude Rural Holanda", "Soro Antiescorpiônico e Curativos", 5.0, True),
            ("Farmacia Cidada Estadual", "Insulina NPH e Hormônios Térmicos", 20.0, False),
            ("Hospital Evangélico de Vila Velha", "Antibióticos Injetáveis Hospitalares", 16.0, False),
            ("Hospital Estadual Antonio Bezerra de Faria", "Bolsas de Sangue O+ e Plasma", 14.0, True),
            ("Hospital Santa Rita de Cassia", "Fármacos Oncológicos Sensíveis", 10.0, True),
            ("Pronto Atendimento de Campo Grande", "Soro Fisiológico 0.9%", 25.0, False),
            ("Hospital Estadual de Atencao Clinica (HEAC)", "Psicotrópicos e Sedativos", 12.0, False),
            ("UPA 24h Serra Sede", "Material Cirúrgico de Emergência", 16.0, False),
            ("Hospital e Maternidade Dr. Arthur Gerhardt", "Kits Obstétricos e Vacinas", 10.0, True),
        ]

        # Mapeia destinos existentes por nome
        dest_map = {d.nome.lower(): d for d in self.kb.destinos_reais}

        for idx, (hosp, insumo, demanda, critico) in enumerate(cenario, start=1):
            d_real = dest_map.get(hosp.lower())
            if d_real:
                lat, lon = d_real.latitude, d_real.longitude
            else:
                lat, lon = base_lat, base_lon

            gx = min(9.0, max(1.0, round(abs(lon - base_lon) * 20.0 + 3.0, 1)))
            gy = min(9.0, max(1.0, round(abs(lat - base_lat) * 25.0 + 3.0, 1)))

            self.pedidos.append(
                PedidoEntrega(
                    id=idx,
                    hospital=hosp,
                    insumo=insumo,
                    demanda_kg=demanda,
                    critico=critico,
                    pos=(gx, gy),
                    latitude=lat,
                    longitude=lon,
                )
            )

        return len(self.pedidos)

    def converter_para_pontos_vrp(self) -> Tuple[Dict[int, dict], Dict[int, str]]:
        pontos_vrp: Dict[int, dict] = {
            0: {
                "pos": (0.0, 0.0),
                "demanda": 0.0,
                "critico": False,
                "nome": self.kb.base_operacional.get("titulo", "Depósito Central"),
            }
        }
        itens_vrp: Dict[int, str] = {}

        for i, pedido in enumerate(self.pedidos, start=1):
            pontos_vrp[i] = {
                "pos": pedido.pos,
                "demanda": pedido.demanda_kg,
                "critico": pedido.critico,
                "nome": pedido.hospital,
            }
            itens_vrp[i] = pedido.insumo

        return pontos_vrp, itens_vrp

    def gerar_tabela_dados_input(self) -> str:
        base = self.kb.base_operacional
        veiculos = self.kb.veiculos

        linhas = [
            "=" * 75,
            "📋 DADOS DE INPUT E PARÂMETROS OPERACIONAIS — HEALTHROUTE AI",
            "=" * 75,
            f"📍 Base Operacional : {base.get('titulo', 'Depósito Central')}",
            f"   Coordenadas      : Lat {base.get('latitude', -20.3167)} | Long {base.get('longitude', -40.3083)}",
            f"   Endereço         : {base.get('endereco', 'Centro Logístico')}",
            "-" * 75,
            "🚐 FROTA DE VEÍCULOS CADASTRADOS:",
            f"{'ID':<6} | {'Modelo':<26} | {'Placa':<9} | {'Capac.':<7} | {'Autonomia':<9} | {'Consumo':<8} | {'Motorista'}",
            "-" * 75,
        ]

        for v in veiculos:
            linhas.append(
                f"{v.veiculo_id:<6} | {v.modelo[:26]:<26} | {v.placa:<9} | {v.capacidade_kg:4.0f} kg | {v.autonomia_km:4.0f} km | {v.consumo_kml:4.1f} km/l | {v.motorista}"
            )

        linhas += [
            "-" * 75,
            "📦 DESTINOS E DEMANDAS DO LOTE ATUAL:",
            f"{'ID':<4} | {'Destino':<26} | {'Demanda':<8} | {'Prioridade':<12} | {'Posição':<10} | {'Insumo Médico'}",
            "-" * 75,
        ]

        linhas.append(f"{'0':<4} | {base.get('titulo', 'Depósito Central')[:26]:<26} | {'0 kg':<8} | {'Base':<12} | {'(0.0, 0.0)':<10} | Base da Frota")

        total_carga = sum(p.demanda_kg for p in self.pedidos)
        criticos_count = sum(1 for p in self.pedidos if p.critico)

        for p in self.pedidos:
            prioridade = "🚨 ULTRA-CRÍT" if p.ultra_critico else ("🚨 CRÍTICO" if p.critico else "🟢 Regular")
            pos_str = f"({p.pos[0]:.1f}, {p.pos[1]:.1f})"
            linhas.append(
                f"{p.id:<4} | {p.hospital[:26]:<26} | {p.demanda_kg:4.1f} kg | {prioridade:<12} | {pos_str:<10} | {p.insumo}"
            )

        linhas += [
            "-" * 75,
            f"📊 TOTAL DO LOTE: {len(self.pedidos)} paradas | {total_carga:.1f} kg | {criticos_count} críticas/emergências",
            "=" * 75,
        ]
        return "\n".join(linhas)

    def gerar_tabela_catalogo_insumos(self) -> str:
        linhas = [
            "=" * 75,
            "💊 CATÁLOGO OFICIAL DE INSUMOS E ANTIOFÍDICOS",
            "=" * 75,
            f"{'Código':<12} | {'Insumo Médico':<32} | {'Peso':<6} | {'Temp.':<10} | {'Urgência'}",
            "-" * 75,
        ]
        for codigo, ins in self.kb.insumos_catalogo.items():
            urg = "🚨 ULTRA" if ins.nivel_urgencia == "ULTRA_CRITICO" else ("⚠️ ALTO" if ins.nivel_urgencia == "ALTO" else "🟢 REGULAR")
            linhas.append(
                f"{codigo:<12} | {ins.nome[:32]:<32} | {ins.peso_unitario_kg:4.2f}kg | {ins.temperatura_conservacao:<10} | {urg}"
            )
        linhas.append("=" * 75)
        return "\n".join(linhas)

    def gerar_tabela_destinos_reais(self) -> str:
        linhas = [
            "=" * 75,
            "🏥 DESTINOS HOSPITALARES E POSTOS REAIS CADASTRADOS",
            "=" * 75,
            f"{'ID':<3} | {'Nome':<36} | {'Município':<16} | {'Tipo':<14}",
            "-" * 75,
        ]
        for d in self.kb.destinos_reais:
            linhas.append(f"{d.id:<3} | {d.nome[:36]:<36} | {d.municipio:<16} | {d.tipo:<14}")
        linhas.append("=" * 75)
        return "\n".join(linhas)

    def gerar_resumo_lote(self) -> str:
        if not self.pedidos:
            return "📦 O lote atual está vazio. Lance pedidos em linguagem natural ou importe um CSV!"

        linhas = [
            f"📦 LOTE ATUAL DE ENTREGAS ({len(self.pedidos)} pedidos catalogados):"
        ]
        for p in self.pedidos:
            crit = "🚨 [ULTRA-CRÍTICO]" if p.ultra_critico else ("🚨 [CRÍTICO]" if p.critico else "📦")
            linhas.append(f"  {p.id}. {crit} {p.hospital}: {p.insumo} ({p.demanda_kg} kg) - Pos {p.pos}")
        linhas.append("\n💡 Digite 'otimizar' ou 'fechar lote' para calcular as rotas deste lote!")
        return "\n".join(linhas)
