"""
vrp/visualization.py — Visualização matplotlib das rotas e exportação de resultados.
"""
import json
import os
from datetime import datetime
from typing import Any, Dict, List

import matplotlib
matplotlib.use("Agg")  # backend headless para salvar sem abrir janela
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from .data import PONTOS, NUM_VEICULOS, CAPACIDADE_VEICULO, AUTONOMIA_VEICULO, MATRIZ_DISTANCIAS

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

CORES_VEICULOS = ["#2196F3", "#FF9800", "#4CAF50"]   # Azul, Laranja, Verde
NOMES_VEICULOS = ["V-101 (Carlos Silva)", "V-102 (Ana Souza)", "V-103 (Roberto Lima)"]

# Coordenadas geográficas reais (Latitude, Longitude) na Grande Vitória e Região Serrana - ES
COORDENADAS_PADRAO: Dict[int, tuple] = {
    0: (-20.3167, -40.3083),  # Depósito Central (Bento Ferreira, Vitória)
    1: (-20.3201, -40.3375),  # Hospital A (UTI) - Hospital Infantil / Vitória
    2: (-20.2889, -40.2981),  # Posto B - Goiabeiras / Vitória
    3: (-20.1936, -40.2458),  # Hospital C (Emergência) - Hospital Jayme Santos Neves / Serra
    4: (-20.3478, -40.2950),  # Posto D - Farmácia Cidadã / Vila Velha
    5: (-20.3350, -40.3950),  # Hospital E - Hospital Evangélico / Vila Velha
    6: (-20.1008, -40.5283),  # Clínica F - Unidade Mista / Santa Leopoldina
}


def obter_coordenadas_ponto(pid: int, pontos_ref: Dict[int, dict] = None) -> tuple:
    """Retorna as coordenadas (latitude, longitude) para o ponto especificado."""
    pts = pontos_ref or PONTOS
    if pid in pts:
        p_dados = pts[pid]
        lat = p_dados.get("latitude")
        lon = p_dados.get("longitude")
        if lat is not None and lon is not None:
            return (float(lat), float(lon))

    if pid in COORDENADAS_PADRAO:
        return COORDENADAS_PADRAO[pid]

    # Interpolação suave a partir da posição relativa ao grid 10x10
    base_lat, base_lon = COORDENADAS_PADRAO[0]
    if pid in pts and "pos" in pts[pid]:
        px, py = pts[pid]["pos"]
        return (round(base_lat + (py - 5.0) * 0.035, 4), round(base_lon + (px - 5.0) * 0.035, 4))

    return COORDENADAS_PADRAO[0]


def gerar_link_google_maps(caminho: List[int], pontos_ref: Dict[int, dict] = None) -> str:
    """
    Gera link direto de navegação do Google Maps (turn-by-turn) para uma rota.
    Exemplo:
    https://www.google.com/maps/dir/?api=1&origin=-20.3167,-40.3083&destination=-20.3167,-40.3083&waypoints=-20.1936,-40.2458|-20.2889,-40.2981&travelmode=driving
    """
    if not caminho:
        return "https://maps.google.com"

    coords = [obter_coordenadas_ponto(p, pontos_ref) for p in caminho]
    origem = f"{coords[0][0]:.4f},{coords[0][1]:.4f}"
    destino = f"{coords[-1][0]:.4f},{coords[-1][1]:.4f}"

    if len(coords) > 2:
        intermediarios = [f"{c[0]:.4f},{c[1]:.4f}" for c in coords[1:-1]]
        waypoints = "|".join(intermediarios)
        return (
            f"https://www.google.com/maps/dir/?api=1&origin={origem}"
            f"&destination={destino}&waypoints={waypoints}&travelmode=driving"
        )
    elif len(coords) == 2:
        return f"https://www.google.com/maps/dir/?api=1&origin={origem}&destination={destino}&travelmode=driving"
    return f"https://www.google.com/maps/search/?api=1&query={origem}"


def _construir_rotas(melhor_rota: List[int]) -> List[List[int]]:
    """Divide a sequência de entregas entre os NUM_VEICULOS veículos."""
    entregas = [p for p in melhor_rota if p != 0]
    partes = np.array_split(entregas, NUM_VEICULOS)
    rotas = []
    for parte in partes:
        caminho = [0] + list(parte) + [0]
        rotas.append(caminho)
    return rotas


