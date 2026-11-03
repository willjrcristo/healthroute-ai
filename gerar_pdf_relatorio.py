"""
Script oficial de geração do Relatório Técnico Completo e Atualizado em PDF.
Tech Challenge Fase 2 | FIAP | HealthRoute AI
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)

PDF_PATH = "Relatório Técnico Atualizado - Otimização de Rotas Médicas (Tech Challenge Fase 2).pdf"

def gerar_pdf():
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    
    # Estilos customizados
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=17,
        leading=21,
        textColor=colors.HexColor('#0D47A1'),
        fontName='Helvetica-Bold',
        spaceAfter=4,
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=12.5,
        textColor=colors.HexColor('#444444'),
        spaceAfter=8,
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading2'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#0D47A1'),
        fontName='Helvetica-Bold',
        spaceBefore=8,
        spaceAfter=5,
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['BodyText'],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#222222'),
        spaceAfter=5,
    )

    link_box_style = ParagraphStyle(
        'LinkBox',
        parent=styles['Normal'],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#0D47A1'),
        fontName='Helvetica-Bold',
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        fontName='Helvetica-Bold',
        alignment=1,
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=7,
        leading=9,
        textColor=colors.HexColor('#222222'),
    )

    story = []

    # Cabeçalho Principal
    story.append(Paragraph("RELATÓRIO TÉCNICO & GUIA DE ENGENHARIA", title_style))
    story.append(Paragraph(
        "<b>HealthRoute AI — Otimização Evolutiva de Rotas Médicas (VRP) & IA Generativa</b><br/>"
        "Tech Challenge — Fase 2 | Pós-Graduação em Inteligência Artificial para Engenharia de Dados — FIAP<br/>"
        "<b>Status:</b> 100% Concluído & Integrado (50/50 Testes PASS) | <b>Data:</b> Novembro / 2026",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0D47A1'), spaceAfter=6))

    # Tabela de Entregáveis Oficiais
    story.append(Paragraph("IDENTIFICAÇÃO DOS ENTREGÁVEIS OFICIAIS (FASE 2)", h1_style))
    entregaveis = [
        [
            Paragraph("<b>Entregável Obrigatório</b>", table_header_style),
            Paragraph("<b>Canal Oficial / Link de Acesso</b>", table_header_style),
            Paragraph("<b>Conteúdo Validador</b>", table_header_style)
        ],
        [
            Paragraph("<b>Repositório Git Completo</b>", table_cell_style),
            Paragraph("<font color='#0D47A1'><u>https://github.com/willjrcristo/healthroute-ai</u></font>", link_box_style),
            Paragraph("Código-fonte completo, Docker Compose, dados públicos, documentação e 50 testes automatizados (100% PASS).", table_cell_style)
        ],
        [
            Paragraph("<b>Vídeo de Demonstração</b>", table_cell_style),
            Paragraph("<font color='#0D47A1'><u>https://vimeo.com/1243045935</u></font>", link_box_style),
            Paragraph("Demonstração audiovisual completa do sistema em execução ao vivo, convergência genética no Pygame, manifestos LLM e Q&A.", table_cell_style)
        ],
        [
            Paragraph("<b>Relatório Técnico</b>", table_cell_style),
            Paragraph("Disponibilizado no Git e em PDF no portal acadêmico FIAP", table_cell_style),
            Paragraph("Documento técnico formal detalhando formulação matemática, operadores genéticos, comparativo de abordagens e guia operacional.", table_cell_style)
        ]
    ]
    t_ent = Table(entregaveis, colWidths=[115, 220, 205])
    t_ent.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8F9FA')]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_ent)
    story.append(Spacer(1, 6))

    # 1. Sumário Executivo
    story.append(Paragraph("1. Sumário Executivo & Domínio Operacional", h1_style))
    story.append(Paragraph(
        "A logística hospitalar de insumos críticos e vacinas opera sob rigorosas restrições de tempo, temperatura e integridade. "
        "O <b>HealthRoute AI</b> soluciona o Problema de Roteamento de Veículos (VRP) multiobjetivo por meio de um Algoritmo Genético especializado "
        "(Ordered Crossover OX1, Swap Mutation e Elitismo Estrito), integrando frota heterogênea (capacidade de 45 a 50 kg, autonomia máxima de 35 a 40 km) "
        "e priorização clínica de Nível 1 e Nível 0 (UTI, hemocomponentes e soros antiofídicos no primeiro vértice da sub-rota).",
        body_style
    ))

    # 2. Formulação Matemática
    story.append(Paragraph("2. Formulação Matemática do VRP & Operadores Genéticos", h1_style))
    story.append(Paragraph(
        "O espaço de soluções é codificado em um cromossomo de permutação particionado dinamicamente entre os veículos com retorno obrigatório ao Depósito Central (0). "
        "A função de aptidão a ser minimizada integra a distância percorrida somada a barreiras de penalização quadrática:<br/>"
        "<b>min F(Π) = D_total + λ_cap · Σ max(0, C_m - C_max) + λ_aut · Σ max(0, D_m - D_max) + λ_prio · Σ Σ k · I(R_m,k ∈ V_crit)</b><br/>"
        "• <b>Hiperparâmetros de Penalidade:</b> λ_cap = 1000.0 (capacidade); λ_aut = 1000.0 (autonomia); λ_prio = 50.0 (prioridade temporal de entrega).<br/>"
        "• <b>Ordered Crossover (OX1):</b> Preserva blocos de adjacência relativos do Pai 1 e completa com os genes do Pai 2 sem duplicidade e sem omissão.<br/>"
        "• <b>Swap Mutation (15%):</b> Permuta dois genes estocasticamente, assegurando escape sistemático de mínimos locais.<br/>"
        "• <b>Elitismo Estrito (K=5):</b> Preserva os 5 melhores cromossomos a cada geração, assegurando convergência monotônica não-crescente.",
        body_style
    ))

    # 3. Comparativo de Desempenho
    story.append(Paragraph("3. Comparativo de Desempenho com Outras Abordagens de Roteamento", h1_style))
    story.append(Paragraph(
        "Conforme preconizado pelo edital, o desempenho do Algoritmo Genético foi confrontado contra o código base inicial (TSP monotípico) "
        "e uma heurística gulosa de vizinho mais próximo (Nearest Neighbor):",
        body_style
    ))
    dados_benchmark = [
        [
            Paragraph("<b>Critério / Métrica</b>", table_header_style),
            Paragraph("<b>TSP Monotípico (Código Base)</b>", table_header_style),
            Paragraph("<b>Heurística Gulosa (Nearest Neighbor)</b>", table_header_style),
            Paragraph("<b>Algoritmo Genético (HealthRoute AI)</b>", table_header_style)
        ],
        [
            Paragraph("Distância Total", table_cell_style),
            Paragraph("48,6 km (inviável operacionalmente)", table_cell_style),
            Paragraph("71,4 km (rotas desordenadas)", table_cell_style),
            Paragraph("<b>62,4 km</b> (otimizado para a frota)", table_cell_style)
        ],
        [
            Paragraph("Capacidade de Carga", table_cell_style),
            Paragraph("❌ <b>Falha Grave</b> (112 kg em 1 veículo)", table_cell_style),
            Paragraph("⚠️ Particionamento arbitrário", table_cell_style),
            Paragraph("✅ <b>100% Conforme</b> (≤ 45 kg por veículo)", table_cell_style)
        ],
        [
            Paragraph("Autonomia Máxima", table_cell_style),
            Paragraph("❌ <b>Falha Grave</b> (48,6 km; limite 35 km)", table_cell_style),
            Paragraph("⚠️ Violação nos veículos finais", table_cell_style),
            Paragraph("✅ <b>100% Conforme</b> (máximo 25,6 km)", table_cell_style)
        ],
        [
            Paragraph("SLA de Urgência Clínica", table_cell_style),
            Paragraph("❌ <b>0%</b> (emergências no fim do ciclo)", table_cell_style),
            Paragraph("❌ <b>33%</b> (ignora gravidade médica)", table_cell_style),
            Paragraph("✅ <b>100%</b> (críticos na 1ª perna de rota)", table_cell_style)
        ],
        [
            Paragraph("Tempo de Execução", table_cell_style),
            Paragraph("< 0,05 s", table_cell_style),
            Paragraph("< 0,01 s", table_cell_style),
            Paragraph("<b>0,08 a 0,11 s</b> (80 gerações)", table_cell_style)
        ]
    ]
    t_bench = Table(dados_benchmark, colWidths=[105, 135, 145, 155])
    t_bench.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8F9FA')]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_bench)
    story.append(Spacer(1, 6))

    # 4. Camada LLM & Novas Funcionalidades
    story.append(Paragraph("4. Camada Generativa (LLM) & Funcionalidades Avançadas", h1_style))
    story.append(Paragraph(
        "<b>A) Quatro Capacidades Centrais da LLM:</b> (1) Manifestos de Transporte passo a passo para motoristas com protocolos de cadeia fria (2°C a 8°C); "
        "(2) Relatório Executivo de Eficiência e confirmação de SLAs; (3) Diagnóstico de Gargalos e Sugestões de Melhorias; "
        "(4) Interface Conversacional de Q&A em linguagem natural para despacho e consultas analíticas.<br/>"
        "<b>B) Inclusão de Endereços via Links do Google Maps:</b> Capacidade de colar URLs do Google Maps (curtas <code>maps.app.goo.gl/...</code> ou completas). "
        "O sistema resolve o redirecionamento HTTP, extrai o nome do hospital e decodifica as coordenadas GPS reais sem custo de API.<br/>"
        "<b>C) Microdados Oficiais do SAMU 192 (DATASUS / AWS):</b> Script automatizado (<code>scripts/baixar_dados_publicos.py</code>) "
        "que ingere dados abertos do Ministério da Saúde na AWS, filtrando ambulâncias reais (USB, USA e VIR) da Grande Vitória e Região Serrana do ES.<br/>"
        "<b>D) Briefing dos Motoristas com Gestão de Flags:</b> Rastreamento do ciclo de vida de cada condutor (⚪ PENDENTE → 📱 ENVIADO → 🔄 RE-ENVIADO) "
        "com links turn-by-turn do Google Maps, checklist de insumos e comandos em linguagem natural (<i>'imprima o briefing do motorista Carlos'</i>).<br/>"
        "<b>E) Protocolo de Emergência Clínica Aguda (Código Vermelho):</b> Reconhecimento automático de acidentes agudos (ex: picada de cascavel), "
        "seleção imediata do <b>Soro Anticrotálico</b>, mapeamento rural (Santa Leopoldina) e disparo de rota expressa prioritária.<br/>"
        "<b>F) Carga de Cenário Regional Robusto:</b> Simulação em lote com 16 hospitais reais do ES (223 kg de demanda e 9 pontos de alta criticidade) "
        "e alocação de veículos por linguagem natural simplificada (<i>'adicione mais um veiculo'</i>).<br/>"
        "<b>G) Visualizações Gráficas Interativas:</b> Painel duplo animado em PyGame (mapa viário + convergência do fitness) e mapa interativo Leaflet (<code>output/rotas_google_maps.html</code>).",
        body_style
    ))

    # 5. Guia de Operação
    story.append(Paragraph("5. Guia Rápido de Comandos & Instruções do Operador", h1_style))
    comandos_dados = [
        [Paragraph("<b>Objetivo Operacional</b>", table_header_style), Paragraph("<b>Comando no Terminal Interativo (main.py)</b>", table_header_style)],
        [Paragraph("Ver Parâmetros & Ajuda", table_cell_style), Paragraph("<code>ajuda</code> ou <code>dados</code>", table_cell_style)],
        [Paragraph("Inserir Destino via Google Maps", table_cell_style), Paragraph("<code>https://maps.app.goo.gl/EaRSkrpGSee8kN8D9 precisa de 18kg de sangue</code>", table_cell_style)],
        [Paragraph("Lançar Emergência com Antiofídico", table_cell_style), Paragraph("<code>Uma criança picada por cascavel em Santa Leopoldina precisa de soro</code>", table_cell_style)],
        [Paragraph("Carregar Cenário Robusto (16 hospitais)", table_cell_style), Paragraph("<code>carregar cenario real</code> ou <code>carga robusta</code>", table_cell_style)],
        [Paragraph("Adicionar Ambulância na Frota", table_cell_style), Paragraph("<code>adicione mais um veiculo</code> ou <code>cadastrar veiculo ...</code>", table_cell_style)],
        [Paragraph("Ver Status de Envio aos Motoristas", table_cell_style), Paragraph("<code>status briefings</code> ou <code>painel motoristas</code>", table_cell_style)],
        [Paragraph("Imprimir / Reenviar Briefing Individual", table_cell_style), Paragraph("<code>imprimir briefing Carlos</code> ou <code>compartilhar briefing Ana</code>", table_cell_style)],
        [Paragraph("Reabrir Visualização no PyGame", table_cell_style), Paragraph("<code>abrir mapa</code> ou <code>pygame</code>", table_cell_style)],
        [Paragraph("Abrir Mapa Interativo no Navegador", table_cell_style), Paragraph("<code>abrir mapa real</code> ou <code>google maps</code>", table_cell_style)],
        [Paragraph("Recalcular Algoritmo Genético VRP", table_cell_style), Paragraph("<code>otimizar</code> ou <code>sim</code>", table_cell_style)],
    ]
    t_cmd = Table(comandos_dados, colWidths=[170, 370])
    t_cmd.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8F9FA')]),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_cmd)
    story.append(Spacer(1, 6))

    # 6. Resultados e Conclusão
    story.append(Paragraph("6. Resultados Experimentais, Conclusão & Garantia de Qualidade", h1_style))
    story.append(Paragraph(
        "• <b>Suíte de Testes Automatizados:</b> <b>50 testes automatizados (100% PASS)</b> via pytest validando operadores OX1/Swap, restrições VRP, prompts LLM, Google Maps e DATASUS.<br/>"
        "• <b>Convergência do Algoritmo Genético:</b> Redução de <b>43,9% no custo fitness</b> (111,12 → 62,37) em apenas <b>0,08 a 0,11 segundos</b> para 80 gerações.<br/>"
        "• <b>Conformidade de SLA Clínico:</b> <b>100% dos insumos críticos</b> (código vermelho e amarelo) alocados rigorosamente na primeira perna de rota da frota.<br/>"
        "• <b>Orquestração Docker & n8n:</b> Ambiente conteinerizado com webhook oficial ativo para despacho hospitalar na porta 5678.<br/>"
        "O <b>HealthRoute AI</b> consolida uma solução madura, com rigor matemático, aplicabilidade prática no SUS e integração robusta entre algoritmos combinatórios e inteligência artificial generativa.",
        body_style
    ))

    doc.build(story)
    print(f"PDF gerado com sucesso: {PDF_PATH}")

if __name__ == "__main__":
    gerar_pdf()
