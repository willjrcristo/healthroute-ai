"""
llm/qa_interface.py — Interface de Perguntas, Gestão de Lotes, Parâmetros e Emergências Clínicas.
"""
from __future__ import annotations

import os
import re
from typing import Any, Callable, Dict, List, Optional

from vrp.orders import GerenciadorLotes, PedidoEntrega

CAPACIDADE_VEICULO = 45.0


def _contexto_para_texto(contexto: Dict[str, Any]) -> str:
    """Serializa o contexto de rotas para texto para uso em prompt de LLM."""
    linhas = []
    for r in contexto.get("rotas", []):
        linhas.append(
            f"Veículo {r['veiculo']} ({r['identificador']}): "
            f"{r['distancia_km']:.1f}km, {r['carga_kg']:.1f}kg ({r['ocupacao_pct']:.0f}%), "
            f"rota: {' -> '.join(r['pontos_nomes'])}"
        )
    return "\n".join(linhas)


def responder_pergunta(
    pergunta: str,
    contexto: Dict[str, Any],
    gerenciador_lotes: Optional[GerenciadorLotes] = None,
) -> str:
    """
    Responde a perguntas analíticas, processa comandos de configuração e emergências clínicas.
    """
    p = pergunta.lower().strip()
    rotas = contexto.get("rotas", [])
    gl = gerenciador_lotes or contexto.get("gerenciador_lotes")

    # ─── 1. Exibição de Dados de Input e Catálogos ────────────────────── #
    if re.search(r"^(?:dados|inputs?|ver dados|ver inputs?|tabela de dados)$", p):
        if gl:
            return gl.gerar_tabela_dados_input()
        return "📋 Dados de input não disponíveis no contexto."

    if re.search(r"^(?:catalogo insumos|insumos|ver insumos|antiofidicos)$", p):
        if gl:
            return gl.gerar_tabela_catalogo_insumos()
        return "💊 Catálogo de insumos não disponível."

    if re.search(r"^(?:destinos reais|hospitais reais|ver destinos)$", p):
        if gl:
            return gl.gerar_tabela_destinos_reais()
        return "🏥 Destinos reais não disponíveis."

    # ─── 2. Ajustes de Parâmetros Operacionais ────────────────────────── #
    # Ajuste da Base Operacional: Ex: "ajustar base Centro Logistico ES lat -20.31 long -40.30"
    match_base = re.search(r"(?:ajustar|configurar)\s+base\s+(.+?)\s+lat\s*[:=]?\s*(-?\d+(?:\.\d+)?)\s+long\s*[:=]?\s*(-?\d+(?:\.\d+)?)", p)
    if match_base and gl:
        titulo = match_base.group(1).strip().title()
        lat = float(match_base.group(2))
        lon = float(match_base.group(3))
        gl.ajustar_base_operacional(titulo, lat, lon)
        return (
            f"✅ **BASE OPERACIONAL ATUALIZADA COM SUCESSO!**\n"
            f"   • Título   : {titulo}\n"
            f"   • Latitude : {lat}\n"
            f"   • Longitude: {lon}\n"
            "Os próximos cálculos de rota partirão desta nova base."
        )

    # Cadastrar Veículo Completo: Ex: "cadastrar veiculo V-104 motorista Marcos modelo Van Fiorino placa ABC-1234 capacidade 50 autonomia 40"
    match_veic = re.search(r"cadastrar\s+ve[íi]culo\s+(\w+-\d+|\w+)\s+motorista\s+(.+?)\s+modelo\s+(.+?)\s+placa\s+(\w+-\w+|\w+)\s+capacidade\s+(\d+(?:\.\d+)?)\s+autonomia\s+(\d+(?:\.\d+)?)", p)
    if match_veic and gl:
        v_id = match_veic.group(1).strip().upper()
        mot = match_veic.group(2).strip().title()
        mod = match_veic.group(3).strip().title()
        plc = match_veic.group(4).strip().upper()
        cap = float(match_veic.group(5))
        aut = float(match_veic.group(6))
        novo_v = gl.cadastrar_veiculo(v_id, mot, mod, plc, cap, aut)
        return (
            f"✅ **VEÍCULO CADASTRADO/ATUALIZADO NA FROTA!**\n"
            f"   • ID / Placa: {novo_v.veiculo_id} ({novo_v.placa})\n"
            f"   • Modelo    : {novo_v.modelo}\n"
            f"   • Motorista : {novo_v.motorista}\n"
            f"   • Capacidade: {novo_v.capacidade_kg} kg | Autonomia: {novo_v.autonomia_km} km"
        )

    # Adicionar Veículo Simplificado / Linguagem Natural: Ex: "adicione mais um veiculo", "adicionar veiculo", "novo veiculo"
    if re.search(r"^(?:adicione|adicionar|incluir|novo|cadastrar)\s+(?:mais\s+um\s+|um\s+|novo\s+)?ve[íi]culo(?:\s+(\w+-\d+|\w+))?", p) and gl:
        m_id = re.search(r"ve[íi]culo\s+(\w+-\d+|\w+)", p)
        v_id_sugerido = m_id.group(1).upper() if m_id else f"V-{100 + len(gl.kb.veiculos) + 1}"

        nomes_disponiveis = [
            "Marcos Oliveira", "Juliana Mendes", "Fernando Dias", "Renata Azevedo",
            "Lucas Guimarães", "Patricia Rocha", "Bruno Castro", "Camila Barreto"
        ]
        mot_sugerido = nomes_disponiveis[(len(gl.kb.veiculos) - 3) % len(nomes_disponiveis)]
        mod_sugerido = "Renault Master Furgão Térmico [USB-SAMU]" if len(gl.kb.veiculos) % 2 == 0 else "Mercedes-Benz Sprinter UTI Móvel [USA-SAMU]"
        plc_sugerida = f"SAM-{1900 + len(gl.kb.veiculos):04d}"

        novo_v = gl.cadastrar_veiculo(
            veiculo_id=v_id_sugerido,
            motorista=mot_sugerido,
            modelo=mod_sugerido,
            placa=plc_sugerida,
            capacidade_kg=50.0,
            autonomia_km=40.0,
        )
        return (
            f"✅ **NOVO VEÍCULO ADICIONADO À FROTA DO SAMU!**\n"
            f"=================================================================\n"
            f"🚐 **Identificador** : {novo_v.veiculo_id} ({novo_v.placa})\n"
            f"👤 **Condutor**      : {novo_v.motorista}\n"
            f"🚑 **Modelo/Tipo**   : {novo_v.modelo}\n"
            f"⚖️  **Capacidade**   : {novo_v.capacidade_kg:.0f} kg\n"
            f"📍 **Autonomia**    : {novo_v.autonomia_km:.0f} km\n"
            f"-----------------------------------------------------------------\n"
            f"A frota agora conta com **{len(gl.kb.veiculos)} veículos ativos** para os próximos cálculos de rota!"
        )

    # Remover Veículo: Ex: "remover veiculo V-103"
    match_rem_v = re.search(r"remover\s+ve[íi]culo\s+(\w+-\d+|\w+)", p)
    if match_rem_v and gl:
        alvo = match_rem_v.group(1).strip()
        removido = gl.remover_veiculo(alvo)
        if removido:
            return f"🗑️ Veículo **{alvo.upper()}** removido da frota com sucesso!"
        return f"⚠️ Veículo {alvo} não encontrado na frota."

    # Ajustar Volume de Pedido Existente: Ex: "ajustar pedido 2 para 35 kg"
    match_aj_ped = re.search(r"ajustar\s+pedido\s+(\d+)\s+para\s+(\d+(?:\.\d+)?)\s*(?:kg)?", p)
    if match_aj_ped and gl:
        ped_id = int(match_aj_ped.group(1))
        novo_vol = float(match_aj_ped.group(2))
        ok = gl.ajustar_volume_pedido(ped_id, novo_vol)
        if ok:
            return f"⚖️ **Volume do Pedido #{ped_id} ajustado para {novo_vol:.1f} kg com sucesso!**"
        return f"⚠️ Pedido #{ped_id} não encontrado no lote atual."

    # Remover Pedido: Ex: "remover pedido 3"
    match_rem_ped = re.search(r"remover\s+pedido\s+(\d+)", p)
    if match_rem_ped and gl:
        ped_id = int(match_rem_ped.group(1))
        ok = gl.remover_pedido(ped_id)
        if ok:
            return f"🗑️ **Pedido #{ped_id} removido do lote atual!**"
        return f"⚠️ Pedido #{ped_id} não encontrado no lote."

    # ─── 3. Ajuda / Comandos ─────────────────────────────────────────── #
    if re.search(r"^(?:ajuda|help|comandos?|\?)$", p):
        tabela_input = gl.gerar_tabela_dados_input() if gl else ""
        return (
            f"{tabela_input}\n\n"
            "💡 GUIA DE COMANDOS E RECURSOS:\n\n"
            "  🚨 [EMERGÊNCIAS CLÍNICAS E ANTIOFÍDICOS]:\n"
            "  • 'Uma criança foi picada por uma cascavel em Santa Leopoldina, precisa de antiofídico'\n"
            "  • 'Acidente com jararaca precisa de soro urgente'\n"
            "  • 'catalogo insumos'      : Lista todos os soros antiofídicos e remédios catalogados\n"
            "  • 'destinos reais'        : Lista os hospitais, UPAs e postos reais com Lat/Long\n\n"
            "  🎮 [MAPAS E VISUALIZAÇÃO INTERATIVA]:\n"
            "  • 'abrir mapa' ou 'pygame'                : Reabre a janela gráfica animada do Pygame\n"
            "  • 'google maps' ou 'mapa real'            : Exibe links de GPS turn-by-turn no Google Maps\n"
            "  • 'abrir mapa real'                       : Abre o mapa interativo geográfico (Leaflet) no navegador\n\n"
            "  🚗 [BRIEFINGS E CONTROLE DE MOTORISTAS]:\n"
            "  • 'status briefings' ou 'painel motoristas' : Tabela com flags de status de cada condutor\n"
            "  • 'imprimir briefing <motorista>'           : Exibe, imprime e gera arquivo do briefing\n"
            "  • 'compartilhar briefing <motorista>'        : Compartilha e atualiza a flag de envio\n"
            "  • Em linguagem natural: 'Imprima o briefing do motorista Carlos',\n"
            "    'Compartilhar o brief com a Ana', 'Pode reimprimir o briefing do Roberto?'\n\n"
            "  ⚙️ [AJUSTE DE PARÂMETROS OPERACIONAIS]:\n"
            "  • 'ajustar base <Nome> lat <x> long <y>' : Altera o Depósito/Base Central\n"
            "  • 'cadastrar veiculo V-104 motorista Marcos modelo Van placa ABC-1234 capacidade 50 autonomia 40'\n"
            "  • 'adicione mais um veiculo' ou 'novo veiculo' : Cadastra automaticamente novo veículo do SAMU\n"
            "  • 'remover veiculo <ID>'                  : Remove veículo da frota\n"
            "  • 'ajustar pedido <ID> para <X> kg'       : Altera o volume de um insumo já pedido\n"
            "  • 'remover pedido <ID>'                   : Exclui um pedido do lote\n\n"
            "  📦 [GESTÃO DE LOTES E CENÁRIOS]:\n"
            "  • Cole links do Google Maps: ex: 'https://maps.app.goo.gl/... precisa de 15kg'\n"
            "  • 'cenario real' ou 'carga robusta'       : Carrega 16 hospitais reais do ES e demandas complexas\n"
            "  • 'ver lote'              : Exibe os pedidos catalogados no lote atual\n"
            "  • 'novo lote'             : Abre um novo lote limpo para receber pedidos\n"
            "  • 'importar <arquivo.csv>': Importa lista de pedidos de arquivo CSV\n"
            "  • 'otimizar' ou 'fechar lote' : Calcula rotas VRP e gera manifestos e relatórios\n\n"
            "  📊 [PERGUNTAS ANALÍTICAS]:\n"
            "  • 'Qual a distância total?' | 'Qual veículo tem carga máxima?' | 'Liste as rotas'\n"
            "  • 'dados' : Exibe novamente a tabela de input acima | 'sair' : Encerra"
        )

    # ─── 4. Visualização PyGame e Mapas ───────────────────────────────── #
    if re.search(r"^(?:abrir mapa|ver mapa|mapa|pygame|abrir pygame|reabrir mapa)$", p):
        callback_pygame = contexto.get("callback_pygame")
        if callback_pygame:
            try:
                callback_pygame()
                return "🎮 **Janela do PyGame encerrada.** Retornando à interface de comando."
            except Exception as e:
                return f"⚠️ Erro ao abrir janela PyGame: {e}. O mapa estático continua disponível em `output/rotas.png`."
        return "🎮 O visualizador Pygame pode ser aberto pelo comando 'python main.py' ou veja o mapa em 'output/rotas.png'."

    # ─── 5. Integração Google Maps e Mapa Geográfico ───────────────────── #
    if re.search(r"^(?:google maps|mapa real|links maps|rotas maps|abrir google maps|ver no maps|maps)$", p):
        linhas = [
            "=" * 70,
            "🗺️  HEALTHROUTE AI — INTEGRAÇÃO COM GOOGLE MAPS",
            "=" * 70,
            "Rotas de navegação GPS passo a passo para cada condutor:",
            "-" * 70,
        ]
        for r in rotas:
            url = r.get("google_maps_url")
            if not url:
                from vrp.visualization import gerar_link_google_maps
                url = gerar_link_google_maps(r.get("caminho", []))
            ident = r.get("identificador") or f"Veículo {r.get('veiculo')}"
            caminho_str = " → ".join(r.get("pontos_nomes", []))
            linhas.append(f"🚐 **{ident}**:")
            linhas.append(f"   📍 Itinerário: {caminho_str}")
            linhas.append(f"   🔗 Navegação GPS: {url}\n")

        caminho_html = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "rotas_google_maps.html")
        if os.path.exists(caminho_html):
            linhas.append("🌐 **Mapa Interativo Geográfico salvo:**")
            linhas.append(f"   `{caminho_html}`")
            linhas.append("💡 Digite **'abrir mapa real'** para visualizá-lo diretamente no navegador.")
        linhas.append("=" * 70)
        return "\n".join(linhas)

    if re.search(r"^(?:abrir mapa real|abrir mapa no navegador|abrir html)$", p):
        caminho_html = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "rotas_google_maps.html")
        if os.path.exists(caminho_html):
            import webbrowser
            webbrowser.open(f"file:///{os.path.abspath(caminho_html)}")
            return f"🌐 **Mapa interativo aberto no seu navegador!**\nArquivo: `{caminho_html}`"
        return "⚠️ Arquivo de mapa interativo ainda não gerado."

    # ─── 6. Painel de Controle de Briefings e Flags ────────────────────── #
    if re.search(r"^(?:status briefings?|status motoristas?|painel motoristas?|briefings?)$", p):
        from llm.manifesto import CONTROLADOR_BRIEFINGS
        return CONTROLADOR_BRIEFINGS.gerar_painel_status(rotas)

    # ─── 7. Impressão e Compartilhamento de Briefings ──────────────────── #
    if re.search(r"(?:imprimir|imprima|compartilhar|compartilhe|enviar|envie)\s+(?:todos\s+os\s+briefings|o\s+briefing\s+de\s+todos|todos)", p):
        from llm.manifesto import CONTROLADOR_BRIEFINGS
        return CONTROLADOR_BRIEFINGS.compartilhar_todos(rotas)

    match_briefing = re.search(
        r"(?:imprimir|imprima|reimprimir|reimprima|compartilhar|compartilhe|enviar|envie|ver|mostrar|gerar)\s+(?:o\s+)?(?:briefing|brief)\s+(?:do\s+motorista\s+|da\s+motorista\s+|do\s+condutor\s+|da\s+condutora\s+|do\s+ve[íi]culo\s+|com\s+(?:o\s+)?(?:motorista\s+)?|para\s+(?:o\s+)?(?:motorista\s+)?|de\s+|do\s+|da\s+)?(.+)",
        p
    )
    if not match_briefing:
        match_briefing = re.search(r"^briefing\s+(?:do\s+motorista\s+|do\s+ve[íi]culo\s+|do\s+|da\s+|de\s+)?(.+)", p)

    if match_briefing:
        alvo = match_briefing.group(1).strip().rstrip("?.! ")
        from llm.manifesto import CONTROLADOR_BRIEFINGS
        texto, msg, ok = CONTROLADOR_BRIEFINGS.compartilhar_briefing(alvo, rotas)
        if ok:
            return f"{texto}\n\n{msg}"
        return msg

    # ─── 4. Comandos de Lote ─────────────────────────────────────────── #
    if re.search(r"^(?:ver lote|lote|pedidos|ver pedidos)$", p):
        if gl:
            return gl.gerar_resumo_lote()
        return "📦 Gerenciador de lotes não inicializado."

    if re.search(r"^(?:novo lote|abrir lote|limpar lote)$", p):
        if gl:
            gl.abrir_novo_lote()
            return "🆕 **Novo lote de entregas aberto com sucesso!**\nAgora você pode informar pedidos como: 'O Hospital X está precisando de Y kg de insumo Z'."
        return "📦 Gerenciador de lotes não inicializado."

    match_imp = re.search(r"^importar\s+([\w\-\.\/\\\:]+\.csv)", p)
    if match_imp:
        if gl:
            caminho = match_imp.group(1).strip()
            try:
                qtd = gl.importar_csv(caminho)
                return f"✅ **{qtd} pedidos importados com sucesso** do arquivo `{caminho}`!\n\n{gl.gerar_resumo_lote()}"
            except Exception as e:
                return f"⚠️ Erro ao importar CSV: {e}"
        return "📦 Gerenciador de lotes não inicializado."

    # Comando de Carga de Cenário Robusto / Real Metropolitano
    if re.search(r"^(?:carregar\s+cen[áa]rio\s+real|cen[áa]rio\s+real|carga\s+robusta|gerar\s+carga\s+robusta|cen[áa]rio\s+robusto|cenario\s+expandido)$", p):
        if gl:
            qtd = gl.carregar_cenario_robusto()
            total_kg = sum(p.demanda_kg for p in gl.pedidos)
            criticos = sum(1 for p in gl.pedidos if p.critico)
            return (
                f"🏥 **CENÁRIO ROBUSTO METROPOLITANO CARREGADO COM SUCESSO!**\n"
                f"=================================================================\n"
                f"📍 **Total de Destinos Reais** : {qtd} hospitais e unidades de saúde\n"
                f"⚖️  **Carga Médica Total**     : {total_kg:.1f} kg\n"
                f"🚨 **Demandas Críticas / UTI** : {criticos} pontos prioritários\n"
                f"🚐 **Frota Disponível**        : {len(gl.kb.veiculos)} veículos ativos do SAMU\n"
                f"-----------------------------------------------------------------\n"
                f"Cidades cobertas: Vitória, Vila Velha, Serra, Cariacica, Domingos Martins e Santa Leopoldina.\n\n"
                f"💡 Digite **'otimizar'** para calcular as rotas otimizadas multi-veiculares agora!"
            )
        return "📦 Gerenciador de lotes não inicializado."

    # ─── 5. Lançamento de Pedidos e Emergências Clínicas ──────────────── #
    if gl:
        pedido_extraido, info_emergencia = gl.interpretar_pedido_texto(pergunta)
        if pedido_extraido:
            gl.adicionar_pedido(pedido_extraido)

            # Caso de Emergência Clínica Aguda (Ex: Picada de cobra / antiofídico)
            if info_emergencia:
                return (
                    f"🚨 **ALERTA DE EMERGÊNCIA MÉDICA AGUDA — CÓDIGO VERMELHO** 🚨\n"
                    f"=================================================================\n"
                    f"🏥 **Diagnóstico** : {info_emergencia['tipo_emergencia']}\n"
                    f"💊 **Insumo Vital** : {info_emergencia['insumo_sugerido']} (Cód: {info_emergencia['codigo_insumo']})\n"
                    f"📍 **Destino**      : {pedido_extraido.hospital}\n"
                    f"⚖️  **Carga**        : {pedido_extraido.demanda_kg:.1f} kg\n"
                    f"⚕️  **Protocolo**    : {info_emergencia['protocolo']}\n"
                    f"-----------------------------------------------------------------\n"
                    f"⚡ **RECOMENDAÇÃO OPERACIONAL:**\n"
                    f"Trata-se de uma entrega com risco iminente de vida. O pedido foi catalogado\n"
                    f"com **Prioridade 0 (Ultra-Crítico)**.\n\n"
                    f"👉 **Recomendamos fechar o lote imediatamente para despacho expresso!**\n"
                    f"Digite **'otimizar'** ou **'sim'** para calcular a rota prioritária agora!"
                )

            crit_badge = "🚨 CRÍTICO (Prioridade Nível 1)" if pedido_extraido.critico else "🟢 Regular"
            coords_msg = ""
            if pedido_extraido.latitude and pedido_extraido.longitude:
                coords_msg = f"   • **GPS Real**  : Lat {pedido_extraido.latitude:.4f}, Lon {pedido_extraido.longitude:.4f}\n"

            return (
                f"✅ **PEDIDO CATALOGADO NO LOTE!**\n"
                f"   • **Destino**   : {pedido_extraido.hospital}\n"
                f"   • **Insumo**    : {pedido_extraido.insumo}\n"
                f"   • **Quantidade**: {pedido_extraido.demanda_kg:.1f} kg\n"
                f"   • **Prioridade**: {crit_badge}\n"
                f"{coords_msg}"
                f"   • **Posição Grid**: {pedido_extraido.pos}\n\n"
                f"📦 O lote atual possui **{len(gl.pedidos)} pedidos** cadastrados.\n"
                "💡 Digite **'otimizar'** para fechar o lote e calcular as rotas!"
            )

    if not rotas:
        return "⚠️ Nenhuma rota disponível no contexto atual."

    # ─── 6. Perguntas Analíticas de Rota ───
    if re.search(r"dist[âa]ncia total|km total|quilometr", p):
        total = sum(r["distancia_km"] for r in rotas)
        return f"📏 A distância total percorrida pela frota é de **{total:.1f} km**."

    if re.search(r"mais carga|maior carga|mais pesado|mais carregado|carga m[áa]xima|capacidade m[áa]xima|limite de carga", p):
        r = max(rotas, key=lambda x: x["carga_kg"])
        return (
            f"⚖️ O veículo com maior carga é **{r['identificador']}** "
            f"com **{r['carga_kg']:.1f} kg** ({r['ocupacao_pct']:.0f}% da capacidade)."
        )

    if re.search(r"menos carga|menor carga|menos carregado|carga m[íi]nima", p):
        r = min(rotas, key=lambda x: x["carga_kg"])
        return (
            f"⚖️ O veículo com menor carga é **{r['identificador']}** "
            f"com **{r['carga_kg']:.1f} kg** ({r['ocupacao_pct']:.0f}% da capacidade)."
        )

    if re.search(r"ocupa[çc][aã]o|capacidade", p):
        linhas = [f"📊 Ocupação por veículo:"]
        for r in rotas:
            status = "🔴" if r["ocupacao_pct"] > 90 else "🟢"
            linhas.append(f"  {status} {r['identificador']}: {r['ocupacao_pct']:.0f}%")
        return "\n".join(linhas)

    if re.search(r"rota mais longa|maior dist[âa]ncia", p):
        r = max(rotas, key=lambda x: x["distancia_km"])
        return f"📍 A rota mais longa é do **{r['identificador']}** com **{r['distancia_km']:.1f} km**."

    if re.search(r"rota mais curta|menor dist[âa]ncia", p):
        r = min(rotas, key=lambda x: x["distancia_km"])
        return f"📍 A rota mais curta é do **{r['identificador']}** com **{r['distancia_km']:.1f} km**."

    if re.search(r"cr[íi]tico|prioridade|uti|emerg[êe]ncia", p):
        linhas = ["🚨 Pontos críticos e seus veículos:"]
        for r in rotas:
            nomes = r.get("pontos_nomes", [])
            for nome in nomes:
                if any(k in nome.lower() for k in ["uti", "emergência", "emergencia", "clínica f", "clinica f", "crítico", "critico"]):
                    linhas.append(f"  • {nome} → {r['identificador']}")
        return "\n".join(linhas) if len(linhas) > 1 else "Nenhum ponto crítico detectado nos nomes das rotas."

    if re.search(r"list[ae]|listar|mostrar|quais s[aã]o as rotas|ver rotas|todas as rotas", p):
        linhas = ["🗺️ Rotas otimizadas:"]
        for r in rotas:
            caminho = " → ".join(r.get("pontos_nomes", [str(pt) for pt in r.get("caminho", [])]))
            linhas.append(f"  {r['identificador']}: {caminho}")
        return "\n".join(linhas)

    for r in rotas:
        v_id = r["identificador"].lower()
        if v_id in p or f"veículo {r['veiculo']}" in p or f"veiculo {r['veiculo']}" in p:
            nomes = " → ".join(r.get("pontos_nomes", []))
            return (
                f"🚐 **{r['identificador']}**:\n"
                f"  Rota: {nomes}\n"
                f"  Distância: {r['distancia_km']:.1f} km\n"
                f"  Carga: {r['carga_kg']:.1f} kg ({r['ocupacao_pct']:.0f}%)"
            )

    if re.search(r"fitness|algoritmo|gera[çc][aã]o|convergiu", p):
        fitness_final = contexto.get("fitness_final", None)
        total_ger = contexto.get("total_geracoes", None)
        if fitness_final is not None:
            return (
                f"🧬 O Algoritmo Genético executou **{total_ger} gerações** "
                f"e atingiu fitness final de **{fitness_final:.2f}**."
            )
        return "🧬 Dados do algoritmo não disponíveis no contexto atual."

    provider = os.getenv("LLM_PROVIDER", "local").lower()
    if provider != "local":
        return _chamar_llm_externo(pergunta, contexto, provider)

    return (
        "🤔 Não entendi completamente sua pergunta.\n"
        "Digite 'ajuda' para visualizar os dados de input e comandos disponíveis,\n"
        "ou lance um pedido como: 'O Hospital X precisa de 20kg de soro'."
    )