def plotar_rotas(melhor_rota: List[int], salvar: bool = True) -> str:
    """
    Gera o mapa 2D das rotas por veículo e salva em output/rotas.png.

    Retorna o caminho completo do arquivo salvo.
    """
    rotas = _construir_rotas(melhor_rota)
    fig, ax = plt.subplots(figsize=(10, 9))
    ax.set_facecolor("#F5F5F5")
    ax.set_title("HealthRoute AI — Mapa de Rotas Médicas Otimizadas", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Coordenada X (km)")
    ax.set_ylabel("Coordenada Y (km)")
    ax.set_xlim(-0.5, 10)
    ax.set_ylim(-0.5, 10.5)
    ax.grid(True, alpha=0.3, linestyle="--")

    # Desenha as rotas
    for idx, (rota, cor, nome) in enumerate(zip(rotas, CORES_VEICULOS, NOMES_VEICULOS)):
        xs = [PONTOS[p]["pos"][0] for p in rota]
        ys = [PONTOS[p]["pos"][1] for p in rota]
        ax.plot(xs, ys, color=cor, linewidth=2.0, alpha=0.8, marker="o",
                markersize=5, zorder=2, label=nome)
        # Setas de direção
        for i in range(len(xs) - 1):
            ax.annotate("", xy=(xs[i + 1], ys[i + 1]), xytext=(xs[i], ys[i]),
                        arrowprops=dict(arrowstyle="->", color=cor, lw=1.5),
                        zorder=3)

    # Desenha os nós
    for pid, dados in PONTOS.items():
        x, y = dados["pos"]
        if pid == 0:
            ax.scatter(x, y, s=250, color="#FFC107", edgecolors="black", zorder=5, marker="*")
            ax.annotate(f"  {dados['nome']}", (x, y), fontsize=8, fontweight="bold", va="bottom")
        elif dados["critico"]:
            ax.scatter(x, y, s=120, color="#F44336", edgecolors="darkred", zorder=5)
            ax.annotate(f"  {dados['nome']}\n  [{dados['demanda']}kg] ⚠", (x, y),
                        fontsize=7.5, color="#B71C1C", va="bottom")
        else:
            ax.scatter(x, y, s=80, color="#1565C0", edgecolors="navy", zorder=5)
            ax.annotate(f"  {dados['nome']}\n  [{dados['demanda']}kg]", (x, y),
                        fontsize=7.5, color="#0D47A1", va="bottom")

    ax.legend(loc="upper left", fontsize=8.5, framealpha=0.9)

    # Legenda de tipos de ponto
    handles_extra = [
        mpatches.Patch(color="#FFC107", label="Depósito"),
        mpatches.Patch(color="#F44336", label="Crítico ⚠"),
        mpatches.Patch(color="#1565C0", label="Regular"),
    ]
    leg2 = ax.legend(handles=handles_extra, loc="lower right", fontsize=8, title="Tipo de Ponto")
    ax.add_artist(leg2)
    ax.legend(loc="upper left", fontsize=8.5, framealpha=0.9)

    plt.tight_layout()
    caminho = os.path.join(OUTPUT_DIR, "rotas.png")
    if salvar:
        fig.savefig(caminho, dpi=150, bbox_inches="tight")
        print(f"[visualization] Mapa salvo em: {caminho}")
    plt.close(fig)
    return caminho


def exportar_json(melhor_rota: List[int], custo: float, rotas_detalhadas: List[Dict[str, Any]]) -> str:
    """
    Exporta os resultados completos do AG em formato JSON estruturado,
    incluindo URLs de navegação direta do Google Maps.

    Retorna o caminho do arquivo salvo.
    """
    rotas = _construir_rotas(melhor_rota)
    payload = {
        "timestamp": datetime.now().isoformat(),
        "algoritmo": "GA_VRP_OX1_Swap",
        "sequencia_otimizada": [int(p) for p in melhor_rota],
        "custo_fitness": round(float(custo), 4),
        "rotas_veiculos": [],
    }
    for i, (rota, nome_v) in enumerate(zip(rotas, NOMES_VEICULOS), start=1):
        distancia = sum(MATRIZ_DISTANCIAS[rota[j]][rota[j + 1]] for j in range(len(rota) - 1))
        carga = sum(PONTOS[p]["demanda"] for p in rota if p != 0)
        maps_url = gerar_link_google_maps(rota)
        payload["rotas_veiculos"].append({
            "veiculo": i,
            "identificador": nome_v,
            "caminho": [int(p) for p in rota],
            "pontos_nomes": [PONTOS[p]["nome"] for p in rota],
            "distancia_km": round(float(distancia), 2),
            "carga_kg": round(float(carga), 1),
            "ocupacao_pct": round(float(carga) / CAPACIDADE_VEICULO * 100, 1),
            "google_maps_url": maps_url,
        })

    caminho = os.path.join(OUTPUT_DIR, "rotas.json")
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"[visualization] JSON salvo em: {caminho}")
    return caminho


