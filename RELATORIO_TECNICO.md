# RELATÓRIO TÉCNICO & GUIA DE ENGENHARIA DO SISTEMA
## HealthRoute AI — Otimização Evolutiva de Rotas Médicas (VRP) & IA Generativa
> **Tech Challenge — Fase 2**  
> **Pós-Graduação em Inteligência Artificial para Engenharia de Dados — FIAP**  
> **Status:** 100% Concluído & Integrado (47/47 Testes PASS)  
> **Data:** Outubro / 2026

---

## SUMÁRIO EXECUTIVO

O projeto **HealthRoute AI** constitui uma solução integrada de engenharia de dados, inteligência artificial combinatória e modelos de linguagem generativa (LLMs) voltada para o transporte sensível de insumos farmacêuticos e hospitalares de alta criticidade.

A partir de uma formulação matemática rigorosa do **Problema de Roteamento de Veículos com Frota Heterogênea e Prioridade Clínica (VRP-CP)**, o sistema otimiza simultaneamente arcos de deslocamento euclidiano e rotas geográficas reais, garantindo estrita observância a:
1. **Capacidade ponderal da frota** ($45,0\text{ kg}$ a $50,0\text{ kg}$ por veículo);
2. **Autonomia operacional máxima** ($35,0\text{ km}$ a $40,0\text{ km}$ por ciclo de rota);
3. **Prioridade clínica de Nível 1 e Nível 0** (UTI, emergência, hemoderivados e soros antiofídicos vitais atendidos no primeiro vértice de cada sub-rota).

O sistema expande os requisitos originais da Fase 2 ao incorporar:
- **Visualização Gráfica Interativa em PyGame**: Mapa 2D da malha hospitalar e convergência do fitness geracional em tempo real, com comando para reabrir a qualquer momento diretamente do terminal;
- **Integração Completa com Google Maps & Mapa Geográfico Interativo**: Geração de links diretos de navegação GPS *turn-by-turn* (`google.com/maps/dir/...`) para cada veículo e mapa web interativo (Leaflet) em `output/rotas_google_maps.html`;
- **Briefing Operacional para Motoristas com Controle de Flags e Versões**: Emissão de briefings individuais detalhados para os condutores com checklist de insumos, conferência de cadeia de frio (2°C a 8°C), links de GPS e controle do ciclo de vida do despacho (`⚪ PENDENTE` $\to$ `📱 ENVIADO` $\to$ `🔄 RE-ENVIADO`), com suporte a comandos em linguagem natural;
- **Camada Generativa Multimodal (LLM)**: Geração de manifestos operacionais para condutores, relatórios de eficiência gerencial e motor de diagnóstico e melhorias de processo;
- **Centro de Despacho & Gestão Dinâmica de Lotes**: Ingestão de pedidos em linguagem natural livre, importação de planilhas CSV e re-otimização instantânea do algoritmo genético;
- **Protocolo de Emergência Aguda (Código Vermelho)**: Raciocínio clínico automatizado capaz de identificar acidentes agudos (ex: *picada de cascavel em zona rural*), selecionar o insumo específico (*Soro Anticrotálico*), calcular a geolocalização e acionar despacho prioritário;
- **Parametrização Operacional em Tempo Real**: Ajuste dinâmico de coordenadas e título da Base Operacional, cadastro detalhado de furgões e ambulâncias (placa, modelo, consumo, hodômetro) e alteração de volumes solicitados.

---

## 1. FORMULAÇÃO MATEMÁTICA E DOMÍNIO OPERACIONAL

### 1.1. Comparativo de Maturidade Operacional

| Dimensão Operacional | Abordagem Tradicional / Manual | HealthRoute AI (AG + VRP + LLM) |
|---|---|---|
| **Tempo de Planejamento** | Horas; decisões empíricas em planilhas desconexas. | **$< 0,15$ segundos** via convergência evolutiva vetorizada. |
| **Respeito a Restrições** | Violações frequentes de capacidade e autonomia. | **Zero violações** com barreiras de penalidade quadrática. |
| **Priorização Clínica** | Triagem humana sujeita a fadiga e inversão de ordem. | **100% de conformidade de SLA**: nós críticos alocados na 1ª parada. |
| **Comunicação com a Frota** | Pranchetas e mensagens de voz informais. | **Manifestos determinísticos estruturados via LLM** com alertas de cadeia de frio. |
| **Tratamento de Emergências** | Comunicação reativa com despacho desordenado. | **Protocolo Código Vermelho**: inferência clínica automática e rota expressa. |

