"""
vrp/knowledge_base.py — Base de Conhecimento Clínico, Frota e Geolocalização Real.
Carrega catálogos de insumos, destinos reais, veículos e parâmetros da base operacional.
"""
from __future__ import annotations

import csv
import json
import math
import os
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def resolver_link_google_maps(url_ou_texto: str, timeout: int = 8) -> Optional[Dict[str, Any]]:
    """
    Resolve links do Google Maps (encurtados 'maps.app.goo.gl' ou completos 'google.com/maps/...').
    Extrai o nome do estabelecimento e as coordenadas geográficas reais (Latitude, Longitude).
    """
    m_url = re.search(r"(https?://[^\s\"'>]+)", url_ou_texto)
    if not m_url:
        return None
    url = m_url.group(1).rstrip(".,;)")

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (HealthRoute-AI)"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            url_final = resp.geturl()
    except Exception:
        url_final = url

    # 1. Extração do nome do local na URL
    nome = "Destino Google Maps"
    m_nome = re.search(r"/place/([^/@?]+)", url_final)
    if m_nome:
        nome_decodificado = urllib.parse.unquote_plus(m_nome.group(1)).replace("+", " ").strip()
        if nome_decodificado:
            nome = nome_decodificado

    # 2. Extração de Latitude e Longitude
    # Formato A: !3d(-20.xxxx)!4d(-40.yyyy)
    lat: Optional[float] = None
    lon: Optional[float] = None
    m_coords_data = re.search(r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", url_final)
    if m_coords_data:
        lat = float(m_coords_data.group(1))
        lon = float(m_coords_data.group(2))
    else:
        # Formato B: @(-20.xxxx),(-40.yyyy)
        m_coords_at = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", url_final)
        if m_coords_at:
            lat = float(m_coords_at.group(1))
            lon = float(m_coords_at.group(2))

    if lat is None or lon is None:
        return None

    return {
        "url_original": url,
        "url_final": url_final,
        "nome": nome,
        "latitude": round(lat, 6),
        "longitude": round(lon, 6),
    }


def calcular_distancia_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula a distância em quilômetros entre duas coordenadas (Latitude/Longitude)."""
    R = 6371.0  # Raio médio da Terra em km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)


@dataclass
class InsumoCatalogo:
    codigo: str
    nome: str
    categoria: str
    peso_unitario_kg: float
    temperatura_conservacao: str
    nivel_urgencia: str
    indicacao_clinica: str


@dataclass
class DestinoReal:
    id: int
    nome: str
    tipo: str
    municipio: str
    latitude: float
    longitude: float
    telefone: str
    horario: str


@dataclass
class VeiculoCadastro:
    id: int
    veiculo_id: str
    motorista: str
    modelo: str
    placa: str
    capacidade_kg: float
    autonomia_km: float
    consumo_kml: float
    hodometro_km: float


class BaseConhecimento:
    """Carrega dados reais de arquivos CSV/JSON e implementa regras clínicas de emergência."""

    def __init__(self):
        self.destinos_reais: List[DestinoReal] = []
        self.insumos_catalogo: Dict[str, InsumoCatalogo] = {}
        self.veiculos: List[VeiculoCadastro] = []
        self.base_operacional: Dict[str, Any] = {}
        self.carregar_tudo()

    def carregar_tudo(self) -> None:
        self._carregar_base_operacional()
        self._carregar_destinos_reais()
        self._carregar_catalogo_insumos()
        self._carregar_veiculos()

    def _carregar_base_operacional(self) -> None:
        caminho = os.path.join(DATA_DIR, "base_operacional.json")
        if os.path.exists(caminho):
            with open(caminho, "r", encoding="utf-8") as f:
                self.base_operacional = json.load(f)
        else:
            self.base_operacional = {
                "titulo": "Centro de Distribuição Médica Central",
                "endereco": "Vitória - ES",
                "latitude": -20.3167,
                "longitude": -40.3083,
                "responsavel": "Logística Médica",
            }

    def salvar_base_operacional(self, titulo: str, latitude: float, longitude: float, endereco: str = "") -> None:
        self.base_operacional["titulo"] = titulo
        self.base_operacional["latitude"] = float(latitude)
        self.base_operacional["longitude"] = float(longitude)
        if endereco:
            self.base_operacional["endereco"] = endereco
        caminho = os.path.join(DATA_DIR, "base_operacional.json")
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(self.base_operacional, f, ensure_ascii=False, indent=2)

    def _carregar_destinos_reais(self) -> None:
        caminho = os.path.join(DATA_DIR, "destinos_reais.csv")
        self.destinos_reais = []
        if os.path.exists(caminho):
            with open(caminho, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.destinos_reais.append(
                        DestinoReal(
                            id=int(row["id"]),
                            nome=row["nome"].strip(),
                            tipo=row.get("tipo", "Hospital").strip(),
                            municipio=row.get("municipio", "").strip(),
                            latitude=float(row["latitude"]),
                            longitude=float(row["longitude"]),
                            telefone=row.get("telefone", "").strip(),
                            horario=row.get("horario", "").strip(),
                        )
                    )

    def _carregar_catalogo_insumos(self) -> None:
        caminho = os.path.join(DATA_DIR, "catalogo_insumos.csv")
        self.insumos_catalogo = {}
        if os.path.exists(caminho):
            with open(caminho, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    codigo = row["codigo"].strip().upper()
                    self.insumos_catalogo[codigo] = InsumoCatalogo(
                        codigo=codigo,
                        nome=row["nome"].strip(),
                        categoria=row.get("categoria", "Medicamento").strip(),
                        peso_unitario_kg=float(row.get("peso_unitario_kg", 0.5)),
                        temperatura_conservacao=row.get("temperatura_conservacao", "Ambiente").strip(),
                        nivel_urgencia=row.get("nivel_urgencia", "REGULAR").strip(),
                        indicacao_clinica=row.get("indicacao_clinica", "").strip(),
                    )

    def _carregar_veiculos(self) -> None:
        caminho = os.path.join(DATA_DIR, "veiculos.csv")
        self.veiculos = []
        if os.path.exists(caminho):
            with open(caminho, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.veiculos.append(
                        VeiculoCadastro(
                            id=int(row["id"]),
                            veiculo_id=row["veiculo_id"].strip(),
                            motorista=row["motorista"].strip(),
                            modelo=row.get("modelo", "Furgão").strip(),
                            placa=row.get("placa", "").strip(),
                            capacidade_kg=float(row.get("capacidade_kg", 45.0)),
                            autonomia_km=float(row.get("autonomia_km", 35.0)),
                            consumo_kml=float(row.get("consumo_kml", 10.0)),
                            hodometro_km=float(row.get("hodometro_km", 0.0)),
                        )
                    )

    def salvar_veiculos(self) -> None:
        caminho = os.path.join(DATA_DIR, "veiculos.csv")
        with open(caminho, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "veiculo_id", "motorista", "modelo", "placa", "capacidade_kg", "autonomia_km", "consumo_kml", "hodometro_km"])
            for v in self.veiculos:
                writer.writerow([v.id, v.veiculo_id, v.motorista, v.modelo, v.placa, v.capacidade_kg, v.autonomia_km, v.consumo_kml, v.hodometro_km])

    def adicionar_ou_atualizar_veiculo(
        self,
        veiculo_id: str,
        motorista: str,
        modelo: str,
        placa: str,
        capacidade_kg: float,
        autonomia_km: float,
        consumo_kml: float,
        hodometro_km: float,
    ) -> VeiculoCadastro:
        for v in self.veiculos:
            if v.veiculo_id.lower() == veiculo_id.lower() or v.placa.lower() == placa.lower():
                v.motorista = motorista
                v.modelo = modelo
                v.placa = placa
                v.capacidade_kg = capacidade_kg
                v.autonomia_km = autonomia_km
                v.consumo_kml = consumo_kml
                v.hodometro_km = hodometro_km
                self.salvar_veiculos()
                return v

        novo_id = len(self.veiculos) + 1
        novo = VeiculoCadastro(
            id=novo_id,
            veiculo_id=veiculo_id.upper(),
            motorista=motorista,
            modelo=modelo,
            placa=placa.upper(),
            capacidade_kg=capacidade_kg,
            autonomia_km=autonomia_km,
            consumo_kml=consumo_kml,
            hodometro_km=hodometro_km,
        )
        self.veiculos.append(novo)
        self.salvar_veiculos()
        return novo

    def remover_veiculo(self, veiculo_id_ou_placa: str) -> bool:
        alvo = veiculo_id_ou_placa.lower().strip()
        inicial = len(self.veiculos)
        self.veiculos = [v for v in self.veiculos if v.veiculo_id.lower() != alvo and v.placa.lower() != alvo]
        if len(self.veiculos) < inicial:
            self.salvar_veiculos()
            return True
        return False

    def diagnosticar_emergencia_clinica(self, texto: str) -> Optional[Dict[str, Any]]:
        """
        Analisa o texto do usuário para identificar situações de emergência médica aguda:
        Ex: Picada de cobra cascavel, hemorragia grave, parada cardiorrespiratória.
        """
        t = texto.lower()

        # 1. Picada de Cascavel
        if any(w in t for w in ["cascavel", "cobra cascavel", "crotalus", "veneno de cascavel"]):
            destino = self._localizar_destino_no_texto(t, municipio_default="Santa Leopoldina")
            return {
                "tipo_emergencia": "ACIDENTE OFÍDICO — PICADA DE CASCAVEL",
                "insumo_sugerido": "Soro Anticrotálico (Cascavel)",
                "codigo_insumo": "SORO-CROT",
                "demanda_kg": 2.5,  # kit completo com ampolas + suporte
                "prioridade": "ULTRA_CRITICO",
                "protocolo": "Despacho Imediato! Tempo de ação crítico para evitar sequelas renais e neuroparalíticas.",
                "destino_sugerido": destino,
                "despacho_imediato_recomendado": True,
            }

        # 2. Picada de Jararaca
        if any(w in t for w in ["jararaca", "bothrops", "cobra jararaca"]):
            destino = self._localizar_destino_no_texto(t, municipio_default="Santa Leopoldina")
            return {
                "tipo_emergencia": "ACIDENTE OFÍDICO — PICADA DE JARARACA",
                "insumo_sugerido": "Soro Antibotrópico (Jararaca)",
                "codigo_insumo": "SORO-BOTR",
                "demanda_kg": 2.5,
                "prioridade": "ULTRA_CRITICO",
                "protocolo": "Despacho URGENTE para conter hemorragias teciduais e necrose.",
                "destino_sugerido": destino,
                "despacho_imediato_recomendado": True,
            }

        # 3. Picada de Escorpião
        if any(w in t for w in ["escorpião", "escorpiao", "picada de escorpião"]):
            destino = self._localizar_destino_no_texto(t, municipio_default="Vitória")
            return {
                "tipo_emergencia": "ACIDENTE ESCORPIÔNICO",
                "insumo_sugerido": "Soro Antiescorpiônico",
                "codigo_insumo": "SORO-ESCORP",
                "demanda_kg": 1.0,
                "prioridade": "ULTRA_CRITICO",
                "protocolo": "Risco de choque cardiogênico em crianças e idosos. Atendimento prioritário.",
                "destino_sugerido": destino,
                "despacho_imediato_recomendado": True,
            }

        # 4. Choque Hipovolêmico / Hemorragia
        if any(w in t for w in ["hemorragia", "transfusão urgente", "choque hipovolêmico", "sangue o-", "politrauma"]):
            destino = self._localizar_destino_no_texto(t, municipio_default="Vitória")
            return {
                "tipo_emergencia": "HEMORRAGIA AGUDA / CHOQUE",
                "insumo_sugerido": "Bolsas de Sangue O- Negativo (Universal)",
                "codigo_insumo": "SANG-ONEG",
                "demanda_kg": 4.5,  # ~10 bolsas
                "prioridade": "ULTRA_CRITICO",
                "protocolo": "Transfusão imediata para suporte de vida.",
                "destino_sugerido": destino,
                "despacho_imediato_recomendado": True,
            }

        return None

    def _localizar_destino_no_texto(self, texto: str, municipio_default: str = "Vitória") -> DestinoReal:
        """Tenta encontrar um destino existente no texto ou seleciona um relevante no município."""
        t = texto.lower()
        for d in self.destinos_reais:
            if d.nome.lower() in t or (d.municipio.lower() in t and d.tipo in ["Pronto Atendimento", "Posto de Saude", "Posto Rural"]):
                return d

        for d in self.destinos_reais:
            if d.municipio.lower() == municipio_default.lower():
                return d

        return self.destinos_reais[0] if self.destinos_reais else DestinoReal(
            id=99,
            nome=f"Posto de Atendimento Rural ({municipio_default})",
            tipo="Posto Rural",
            municipio=municipio_default,
            latitude=-20.1008,
            longitude=-40.5283,
            telefone="(27) 3255-0000",
            horario="24h Emergência",
        )
