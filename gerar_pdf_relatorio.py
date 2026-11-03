"""
Script para compilar o Relatório Técnico Oficial Atualizado em formato PDF.
Inclui metadados do projeto, links para o GitHub e Vimeo, formulação matemática,
arquitetura de microsserviços, guia operacional e resultados experimentais.
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

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
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0D47A1'),
        fontName='Helvetica-Bold',
        spaceAfter=4,
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#444444'),
        spaceAfter=10,
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading2'],
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#0D47A1'),
        fontName='Helvetica-Bold',
        spaceBefore=10,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['BodyText'],
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#222222'),
        spaceAfter=6,
    )

    link_box_style = ParagraphStyle(
        'LinkBox',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#0D47A1'),
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        textColor=colors.white,
        fontName='Helvetica-Bold',
        alignment=1,
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=7.5,
        leading=9.5,
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
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0D47A1'), spaceAfter=8))

    # Tabela de Entregáveis e Links Oficiais
    story.append(Paragraph("IDENTIFICAÇÃO DOS ENTREGÁVEIS OFICIAIS (FASE 2)", h1_style))
    entregaveis = [
        [
            Paragraph("<b>Entregável Obrigatório</b>", table_header_style),
            Paragraph("<b>Canal Oficial / Link de Acesso</b>", table_header_style),
            Paragraph("<b>Descrição / Conteúdo Validador</b>", table_header_style)
        ],
        [
            Paragraph("<b>Repositório Git Completo</b>", table_cell_style),
            Paragraph("<font color='#0D47A1'><u>https://github.com/willjrcristo/healthroute-ai</u></font>", link_box_style),
            Paragraph("Código-fonte completo, infraestrutura Docker Compose, documentação, dados públicos e suíte com 50 testes automatizados.", table_cell_style)
        ],
        [
            Paragraph("<b>Vídeo de Demonstração</b>", table_cell_style),
            Paragraph("<font color='#0D47A1'><u>https://vimeo.com/reviews/85747154-309e-481b-bb79-7fad42627151/videos/1243045935</u></font>", link_box_style),
            Paragraph("Demonstração audiovisual (Vimeo) do sistema em execução, convergência gráfica no Pygame, manifestos LLM, links Google Maps e Q&A.", table_cell_style)
        ],
        [
            Paragraph("<b>Relatório Técnico</b>", table_cell_style),
            Paragraph("Disponibilizado no Git e submetido em PDF no portal FIAP", table_cell_style),
            Paragraph("Documento técnico formal detalhando formulação matemática, operadores genéticos, integração com LLMs e guia operacional.", table_cell_style)
        ]
    ]
    t_ent = Table(entregaveis, colWidths=[120, 230, 190])
    t_ent.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8F9FA')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_ent)
    story.append(Spacer(1, 6))

    # 1. Sumário Executivo
    story.append(Paragraph("1. Sumário Executivo e Domínio Operacional", h1_style))
    story.append(Paragraph(
        "A logística hospitalar de insumos críticos e vacinas não tolera atrasos nem ruptura de temperatura. "
        "O <b>HealthRoute AI</b> resolve o Problema de Roteamento de Veículos (VRP) multiobjetivo por meio de um Algoritmo Genético especializado "
        "(Ordered Crossover OX1, Swap Mutation e Elitismo Estrito), acoplado a uma frota heterogênea (capacidade de 45 a 50 kg, autonomia máxima de 35 a 40 km) "
        "e priorização clínica estrita de Nível 1 e Nível 0 (UTI, hemocomponentes e soros antiofídicos no primeiro vértice da sub-rota).",
        body_style
    ))

    # Tabela comparativa
    dados_comp = [
        [Paragraph("<b>Critério Operacional</b>", table_header_style), Paragraph("<b>Logística Tradicional / Manual</b>", table_header_style), Paragraph("<b>HealthRoute AI (AG + VRP + LLM)</b>", table_header_style)],
        [Paragraph("Tempo de Planejamento", table_cell_style), Paragraph("Horas em planilhas desconexas", table_cell_style), Paragraph("<b>< 0,15 segundos</b> (AG vetorizado)", table_cell_style)],
        [Paragraph("Gestão de Restrições", table_cell_style), Paragraph("Violações frequentes de carga e km", table_cell_style), Paragraph("<b>Zero violações</b> (penalidades quadráticas)", table_cell_style)],
        [Paragraph("Prioridade Clínica", table_cell_style), Paragraph("Subjetiva e sujeita a omissões humanas", table_cell_style), Paragraph("<b>100% de conformidade de SLA clínico</b>", table_cell_style)],
        [Paragraph("Comunicação com a Frota", table_cell_style), Paragraph("Pranchetas e recados informais", table_cell_style), Paragraph("<b>Manifestos estruturados via LLM</b> e GPS turn-by-turn", table_cell_style)],
        [Paragraph("Tratamento de Emergências", table_cell_style), Paragraph("Comunicação verbal desordenada", table_cell_style), Paragraph("<b>Protocolo Código Vermelho</b> (raciocínio clínico automático)", table_cell_style)],
    ]
    t_comp = Table(dados_comp, colWidths=[130, 180, 230])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8F9FA')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 6))

    # 2. Formulação Matemática
    story.append(Paragraph("2. Formulação Matemática do VRP & Operadores Genéticos", h1_style))
    story.append(Paragraph(
        "O espaço de soluções é codificado em um cromossomo de permutação dinamicamente particionado entre os veículos com reinjeção obrigatória do Depósito Central (0). "
        "A função de aptidão a ser minimizada integra a distância percorrida somada a barreiras de penalização:<br/>"
        "<b>min F(Π) = D_total + λ_cap · Σ max(0, C_m - C_max) + λ_aut · Σ max(0, D_m - D_max) + λ_prio · Σ Σ k · I(R_m,k ∈ V_crit)</b><br/>"
        "• <b>Hiperparâmetros:</b> λ_cap = 1000.0 (capacidade); λ_aut = 1000.0 (autonomia); λ_prio = 50.0 (prioridade temporal de entrega).<br/>"
        "• <b>Ordered Crossover (OX1):</b> Preserva blocos de adjacência do Pai 1 e preenche as demais posições com a ordem do Pai 2 sem duplicidade.<br/>"
        "• <b>Swap Mutation (15%):</b> Permuta dois genes estocasticamente, assegurando escape sistemático de mínimos locais.<br/>"
        "• <b>Elitismo Estrito (K=5):</b> Preserva os 5 melhores cromossomos a cada ciclo geracional, garantindo convergência não-crescente.",
        body_style
    ))

    # 3. Funcionalidades Avançadas
    story.append(Paragraph("3. Recursos Implementados & Extensões de Alto Nível", h1_style))
    story.append(Paragraph(
        "<b>A) Visualização Gráfica em PyGame & Web Leaflet:</b> Painel duplo animado com mapa 2D dos hospitais no grid 10×10 km e gráfico de convergência geracional do fitness, além de mapa interativo geográfico (Leaflet) em <code>output/rotas_google_maps.html</code>.<br/>"
        "<b>B) Inclusão de Destinos via Links do Google Maps:</b> Capacidade de colar URLs encurtadas (<code>maps.app.goo.gl/...</code>) ou completas; o sistema decodifica redirecionamentos HTTP, extrai o nome do hospital e decodifica as coordenadas geodésicas reais.<br/>"
        "<b>C) Download de Microdados Oficiais do SAMU 192 (DATASUS):</b> Script automatizado (<code>scripts/baixar_dados_publicos.py</code>) que consome dados abertos do Ministério da Saúde na AWS, extraindo viaturas USB, USA e VIR reais da Grande Vitória e Região Serrana do ES.<br/>"
        "<b>D) Camada Generativa Multimodal (LLM):</b> Geração de manifestos operacionais detalhados para motoristas com protocolos de cadeia fria (2°C a 8°C), relatórios executivos de eficiência, motor de diagnóstico e interface conversacional de Q&A.<br/>"
        "<b>E) Briefings para Motoristas com Controle de Flags:</b> Emissão individual de briefings, geração de rotas GPS turn-by-turn do Google Maps e rastreamento do ciclo de vida de despacho (⚪ PENDENTE → 📱 ENVIADO → 🔄 RE-ENVIADO) em linguagem natural.<br/>"
        "<b>F) Protocolo de Emergência Clínica (Código Vermelho):</b> Raciocínio clínico capaz de identificar acidentes agudos (ex: picada de cascavel), selecionar o <b>Soro Anticrotálico</b> correspondente e mobilizar despacho expresso imediato.<br/>"
        "<b>G) Carga de Cenário Regional Robusto:</b> Simulação em lote com 16 hospitais reais simultâneos no Espírito Santo (223 kg de demanda e 9 pontos críticos) e alocação de veículos em linguagem natural (<i>'adicione mais um veiculo'</i>).",
        body_style
    ))

    # 4. Instruções de Operação
    story.append(Paragraph("4. Guia Rápido de Instruções & Comandos do Operador", h1_style))
    comandos_dados = [
        [Paragraph("<b>Objetivo Operacional</b>", table_header_style), Paragraph("<b>Comando no Terminal Interativo (main.py)</b>", table_header_style)],
        [Paragraph("Ver Dados & Guia de Ajuda", table_cell_style), Paragraph("<code>ajuda</code> ou <code>dados</code>", table_cell_style)],
        [Paragraph("Inserir Destino via Google Maps", table_cell_style), Paragraph("<code>https://maps.app.goo.gl/EaRSkrpGSee8kN8D9 precisa de 18kg de sangue</code>", table_cell_style)],
        [Paragraph("Lançar Emergência com Antiofídico", table_cell_style), Paragraph("<code>Uma criança picada por cascavel em Santa Leopoldina precisa de soro</code>", table_cell_style)],
        [Paragraph("Carregar Cenário Robusto (16 hospitais)", table_cell_style), Paragraph("<code>carregar cenario real</code> ou <code>carga robusta</code>", table_cell_style)],
        [Paragraph("Adicionar Ambulância na Frota", table_cell_style), Paragraph("<code>adicione mais um veiculo</code> ou <code>cadastrar veiculo ...</code>", table_cell_style)],
        [Paragraph("Ver Status de Envio aos Motoristas", table_cell_style), Paragraph("<code>status briefings</code> ou <code>painel motoristas</code>", table_cell_style)],
        [Paragraph("Imprimir/Compartilhar com Motorista", table_cell_style), Paragraph("<code>imprimir briefing Carlos</code> ou <code>compartilhar briefing Ana</code>", table_cell_style)],
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
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_cmd)
    story.append(Spacer(1, 6))

    # 5. Resultados Experimentais
    story.append(Paragraph("5. Resultados Experimentais & Garantia de Qualidade", h1_style))
    story.append(Paragraph(
        "• <b>Suíte de Testes Automatizados:</b> <b>50 testes automatizados (100% PASS)</b> via pytest cobrindo operadores OX1/Swap, restrições VRP, prompts LLM, Google Maps e DATASUS.<br/>"
        "• <b>Convergência do Algoritmo Genético:</b> Redução de <b>43,9% no custo fitness</b> (111,12 → 62,37) em apenas <b>0,08 a 0,11 segundos</b> para 80 gerações.<br/>"
        "• <b>Conformidade de SLA Clínico:</b> <b>100% dos insumos críticos</b> (código vermelho e amarelo) alocados rigorosamente na primeira perna de rota da frota.<br/>"
        "• <b>Infraestrutura de Microsserviços Docker:</b> Orquestração containerizada da aplicação e serviço <b>n8n</b> integrado via Webhook na porta 5678.",
        body_style
    ))

    doc.build(story)
    print(f"PDF gerado com sucesso: {PDF_PATH}")

if __name__ == "__main__":
    gerar_pdf()