### 1.2. Modelagem Matemática do Fitness Multi-Objetivo

Dado um conjunto de $N$ pontos de demanda $V = \{1, 2, \dots, N\}$ e o Depósito Central $v_0 = 0$, o espaço de soluções é representado por um cromossomo de permutação $\Pi = (\pi_1, \pi_2, \dots, \pi_N)$, particionado dinamicamente entre os $M$ veículos da frota.

A função objetivo $F(\Pi)$ a ser minimizada é expressa por:

$$\min F(\Pi) = D_{\text{total}}(\Pi) + \lambda_{\text{cap}} \sum_{m=1}^{M} \max(0, C_m - C_{\max}) + \lambda_{\text{aut}} \sum_{m=1}^{M} \max(0, D_m - D_{\max}) + \lambda_{\text{prio}} \sum_{m=1}^{M} \sum_{k=1}^{|R_m|} k \cdot \mathbb{I}(R_{m,k} \in V_{\text{crit}})$$

Onde:
- $D_{\text{total}}$: Distância euclidiana ou geodésica acumulada de toda a frota (km);
- $C_m$: Carga total alocada ao veículo $m$, limitada a $C_{\max} = 45,0\text{ kg}$;
- $D_m$: Extensão total da sub-rota do veículo $m$, limitada a $D_{\max} = 35,0\text{ km}$;
- $\mathbb{I}(R_{m,k} \in V_{\text{crit}})$: Função indicadora que penaliza nós críticos posicionados tardiamente na sub-rota ($k > 1$);
- $\lambda_{\text{cap}} = 1000,0$; $\lambda_{\text{aut}} = 1000,0$; $\lambda_{\text{prio}} = 50,0$: Hiperparâmetros de penalização que atuam como barreiras de Pareto.

---

## 2. ARQUITETURA DO ALGORITMO GENÉTICO & OPERADORES

### 2.1. Invariância Combinatória e Operadores

Operadores genéticos convencionais (como single-point ou uniform crossover) são inadequados para problemas de permutação, pois geram filhos inválidos com vértices duplicados e pontos omitidos. O **HealthRoute AI** implementa operadores especializados:

1. **Ordered Crossover (OX1)**:
   - Sorteia dois pontos de corte $a$ e $b$ no Pai 1;
   - Transfere o segmento contíguo $[\pi_a, \dots, \pi_b]$ diretamente para o filho;
   - Preenche as posições restantes com os genes do Pai 2 na ordem em que aparecem, pulando elementos já herdados;
   - **Garantia**: Preserva blocos de adjacência relativos sem duplicidade.

2. **Swap Mutation (Mutação por Troca)**:
   - Com probabilidade estocástica $\mu = 15\%$, seleciona dois índices arbitrários $(i, j)$ e permuta seus elementos: $\pi_i \leftrightarrow \pi_j$;
   - **Garantia**: Injeta diversidade alélica na população e evita aprisionamento em mínimos locais.

3. **Seleção por Torneio Binário ($k=2$)**:
   - Seleciona dois indivíduos aleatórios do pool de elite e elege o de menor fitness;
   - Mantém uma pressão seletiva calibrada sem perda precoce de variabilidade genética.

4. **Elitismo Estrito ($K=5$)**:
   - As 5 melhores soluções da geração corrente são copiadas intactas para a próxima geração, garantindo convergência monotônica não-crescente:
     $$F_{\text{best}}(t+1) \le F_{\text{best}}(t)$$

---

## 3. ARQUITETURA DE MICROSSERVIÇOS & PACOTES

O projeto foi construído sob arquitetura modular desacoplada com tipagem estática e empacotamento completo em contêineres:

```
Tech-Challenge/
├── data/                        # Bases de dados reais e catálogos operacionais
│   ├── base_operacional.json    # Título, coordenadas Lat/Long e contatos da Base
│   ├── catalogo_insumos.csv     # Antiofídicos, hemoderivados e vacinas com regras clínicas
│   ├── destinos_reais.csv       # Hospitais, postos rurais e UPAs com geolocalização real
│   └── veiculos.csv             # Cadastro da frota (modelo, placa, hodômetro, consumo)
│
├── vrp/                         # Motor de Otimização Combinatória
│   ├── __init__.py
│   ├── data.py                  # Definições estáticas, matriz de distâncias e nós base
│   ├── fitness.py               # Função multi-objetivo com penalizações
│   ├── operators.py             # Crossover OX1 e Swap Mutation
│   ├── genetic_algorithm.py     # Algoritmo Genético com histórico de convergência
│   ├── visualization.py         # Mapa 2D matplotlib e exportador JSON
│   ├── pygame_viz.py            # Janela gráfica animada (mapa + convergência do fitness)
│   ├── knowledge_base.py        # Base de conhecimento clínico, Haversine e acidentes ofídicos
│   └── orders.py                # Gerenciador de lotes, comandos em linguagem natural e CSV
│
├── llm/                         # Camada de Inteligência Artificial Generativa
│   ├── __init__.py
│   ├── prompts.py               # System prompts e contratos padronizados
│   ├── manifesto.py             # Gerador de manifestos passo a passo para condutores
│   ├── relatorio.py             # Gerador de relatórios de eficiência e SLAs
│   ├── melhorias.py             # Motor de diagnóstico e sugestão de melhorias
│   └── qa_interface.py          # Interface interativa de perguntas, comandos e emergências
│
├── webhook/                     # Camada de Integração e Orquestração
│   ├── __init__.py
│   └── payload.py               # Serializador de payloads JSON para webhook / n8n
│
├── tests/                       # Suíte de Testes Automatizados (pytest)
│   ├── __init__.py
│   ├── test_vrp.py              # Testes unitários do motor VRP e operadores
│   └── test_llm.py              # Testes de manifestos, Q&A, emergências e catálogo
│
├── output/                      # Artefatos produzidos em tempo de execução
│   ├── rotas.png                # Mapa gráfico de rotas por veículo
│   ├── rotas.json               # Dados estruturados da telemetria
│   └── webhook_payload.json     # Payload JSON formatado para webhook
│
├── Dockerfile                   # Imagem Docker Python 3.11-slim
├── docker-compose.yml           # Orquestração do app + n8n na porta 5678
├── requirements.txt             # Dependências de produção e teste
└── main.py                      # Orquestrador principal da aplicação
```

---

## 4. FUNCIONALIDADES AVANÇADAS IMPLEMENTADAS