def _chamar_llm_externo(pergunta: str, contexto: Dict[str, Any], provider: str) -> str:
    contexto_texto = _contexto_para_texto(contexto)
    try:
        if provider == "groq":
            from groq import Groq
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            resp = client.chat.completions.create(
                model="deepseek-r1-distill-llama-70b",
                messages=[
                    {"role": "system", "content": "Você é um assistente de logística médica. Responda em português de forma concisa."},
                    {"role": "user", "content": f"Contexto das rotas:\n{contexto_texto}\n\nPergunta: {pergunta}"},
                ],
                max_tokens=300,
            )
            return resp.choices[0].message.content
        elif provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel("gemini-1.5-flash")
            resp = model.generate_content(
                f"Contexto das rotas médicas:\n{contexto_texto}\n\nPergunta: {pergunta}"
            )
            return resp.text
    except Exception as e:
        return f"⚠️ Erro ao chamar LLM ({provider}): {e}. Tente reformular a pergunta."
    return "⚠️ Provedor LLM não configurado corretamente."


def iniciar_qa_interativo(
    contexto: Dict[str, Any],
    gerenciador_lotes: Optional[GerenciadorLotes] = None,
    callback_reotimizar: Optional[Callable[[Dict[int, dict], Dict[int, str]], Dict[str, Any]]] = None,
    callback_pygame: Optional[Callable[[], None]] = None,
) -> None:
    gl = gerenciador_lotes or GerenciadorLotes()
    contexto["gerenciador_lotes"] = gl
    if callback_pygame:
        contexto["callback_pygame"] = callback_pygame

    print("\n" + "=" * 65)
    print("  HEALTHROUTE AI — INTERFACE DE PEDIDOS, PARÂMETROS E Q&A")
    print("=" * 65)
    print("  • Faça perguntas ou lance emergências médicas em linguagem natural")
    print("    Ex: 'Criança picada por cascavel em Santa Leopoldina precisa de antiofídico'")
    print("  • 'abrir mapa' (Pygame) | 'google maps' | 'status briefings' | 'ajuda' | 'sair'")
    print("  • 'imprimir briefing <motorista>' | 'compartilhar briefing <motorista>'")
    print("=" * 65 + "\n")

    while True:
        try:
            pergunta = input("🔍 Sua pergunta ou comando: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[Q&A] Encerrado pelo usuário.")
            break

        if not pergunta:
            continue

        if pergunta.lower() in {"sair", "exit", "q", "quit", "fechar"}:
            print("✅ Interface encerrada.")
            break

        # Comando de re-otimização do lote ou confirmação de despacho expresso
        if re.search(r"^(?:otimizar|fechar lote|calcular rotas|rodar rotas|sim|despachar|despachar agora)$", pergunta.lower()):
            if not gl.pedidos:
                print("\n⚠️ O lote atual está vazio! Adicione pedidos antes de otimizar.\n")
                continue

            if callback_reotimizar:
                print("\n🔄 Re-otimizando rotas da frota com o Algoritmo Genético...")
                novos_pontos, novos_itens = gl.converter_para_pontos_vrp()
                novo_contexto = callback_reotimizar(novos_pontos, novos_itens)
                contexto.update(novo_contexto)
                print("✅ Lote otimizado com sucesso! Novos manifestos e rotas gerados.\n")
            else:
                print("✅ Lote fechado. Otimização solicitada.")
            continue

        resposta = responder_pergunta(pergunta, contexto, gl)
        print(f"\n{resposta}\n")
