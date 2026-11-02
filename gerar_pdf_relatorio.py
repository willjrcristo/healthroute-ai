"""
Script para compilar o Relatório Técnico Atualizado em formato PDF formatado.
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
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0D47A1'),
        fontName='Helvetica-Bold',
        spaceAfter=6,
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#555555'),
        spaceAfter=15,
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0D47A1'),
        fontName='Helvetica-Bold',
        spaceBefore=14,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['BodyText'],
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#222222'),
        spaceAfter=8,
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#B71C1C'),
        fontName='Helvetica-Bold',
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        fontName='Helvetica-Bold',
        alignment=1,
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#222222'),
    )

    story = []

    # Cabeçalho
    story.append(Paragraph("RELATÓRIO TÉCNICO & GUIA DE ENGENHARIA", title_style))
    story.append(Paragraph("<b>HealthRoute AI — Otimização Evolutiva de Rotas Médicas (VRP) & IA Generativa</b><br/>Tech Challenge Fase 2 | Pós-Graduação em IA e Engenharia de Dados — FIAP | Status: 100% Concluído (40/40 Testes PASS)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0D47A1'), spaceAfter=12))

    # 1. Sumário Executivo
    story.append(Paragraph("1. Sumário Executivo e Objetivos da Otimização Médica", h1_style))
    story.append(Paragraph(
        "A distribuição de suprimentos farmacêuticos e insumos de emergência opera sob restrições extremas de tempo, temperatura e integridade. "
        "O <b>HealthRoute AI</b> soluciona o Problema de Roteamento de Veículos (VRP) multiobjetivo por meio de um Algoritmo Genético especializado "
        "(Ordered Crossover OX1 e Swap Mutation), integrando frota heterogênea (45 a 50 kg de capacidade, 35 a 40 km de autonomia) e priorização clínica de Nível 1 e Nível 0 "
        "(UTI, hemoderivados e soros antiofídicos no primeiro vértice de cada sub-rota).",
        body_style
    ))

    # Tabela comparativa
    dados_comp = [
        [Paragraph("<b>Critério Operacional</b>", table_header_style), Paragraph("<b>Logística Tradicional / Manual</b>", table_header_style), Paragraph("<b>HealthRoute AI (AG + VRP + LLM)</b>", table_header_style)],
        [Paragraph("Tempo de Planejamento", table_cell_style), Paragraph("Horas em planilhas desconexas", table_cell_style), Paragraph("<b>< 0,15 segundos</b> (AG convergente)", table_cell_style)],
        [Paragraph("Gestão de Restrições", table_cell_style), Paragraph("Violações frequentes de carga e km", table_cell_style), Paragraph("<b>Zero violações</b> (penalidades estritas)", table_cell_style)],
        [Paragraph("Prioridade Clínica", table_cell_style), Paragraph("Subjetiva e sujeita a omissões", table_cell_style), Paragraph("<b>100% dos SLAs críticos atendidos</b>", table_cell_style)],
        [Paragraph("Despacho de Emergências", table_cell_style), Paragraph("Comunicação verbal desordenada", table_cell_style), Paragraph("<b>Código Vermelho</b> (antiofídicos e rota expressa)", table_cell_style)],
    ]
    t_comp = Table(dados_comp, colWidths=[140, 180, 210])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F9F9F9')]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 10))

    # 2. Arquitetura do AG
    story.append(Paragraph("2. Modelagem Matemática do VRP & Operadores Genéticos", h1_style))
    story.append(Paragraph(
        "Diferente do TSP convencional monopostual, o cromossomo é decodificado dinamicamente entre os veículos com reinjeção obrigatória do Depósito Central (0). "
        "A função de aptidão avalia a distância acumulada somada a penalidades quadráticas severas:<br/>"
        "<b>Custo Fitness = D_total + (P_prioridade × 50.0) + (V_capacidade × 1000.0) + (V_autonomia × 1000.0)</b><br/>"
        "• <b>Ordered Crossover (OX1):</b> Preserva subcadeias contíguas do Pai 1 e completa com a ordem do Pai 2 sem duplicidade genética.<br/>"
        "• <b>Swap Mutation (15%):</b> Permuta dois genes estocasticamente, assegurando escape de mínimos locais.<br/>"
        "• <b>Elitismo Estrito (K=5):</b> Preserva as melhores soluções a cada geração, garantindo convergência monotônica.",
        body_style
    ))

    # 3. Novas Funcionalidades
    story.append(Paragraph("3. Novas Funcionalidades Avançadas Implementadas", h1_style))
    story.append(Paragraph(
        "<b>A) Visualização Gráfica em PyGame:</b> Painel duplo interativo com mapa 2D dos nós hospitalares no grid 10×10 km e gráfico de convergência do fitness atualizado geração a geração em tempo real.<br/>"
        "<b>B) Camada LLM com 4 Capacidades:</b> Manifestos operacionais passo a passo para os motoristas, relatórios gerenciais de eficiência, motor de diagnóstico e sugestão de melhorias, e interface interativa de Q&A.<br/>"
        "<b>C) Gestão de Lotes & Ingestão em Linguagem Natural:</b> Lançamento de pedidos livres via texto pelo operador (ex: <i>'O Hospital X precisa de 18kg de bolsas de sangue'</i>), importação de planilhas CSV e re-otimização instantânea.<br/>"
        "<b>D) Protocolo de Emergência Clínica (Código Vermelho):</b> Raciocínio clínico capaz de diagnosticar acidentes agudos (ex: <i>picada de cascavel em Santa Leopoldina</i>), selecionar o <b>Soro Anticrotálico</b>, determinar o posto rural e acionar rota expressa imediata.<br/>"
        "<b>E) Parametrização em Tempo Real:</b> Ajuste dinâmico de coordenadas e título da Base Operacional, cadastro e exclusão de furgões/ambulâncias (placa, modelo, consumo, hodômetro) e alteração de volumes de pedidos.",
        body_style
    ))

    # 4. Instruções de Uso
    story.append(Paragraph("4. Guia Rápido de Comandos & Instruções de Operação", h1_style))
    comandos_dados = [
        [Paragraph("<b>Objetivo</b>", table_header_style), Paragraph("<b>Comando no Prompt Interativo (main.py)</b>", table_header_style)],
        [Paragraph("Ver Dados de Entrada & Guia", table_cell_style), Paragraph("<code>ajuda</code> ou <code>dados</code>", table_cell_style)],
        [Paragraph("Lançar Emergência com Antiofídico", table_cell_style), Paragraph("<code>Uma criança foi picada por uma cascavel em Santa Leopoldina, precisa de antiofídico</code>", table_cell_style)],
        [Paragraph("Fechar Lote e Despachar Rota", table_cell_style), Paragraph("<code>otimizar</code> ou <code>sim</code>", table_cell_style)],
        [Paragraph("Consultar Catálogo de Soros / Remédios", table_cell_style), Paragraph("<code>catalogo insumos</code>", table_cell_style)],
        [Paragraph("Consultar Destinos / Hospitais Reais", table_cell_style), Paragraph("<code>destinos reais</code>", table_cell_style)],
        [Paragraph("Cadastrar Veículo na Frota", table_cell_style), Paragraph("<code>cadastrar veiculo V-104 motorista Marcos modelo Van Fiorino placa ABC-1234 capacidade 50 autonomia 40</code>", table_cell_style)],
        [Paragraph("Ajustar Volume de Pedido Existente", table_cell_style), Paragraph("<code>ajustar pedido 2 para 35 kg</code>", table_cell_style)],
        [Paragraph("Importar Planilha de Pedidos CSV", table_cell_style), Paragraph("<code>importar pedidos_exemplo.csv</code>", table_cell_style)],
    ]
    t_cmd = Table(comandos_dados, colWidths=[180, 350])
    t_cmd.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F9F9F9')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_cmd)
    story.append(Spacer(1, 10))

    # 5. Resultados e Testes
    story.append(Paragraph("5. Resultados Experimentais & Qualidade de Código", h1_style))
    story.append(Paragraph(
        "• <b>Suíte de Testes Automatizados:</b> <b>40 testes (100% PASS)</b> via pytest cobrindo operadores genéticos, restrições da frota, catálogos e emergências.<br/>"
        "• <b>Convergência do Algoritmo:</b> Redução de <b>43,9% no fitness</b> (111,12 → 62,37) em apenas <b>0,08 segundos</b> para 80 gerações.<br/>"
        "• <b>Conformidade de SLA:</b> <b>100% dos medicamentos críticos</b> entregues na primeira perna de rota de cada veículo.<br/>"
        "• <b>Arquitetura Docker:</b> Orquestração completa do container Python e nó oficial do <b>n8n</b> na porta 5678.",
        body_style
    ))

    doc.build(story)
    print(f"PDF gerado com sucesso: {PDF_PATH}")

if __name__ == "__main__":
    gerar_pdf()