def gerar_mapa_html(
    rotas_detalhadas: List[Dict[str, Any]],
    pontos_ref: Dict[int, dict] = None,
    caminho_saida: str = None,
) -> str:
    """
    Gera um mapa interativo geográfico completo (HTML com Leaflet e OpenStreetMap),
    com marcadores reais, traçados por veículo e botões com links diretos para o Google Maps.
    """
    pts = pontos_ref or PONTOS
    caminho_final = caminho_saida or os.path.join(OUTPUT_DIR, "rotas_google_maps.html")

    # Coleta de coordenadas centrais
    todas_coords = [obter_coordenadas_ponto(p, pts) for p in pts.keys()]
    lat_centro = sum(c[0] for c in todas_coords) / max(len(todas_coords), 1)
    lon_centro = sum(c[1] for c in todas_coords) / max(len(todas_coords), 1)

    # Construção de marcadores JavaScript
    marcadores_js = []
    for pid, dados in pts.items():
        lat, lon = obter_coordenadas_ponto(pid, pts)
        nome = dados.get("nome", f"Ponto {pid}").replace("'", "\\'")
        demanda = dados.get("demanda", 0)
        eh_critico = dados.get("critico", False)
        eh_base = (pid == 0)

        if eh_base:
            cor_icone = "#FFC107"
            titulo_popup = f"🏬 <b>{nome}</b><br>Base Central de Abastecimento e Frota"
        elif eh_critico:
            cor_icone = "#F44336"
            titulo_popup = f"🚨 <b>{nome}</b><br><b>Prioridade:</b> CRÍTICA (UTI/Emergência)<br><b>Demanda:</b> {demanda:.1f} kg"
        else:
            cor_icone = "#2196F3"
            titulo_popup = f"🏥 <b>{nome}</b><br><b>Prioridade:</b> Regular<br><b>Demanda:</b> {demanda:.1f} kg"

        marcadores_js.append(
            f"""
        L.circleMarker([{lat}, {lon}], {{
            radius: {12 if eh_base else (10 if eh_critico else 8)},
            fillColor: '{cor_icone}',
            color: '#000',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.85
        }}).addTo(map).bindPopup('{titulo_popup}');
        """
        )

    # Construção de linhas de rota e cartões HTML
    linhas_rotas_js = []
    cards_html = []
    for r in rotas_detalhadas:
        cor = r.get("cor", CORES_VEICULOS[(r["veiculo"] - 1) % len(CORES_VEICULOS)])
        ident = r.get("identificador", f"Veículo {r['veiculo']}")
        caminho_pids = r.get("caminho", [])
        coords_rota = [list(obter_coordenadas_ponto(p, pts)) for p in caminho_pids]
        coords_json = json.dumps(coords_rota)
        maps_url = r.get("google_maps_url") or gerar_link_google_maps(caminho_pids, pts)

        linhas_rotas_js.append(
            f"""
        L.polyline({coords_json}, {{
            color: '{cor}',
            weight: 4,
            opacity: 0.85,
            dashArray: '2, 6'
        }}).addTo(map).bindPopup('<b>{ident}</b><br>Distância: {r.get("distancia_km", 0):.1f} km<br>Carga: {r.get("carga_kg", 0):.1f} kg');
        """
        )

        nomes_passos = " → ".join(r.get("pontos_nomes", []))
        cards_html.append(
            f"""
        <div style="background: white; border-radius: 8px; padding: 14px; margin-bottom: 12px; border-left: 6px solid {cor}; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <h4 style="margin: 0 0 6px 0; color: #1e293b;">{ident}</h4>
            <p style="margin: 2px 0; font-size: 13px; color: #475569;"><b>📏 Distância:</b> {r.get("distancia_km", 0):.1f} km &nbsp;|&nbsp; <b>⚖️ Carga:</b> {r.get("carga_kg", 0):.1f} kg ({r.get("ocupacao_pct", 0):.0f}%)</p>
            <p style="margin: 4px 0 10px 0; font-size: 12px; color: #64748b; line-height: 1.4;"><b>Itinerário:</b> {nomes_passos}</p>
            <a href="{maps_url}" target="_blank" style="display: inline-block; background: #2563eb; color: white; text-decoration: none; padding: 7px 14px; border-radius: 6px; font-size: 13px; font-weight: bold; transition: background 0.2s;">
                🗺️ Abrir Rota no Google Maps
            </a>
        </div>
        """
        )

    cards_str = "\n".join(cards_html)
    marcadores_str = "\n".join(marcadores_js)
    linhas_str = "\n".join(linhas_rotas_js)

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HealthRoute AI — Rotas Médicas no Google Maps</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; display: flex; height: 100vh; background: #f8fafc; }}
        #sidebar {{ width: 420px; height: 100vh; overflow-y: auto; padding: 20px; box-sizing: border-box; background: #f1f5f9; border-right: 1px solid #cbd5e1; }}
        #map {{ flex: 1; height: 100vh; }}
        .header {{ margin-bottom: 20px; }}
        .header h2 {{ margin: 0 0 5px 0; color: #0f172a; font-size: 20px; }}
        .header p {{ margin: 0; color: #64748b; font-size: 13px; }}
        .legend {{ background: white; border-radius: 8px; padding: 12px; margin-bottom: 15px; font-size: 12px; border: 1px solid #e2e8f0; }}
        .legend-item {{ display: flex; align-items: center; margin-bottom: 5px; }}
        .legend-circle {{ width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }}
    </style>
</head>
<body>
    <div id="sidebar">
        <div class="header">
            <h2>🚑 HealthRoute AI</h2>
            <p>Navegação Geográfica & Rotas Otimizadas VRP</p>
        </div>
        <div class="legend">
            <div class="legend-item"><span class="legend-circle" style="background: #FFC107;"></span> <b>Depósito / Base Central</b></div>
            <div class="legend-item"><span class="legend-circle" style="background: #F44336;"></span> <b>Ponto Crítico (UTI / Emergência)</b></div>
            <div class="legend-item"><span class="legend-circle" style="background: #2196F3;"></span> <b>Ponto Regular de Saúde</b></div>
        </div>
        <h3 style="font-size: 15px; color: #334155; margin-bottom: 12px;">🚐 Rotas por Veículo & Navegação:</h3>
        {cards_str}
    </div>
    <div id="map"></div>

    <script>
        var map = L.map('map').setView([{lat_centro}, {lon_centro}], 11);
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '&copy; OpenStreetMap contributors | HealthRoute AI'
        }}).addTo(map);

        {marcadores_str}
        {linhas_str}
    </script>
</body>
</html>
"""
    with open(caminho_final, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[visualization] Mapa HTML interativo salvo em: {caminho_final}")
    return caminho_final


def gerar_relatorio_executivo(rotas_detalhadas: List[Dict[str, Any]], custo: float) -> str:
    """
    Gera o Relatório Executivo (Artefato 1 do PDF) em texto estruturado.
    """
    linhas = [
        "=" * 65,
        "  HEALTHROUTE AI — RELATÓRIO EXECUTIVO DE OTIMIZAÇÃO",
        "=" * 65,
        f"  Data/Hora   : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        f"  Algoritmo   : Algoritmo Genético VRP (OX1 + Swap Mutation)",
        f"  Frota       : {NUM_VEICULOS} veículos | Cap. máx.: {CAPACIDADE_VEICULO} kg | Autonomia: {AUTONOMIA_VEICULO} km",
        "-" * 65,
        "  RESULTADOS POR VEÍCULO",
        "-" * 65,
    ]
    dist_total = 0.0
    carga_total = 0.0
    for r in rotas_detalhadas:
        dist_total += r["distancia_km"]
        carga_total += r["carga_kg"]
        ocup = r["ocupacao_pct"]
        linhas.append(
            f"  {r['identificador']:<35} | {r['distancia_km']:5.1f} km | {r['carga_kg']:4.1f} kg ({ocup:.0f}%)"
        )
    linhas += [
        "-" * 65,
        f"  TOTAIS: Distância = {dist_total:.1f} km | Carga = {carga_total:.1f} kg | Fitness = {custo:.2f}",
        "=" * 65,
    ]
    return "\n".join(linhas)