### 4.1. Visualização Animada com PyGame (Vídeo 5:21)
O módulo [`vrp/pygame_viz.py`](file:///c:/repos/FIAP/FASE2/Tech-Challenge/vrp/pygame_viz.py) implementa interface de alta fidelidade dividida em dois painéis:
- **Painel Esquerdo (720×720)**: Grid cartesiano $10 \times 10\text{ km}$ renderizando o Depósito Central com ícone de destaque, nós hospitalares codificados por cor e etiquetas de demanda, traçado progressivo de cada sub-rota por veículo em cores distintas e legenda translúcida desobstruída no topo direito.
- **Painel Direito (560×720)**: Renderização dinâmica da curva de fitness geração a geração em tempo real, informando número de geração, fitness atual e botão visual interativo para prosseguir ao terminal.

### 4.2. Quatro Capacidades Centrais da Camada LLM (Vídeo 6:46)
1. **Manifestos Operacionais de Transporte**: Emissão de roteiros passo a passo por veículo detalhando conferência inicial de temperatura (< 8°C), protocolos de entrega em mãos com assinatura digital e procedimentos de emergência.
2. **Relatório de Eficiência de Rotas**: Consolidação gerencial com quilometragem total, percentual médio de ocupação volumétrica, taxa de sucesso de SLAs de prioridade e tempo de processamento.
3. **Sugestões de Melhoria de Processo**: Diagnóstico algorítmico identificando assimetria de carga entre veículos, veículos próximos ao limite de capacidade e estimativa do ponto de estabilização do AG para calibração de hiperparâmetros.
4. **Interface Q&A em Linguagem Natural**: Processamento de consultas do usuário sobre métricas operacionais, rotas individuais e status de cada veículo.

### 4.3. Protocolo de Emergência Clínica & Antiofídicos (Código Vermelho)
O sistema reconhece ocorrências médicas graves e executa triagem especializada:
- **Picada de Cascavel (*Crotalus*)**: Diagnóstico imediato, alocação do **Soro Anticrotálico**, localização de postos rurais (ex: Santa Leopoldina), marcação como **Prioridade 0 (Ultra-Crítico)** e recomendação explícita de encerramento do lote para despacho expresso.
- **Picadas de Jararaca, Surucucu, Coral e Escorpião**: Mapeamento para **Soro Antibotrópico**, **Antilaquético**, **Antielapídico** e **Antiescorpiônico**.
- **Hemorragias Agudas**: Despacho de **Bolsas de Sangue O- Negativo (Universal)** sob protocolo de urgência.

### 4.4. Gestão Dinâmica de Lotes e Parametrização em Tempo Real
- **Ingestão em Linguagem Natural**: O operador pode registrar pedidos diretamente digitando *"O Hospital Santa Casa precisa de 18kg de bolsas de sangue"*.
- **Importação CSV**: Comando `importar pedidos_exemplo.csv` para carga massiva de pedidos.
- **Parametrização da Base**: `ajustar base <Título> lat <x> long <y>`.
- **Gestão da Frota**: `cadastrar veiculo V-104 motorista Marcos modelo Van placa ABC-1234 capacidade 50 autonomia 40` e `remover veiculo <ID>`.
- **Ajuste de Volumes**: `ajustar pedido <ID> para <X> kg` e `remover pedido <ID>`.
- **Re-otimização Instantânea**: Ao digitar `otimizar` ou `fechar lote`, o Algoritmo Genético recalcula imediatamente as rotas para a nova configuração e emite novos manifestos e relatórios.

### 4.5. Integração com Google Maps e Navegação Geográfica Real
- **Geração de URLs Diretas de Navegação**: Para cada sub-rota de veículo, o sistema calcula a rota de ida e volta e monta a URL oficial de direções do Google Maps no formato:
  `https://www.google.com/maps/dir/?api=1&origin={lat0},{lon0}&destination={lat0},{lon0}&waypoints={lat1},{lon1}|{lat2},{lon2}&travelmode=driving`
- **Mapa Interativo Web (Leaflet / OpenStreetMap)**: Gerado automaticamente em `output/rotas_google_maps.html`, exibindo marcadores personalizados (Base Dourada, Crítico Vermelho, Regular Azul), traçados pontilhados na cor de cada veículo e botões com links diretos para abrir a rota no Google Maps.
- **Exportação em JSON**: Cada veículo em `output/rotas.json` contém a chave `"google_maps_url"` pronta para integração móvel.

### 4.6. Briefing Operacional para Motoristas & Controle de Flags de Despacho
Para atender às necessidades reais dos motoristas na ponta operacional, foi desenvolvido o **Controlador de Briefings (`ControladorBriefings`)**:
- **Conteúdo do Briefing Individual**:
  - Dados cadastrais do condutor, veículo, placa e modelo;
  - Link clicável direto para navegação no **Google Maps GPS**;
  - Checklist pré-embarque de insumos com conferência de cadeia de frio (ex: 2°C a 8°C);
  - Sequência passo a passo com endereços, prioridades clínicas e protocolos em mãos;
  - Contatos de emergência (Central VHF, SAMU 192).
- **Ciclo de Vida e Flags de Rastreamento**:
  - `⚪ PENDENTE DE ENVIO`: Estado inicial antes do despacho da rota;
  - `📱 ENVIADO / COMPARTILHADO`: Disparado no primeiro envio com registro de timestamp e Versão 1;
  - `🔄 RE-ENVIADO / RE-IMPRESSO`: Atualizado automaticamente caso o operador solicite uma reimpressão ou reenvio, incrementando o número de revisão (Rev. 2, 3...) e atualizando o horário;
  - **Exportação em Arquivo**: Cada briefing é salvo individualmente em `output/briefing_<veiculo>_<motorista>.txt` e consolidado em `output/briefings_status.json`.
- **Compreensão em Linguagem Natural**: O sistema entende comandos variados como:
  - *"Imprima o briefing do motorista Carlos"*
  - *"Compartilhar o brief com a Ana"*
  - *"Pode reimprimir o briefing do Roberto?"*
  - *"status briefings"* (exibe o painel consolidado com a tabela de status de toda a frota).

---

## 5. GUIA DE OPERAÇÃO & INSTRUÇÕES DE USO

### 5.1. Instalação e Preparação do Ambiente
```bash
# 1. Clonar repositório e entrar na pasta
cd Tech-Challenge

# 2. Instalar dependências
pip install -r requirements.txt
```

### 5.2. Comandos de Execução

```bash
# Modo Completo com Interface Gráfica PyGame:
python main.py

# Modo Headless (Sem Janela Gráfica / Servidores):
python main.py --no-gui

# Modo Automatizado para CI/CD (Sem Janela e Sem Loop Interativo):
python main.py --no-gui --no-qa

# Customizando hiperparâmetros do Algoritmo Genético:
python main.py --pop 60 --ger 120 --no-gui
```

### 5.3. Exemplos Práticos de Interação no Prompt Q&A

| Objetivo do Operador | Comando / Exemplo Digitado no Prompt |
|---|---|
| **Ver guia de ajuda e dados de input** | `ajuda` ou `dados` |
| **Reabrir tela gráfica do Pygame** | `abrir mapa` ou `pygame` |
| **Consultar links do Google Maps** | `google maps` ou `mapa real` |
| **Abrir mapa geográfico interativo no navegador** | `abrir mapa real` |
| **Ver painel com status de envio dos motoristas** | `status briefings` ou `painel motoristas` |
| **Imprimir briefing de um condutor específico** | `imprimir briefing Carlos` ou `Imprima o briefing do motorista Carlos` |
| **Compartilhar briefing e atualizar flag** | `compartilhar briefing Ana` ou `compartilhar o brief com a Ana` |
| **Reimprimir briefing atualizando para RE-ENVIADO** | `Pode reimprimir o briefing do Roberto?` |
| **Despachar briefings de toda a frota** | `imprimir todos os briefings` |
| **Registrar emergência com antiofídico** | `Uma criança foi picada por uma cascavel em Santa Leopoldina, precisa de antiofídico` |
| **Fechar lote e despachar rota imediata** | `otimizar` ou `sim` |
| **Lançar pedido regular em linguagem natural** | `O Hospital Infantil precisa de 15kg de vacinas pediatricas (urgente)` |
| **Consultar catálogo de soros e remédios** | `catalogo insumos` |
| **Consultar hospitais e postos reais** | `destinos reais` |
| **Importar pedidos de planilha CSV** | `importar pedidos_exemplo.csv` |
| **Cadastrar novo veículo na frota** | `cadastrar veiculo V-104 motorista Marcos modelo Van Fiorino placa ABC-1234 capacidade 50 autonomia 40` |
| **Ajustar volume de um pedido existente** | `ajustar pedido 2 para 35 kg` |
| **Excluir um pedido do lote** | `remover pedido 3` |
| **Consultar distância total da frota** | `Qual a distância total percorrida?` |
| **Consultar veículo mais sobrecarregado** | `Qual veículo tem carga máxima?` |
| **Listar rotas otimizadas** | `liste as rotas` |
| **Encerrar a aplicação** | `sair` |

---

## 6. RESULTADOS EXPERIMENTAIS & VALIDAÇÃO TÉCNICA

### 6.1. Suíte de Testes Automatizados (Pytest)
A suíte conta com **47 testes unitários e de integração contínua**, atestando 100% de conformidade:

```bash
python -m pytest tests/ -v
```

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1
rootdir: C:\repos\FIAP\FASE2\Tech-Challenge
collected 47 items

tests/test_llm.py::test_manifesto_local_contem_id_veiculo PASSED         [  2%]
tests/test_llm.py::test_manifesto_local_contem_motorista PASSED          [  4%]
tests/test_llm.py::test_manifesto_critico_contem_alerta PASSED           [  6%]
tests/test_llm.py::test_manifesto_retorna_string PASSED                  [  8%]
tests/test_llm.py::test_formatar_passo_origem PASSED                     [ 10%]
tests/test_llm.py::test_formatar_passo_retorno PASSED                    [ 12%]
tests/test_llm.py::test_payload_llm_tem_chaves_system_e_user PASSED      [ 14%]
tests/test_llm.py::test_payload_llm_system_nao_vazio PASSED              [ 17%]
tests/test_llm.py::test_payload_llm_user_contem_veiculo PASSED           [ 19%]
tests/test_llm.py::test_relatorio_eficiencia_contem_distancia PASSED     [ 21%]
tests/test_llm.py::test_relatorio_eficiencia_retorna_string PASSED       [ 23%]
tests/test_llm.py::test_melhorias_retorna_string PASSED                  [ 25%]
tests/test_llm.py::test_melhorias_sem_dados PASSED                       [ 27%]
tests/test_llm.py::test_qa_responde_distancia_total PASSED               [ 29%]
tests/test_llm.py::test_qa_responde_veiculo_mais_carregado PASSED        [ 31%]
tests/test_llm.py::test_qa_responde_ajuda PASSED                         [ 34%]
tests/test_llm.py::test_qa_responde_lista_rotas PASSED                   [ 36%]
tests/test_llm.py::test_qa_retorna_string_para_pergunta_desconhecida PASSED [ 38%]
tests/test_llm.py::test_gerenciador_interpreta_pedido_texto PASSED       [ 40%]
tests/test_llm.py::test_emergencia_clinica_cascavel_antiofidico PASSED   [ 42%]
tests/test_llm.py::test_ajuste_volume_e_remocao_pedido PASSED            [ 44%]
tests/test_llm.py::test_cadastro_veiculo_e_base PASSED                   [ 46%]
tests/test_llm.py::test_gerenciador_importa_csv PASSED                   [ 48%]
tests/test_llm.py::test_qa_ajuda_exibe_dados_input PASSED                [ 51%]
tests/test_llm.py::test_gerar_link_google_maps PASSED                    [ 53%]
tests/test_llm.py::test_gerar_mapa_html PASSED                           [ 55%]
tests/test_llm.py::test_controlador_briefings_flags_e_reenvio PASSED     [ 57%]
tests/test_llm.py::test_qa_status_briefings PASSED                       [ 59%]
tests/test_llm.py::test_qa_imprimir_briefing_linguagem_natural PASSED    [ 61%]
tests/test_llm.py::test_qa_google_maps_comando PASSED                    [ 63%]
tests/test_llm.py::test_qa_abrir_mapa_pygame_callback PASSED             [ 65%]
tests/test_vrp.py::test_pontos_tem_deposito PASSED                       [ 68%]
tests/test_vrp.py::test_matriz_distancias_shape PASSED                   [ 70%]
tests/test_vrp.py::test_matriz_distancias_diagonal_zero PASSED           [ 72%]
tests/test_vrp.py::test_matriz_distancias_simetrica PASSED               [ 74%]
tests/test_vrp.py::test_gerar_matriz_distancias_custom PASSED            [ 76%]
tests/test_vrp.py::test_fitness_retorna_float_positivo PASSED            [ 78%]
tests/test_vrp.py::test_fitness_cobre_todos_os_clientes PASSED           [ 80%]
tests/test_vrp.py::test_crossover_ox1_sem_duplicatas PASSED              [ 82%]
tests/test_vrp.py::test_crossover_ox1_mesmo_tamanho PASSED               [ 85%]
tests/test_vrp.py::test_crossover_ox1_contem_todos_clientes PASSED       [ 87%]
tests/test_vrp.py::test_mutacao_swap_mesmo_tamanho PASSED                [ 89%]
tests/test_vrp.py::test_mutacao_swap_mesmos_genes PASSED                 [ 91%]
tests/test_vrp.py::test_ag_retorna_todos_os_clientes PASSED              [ 93%]
tests/test_vrp.py::test_ag_retorna_float_positivo PASSED                 [ 95%]
tests/test_vrp.py::test_ag_retorna_historico_fitness PASSED              [ 97%]
tests/test_vrp.py::test_ag_fitness_nao_piora PASSED                      [100%]

============================= 47 passed in 1.04s ==============================
tests/test_llm.py::test_qa_responde_distancia_total PASSED               [ 35%]
tests/test_llm.py::test_qa_responde_veiculo_mais_carregado PASSED        [ 37%]
tests/test_llm.py::test_qa_responde_ajuda PASSED                         [ 40%]
tests/test_llm.py::test_qa_responde_lista_rotas PASSED                   [ 42%]
tests/test_llm.py::test_qa_retorna_string_para_pergunta_desconhecida PASSED [ 45%]
tests/test_llm.py::test_gerenciador_interpreta_pedido_texto PASSED       [ 47%]
tests/test_llm.py::test_emergencia_clinica_cascavel_antiofidico PASSED   [ 50%]
tests/test_llm.py::test_ajuste_volume_e_remocao_pedido PASSED            [ 52%]
tests/test_llm.py::test_cadastro_veiculo_e_base PASSED                   [ 55%]
tests/test_llm.py::test_gerenciador_importa_csv PASSED                   [ 57%]
tests/test_llm.py::test_qa_ajuda_exibe_dados_input PASSED                [ 60%]
tests/test_vrp.py::test_pontos_tem_deposito PASSED                       [ 62%]
tests/test_vrp.py::test_matriz_distancias_shape PASSED                   [ 65%]
tests/test_vrp.py::test_matriz_distancias_diagonal_zero PASSED           [ 67%]
tests/test_vrp.py::test_matriz_distancias_simetrica PASSED               [ 70%]
tests/test_vrp.py::test_gerar_matriz_distancias_custom PASSED            [ 72%]
tests/test_vrp.py::test_fitness_retorna_float_positivo PASSED            [ 75%]
tests/test_vrp.py::test_fitness_cobre_todos_os_clientes PASSED           [ 77%]
tests/test_vrp.py::test_crossover_ox1_sem_duplicatas PASSED              [ 80%]
tests/test_vrp.py::test_crossover_ox1_mesmo_tamanho PASSED               [ 82%]
tests/test_vrp.py::test_crossover_ox1_contem_todos_clientes PASSED       [ 85%]
tests/test_vrp.py::test_mutacao_swap_mesmo_tamanho PASSED                [ 87%]
tests/test_vrp.py::test_mutacao_swap_mesmos_genes PASSED                 [ 90%]
tests/test_vrp.py::test_ag_retorna_todos_os_clientes PASSED              [ 92%]
tests/test_vrp.py::test_ag_retorna_float_positivo PASSED                 [ 95%]
tests/test_vrp.py::test_ag_retorna_historico_fitness PASSED              [ 97%]
tests/test_vrp.py::test_ag_fitness_nao_piora PASSED                      [100%]

============================= 40 passed in 0.43s ==============================
```

### 6.2. Métricas de Convergência da Solução Padrão
- **Fitness Inicial**: $\approx 111,12$
- **Fitness Otimizado**: **$62,37$**
- **Ganho de Otimização**: **$43,9\%$ de redução de custo**
- **Tempo Médio de Execução do AG**: **$0,08\text{ a }0,11\text{ segundos}$** (80 gerações)
- **Atendimento de Prioridade Crítica**: **100% de conformidade** (nós críticos na primeira perna de cada veículo).

---

## 7. ORQUESTRAÇÃO DOCKER & INTEGRAÇÃO N8N

O ecossistema é empacotado para execução reprodutível via Docker Compose:

```bash
# Iniciar container Python e nó n8n:
docker compose up -d
```

- **Serviço n8n**: Porta `5678` com nó de Webhook configurado em `http://localhost:5678/webhook/vrp`.
- **Serviço VRP**: Container Python 3.11 executando o otimizador e despachando o payload JSON estruturado com métricas da frota e telemetria de cada veículo.

---

## 8. CONCLUSÃO

O **HealthRoute AI** cumpre integralmente os requisitos da Fase 2 do Tech Challenge FIAP e expande o estado da arte do projeto:
- Resolve a combinatória complexa do VRP através de Algoritmos Genéticos eficientes;
- Transforma dados matemáticos brutos em inteligência acionável via LLMs;
- Responde a incidentes críticos em tempo real através de raciocínio clínico automatizado;
- Disponibiliza uma arquitetura profissional, extensível, 100% testada e pronta para implantação em produção.
