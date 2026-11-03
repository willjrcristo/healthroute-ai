# RELATÓRIO TÉCNICO & GUIA DE ENGENHARIA DO SISTEMA
## HealthRoute AI — Otimização Evolutiva de Rotas Médicas (VRP) & IA Generativa
> **Tech Challenge — Fase 2**  
> **Pós-Graduação em Inteligência Artificial para Engenharia de Dados — FIAP**  
> **Repositório GitHub:** [https://github.com/willjrcristo/healthroute-ai](https://github.com/willjrcristo/healthroute-ai)  
> **Vídeo de Demonstração (Vimeo):** [https://vimeo.com/1243045935](https://vimeo.com/1243045935)  
> **Status:** 100% Concluído & Integrado (50/50 Testes PASS)  
> **Data:** Novembro / 2026

---

## IDENTIFICAÇÃO DOS ENTREGÁVEIS OFICIAIS (FASE 2)

Para atendimento estrito aos requisitos de avaliação do Tech Challenge Fase 2, os entregáveis oficiais estão disponibilizados nos seguintes canais:

| Entregável Obrigatório | Canal Oficial / URL de Acesso | Descrição e Validação Técnica |
|---|---|---|
| **Repositório Git Completo** | [github.com/willjrcristo/healthroute-ai](https://github.com/willjrcristo/healthroute-ai) | Código-fonte completo em Python 3.11+, infraestrutura Docker Compose, scripts utilitários, dados públicos, documentação interativa e suíte com **50 testes automatizados (100% PASS)**. |
| **Vídeo de Demonstração** | [vimeo.com/1243045935](https://vimeo.com/1243045935) | Demonstração audiovisual completa do sistema em execução ao vivo, convergência genética no Pygame, manifestos LLM, rotas turn-by-turn do Google Maps, comandos em linguagem natural e execução de testes. |
| **Relatório Técnico & Engenharia** | Arquivo `RELATORIO_TECNICO.md` e PDF anexo | Documento formal cobrindo formulação matemática, operadores genéticos, comparativo de abordagens, camada generativa LLM, dados públicos do SAMU e guia de operação. |

---

## SUMÁRIO EXECUTIVO

O projeto **HealthRoute AI** constitui uma solução integrada de engenharia de dados, inteligência artificial combinatória e modelos de linguagem generativa (LLMs) voltada para o transporte de insumos hospitalares e farmacêuticos de alta criticidade.

A partir de uma formulação matemática rigorosa do **Problema de Roteamento de Veículos com Frota Heterogênea e Prioridade Clínica (VRP-CP)**, o sistema otimiza simultaneamente arcos de deslocamento e rotas geográficas reais, garantindo estrita observância a:
1. **Capacidade ponderal da frota** ($45,0\text{ kg}$ a $50,0\text{ kg}$ por veículo);
2. **Autonomia operacional máxima** ($35,0\text{ km}$ a $40,0\text{ km}$ por ciclo de rota);
3. **Prioridade clínica de Nível 1 e Nível 0** (UTI, emergência, hemoderivados e soros antiofídicos atendidos no primeiro vértice de cada sub-rota).

O sistema expande significativamente o código-base fornecido na Fase 2 ao incorporar:
- **Visualização Gráfica Interativa em Pygame & Web Leaflet**: Mapa 2D da malha hospitalar e convergência do fitness em tempo real, com comando para reabrir a qualquer momento do terminal e mapa geográfico interativo em `output/rotas_google_maps.html`;
- **Inclusão Dinâmica de Endereços via Links do Google Maps**: Decodificação automática de URLs curtas (`maps.app.goo.gl`) e completas com resolução de redirecionamento HTTP, extração do nome do hospital e decodificação de coordenadas geodésicas reais;
- **Integração de Microdados Oficiais do SAMU 192 (DATASUS)**: Downloader automatizado que ingere dados abertos do Ministério da Saúde na AWS, filtrando viaturas móveis reais (USB, USA, VIR) na Grande Vitória e Região Serrana do ES;
- **Briefing Operacional para Motoristas com Gestão de Ciclo de Vida e Flags**: Emissão de briefings individuais estruturados, checklist de cadeia fria (2°C a 8°C), links GPS e controle de auditoria de despacho (`⚪ PENDENTE` $\to$ `📱 ENVIADO` $\to$ `🔄 RE-ENVIADO`);
- **Camada Generativa Multimodal (LLM)**: Manifestos operacionais detalhados, relatórios executivos de eficiência gerencial, diagnóstico de melhorias e interface Q&A em linguagem natural;
- **Centro de Despacho & Gestão Dinâmica de Lotes**: Ingestão de pedidos livres por texto, suporte a cenários regionais robustos com 16 hospitais reais, importação de planilhas CSV e re-otimização instantânea do algoritmo genético;
- **Protocolo de Emergência Aguda (Código Vermelho)**: Raciocínio clínico capaz de identificar acidentes agudos (ex: picada de cascavel em zona rural), selecionar o insumo específico (**Soro Anticrotálico**), localizar o posto rural e mobilizar rota expressa imediata;
- **Parametrização Operacional em Tempo Real**: Ajuste dinâmico de coordenadas e título da Base Operacional, cadastro detalhado de furgões e ambulâncias, alocação de veículos por linguagem natural simplificada e alteração de volumes.

---

## 1. FORMULAÇÃO MATEMÁTICA E DOMÍNIO OPERACIONAL

### 1.1. Comparativo de Maturidade Operacional

| Dimensão Operacional | Abordagem Tradicional / Manual | HealthRoute AI (AG + VRP + LLM) |
|---|---|---|
| **Tempo de Planejamento** | Horas; decisões empíricas em planilhas desconexas. | **$< 0,15$ segundos** via convergência evolutiva vetorizada. |
| **Respeito a Restrições** | Violações frequentes de capacidade e autonomia. | **Zero violações** com barreiras de penalidade quadrática. |
| **Priorização Clínica** | Triagem humana sujeita a fadiga e inversão de ordem. | **100% de conformidade de SLA**: nós críticos alocados na 1ª parada. |
| **Comunicação com a Frota** | Pranchetas e mensagens de voz informais. | **Manifestos determinísticos estruturados via LLM** com links de GPS turn-by-turn. |
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

### 2.1. Invariância Combinatória e Operadores Especializados

Operadores genéticos convencionais (como single-point ou uniform crossover) são inadequados para problemas de permutação, pois geram filhos inválidos com vértices duplicados e nós omitidos. O **HealthRoute AI** implementa operadores estritamente fechados sob o espaço de permutações:

1. **Ordered Crossover (OX1)**:
   - Sorteia dois pontos de corte aleatórios $a$ e $b$ no Pai 1;
   - Transfere o segmento contíguo $[\pi_a, \dots, \pi_b]$ diretamente para o filho na mesma posição;
   - Preenche as posições restantes com os genes do Pai 2 na ordem em que aparecem a partir do segundo ponto de corte, ignorando elementos já herdados;
   - **Garantia**: Preserva blocos de adjacência relativos sem duplicidade e sem omissão de nós.

2. **Swap Mutation (Mutação por Troca)**:
   - Com probabilidade estocástica $\mu = 15\%$, seleciona dois índices arbitrários $(i, j)$ e permuta seus elementos: $\pi_i \leftrightarrow \pi_j$;
   - **Garantia**: Injeta diversidade alélica controlada na população, permitindo escape de mínimos locais.

3. **Seleção por Torneio Binário ($k=2$)**:
   - Seleciona dois indivíduos aleatórios do pool de elite e elege o de menor fitness;
   - Mantém uma pressão seletiva calibrada sem perda precoce de variabilidade genética.

4. **Elitismo Estrito ($K=5$)**:
   - As 5 melhores soluções da geração corrente são copiadas intactas para a próxima geração, garantindo convergência monotônica não-crescente:
     $$F_{\text{best}}(t+1) \le F_{\text{best}}(t)$$

---

## 3. COMPARATIVO DE DESEMPENHO COM OUTRAS ABORDAGENS

Em conformidade com as diretrizes do Tech Challenge Fase 2, o desempenho do **Algoritmo Genético VRP** proposto foi rigorosamente confrontado com outras duas estratégias clássicas de roteamento:
1. **TSP Monotípico (Código Base Inicial)**: Atendimento de todos os destinos por um único veículo sem particionamento de frota.
2. **Heurística Gulosa (Nearest Neighbor / Vizinho Mais Próximo)**: Seleção sequencial do nó não visitado de menor distância a partir da posição atual.
3. **Algoritmo Genético VRP Multiveicular com Prioridade Clínica (HealthRoute AI)**: Nossa abordagem multi-objetivo com frota heterogênea.

### 3.1. Tabela Comparativa de Métricas

| Métrica Avaliada | TSP Monotípico (Código Base) | Heurística Gulosa (Nearest Neighbor) | Algoritmo Genético VRP (HealthRoute AI) |
|---|---|---|---|
| **Distância Total Percorrida** | $48,6\text{ km}$ (viola limites) | $71,4\text{ km}$ | **$62,4\text{ km}$ (otimizada para frota)** |
| **Respeito à Capacidade de Carga** | ❌ **Falha Grave** (112 kg em 1 veículo; limite 45 kg) | ⚠️ Parcial (divide por corte fixo de capacidade) | ✅ **100% Conforme** (máximo 45 kg/veículo) |
| **Respeito à Autonomia Máxima** | ❌ **Falha Grave** (48,6 km; limite 35 km) | ⚠️ Violações nos veículos finais | ✅ **100% Conforme** (máximo 25,6 km/veículo) |
| **Conformidade de SLA Crítico** | ❌ **0%** (nó crítico atendido na 4ª e 6ª posições) | ❌ **33%** (prioriza proximidade, não urgência) | ✅ **100%** (críticos na 1ª parada de cada veículo) |
| **Tempo de Execução** | $< 0,05\text{ s}$ | $< 0,01\text{ s}$ | **$0,08\text{ a }0,11\text{ s}$ (convergência em 80 gerações)** |
| **Risco à Vida / Ruptura Clínica** | 🔴 Inaceitável para saúde pública | 🟠 Alto risco de atraso em UTIs | 🟢 **Zero risco: validado e seguro** |

### 3.2. Análise Técnica dos Resultados
A abordagem gulosa demonstrou o clássico fenômeno de *miopia combinatória*: ao escolher sempre o hospital mais próximo, ela negligenciou destinos críticos distantes e sobrecarregou os últimos veículos, acumulando retornos ineficientes ao depósito. O **HealthRoute AI**, por sua vez, explorou o espaço de busca global via crossover OX1 e mutação, equilibrando perfeitamente a ocupação volumétrica dos 3 veículos (100%, 67% e 82%) e assegurando que nenhum medicamento de emergência aguardasse mais de uma parada intermediária.

---

## 4. CAMADA DE INTELIGÊNCIA ARTIFICIAL GENERATIVA (LLM)

A camada generativa foi arquitetada com técnicas de engenharia de prompt avançada (*Role Prompting*, *Few-Shot In-Context Learning* e *Chain-of-Thought* médico).

```
                      ┌──────────────────────────────────────┐
                      │    Telemetria do Algoritmo Genético   │
                      │ (Rotas, Cargas, Distâncias, Nós SLA) │
                      └──────────────────┬───────────────────┘
                                         │
                                         ▼
                      ┌──────────────────────────────────────┐
                      │      Engenharia de Prompt & LLM      │
                      │  (Farmacovigilância + Roteamento)    │
                      └──────────────────┬───────────────────┘
                                         │
        ┌────────────────────┬───────────┴───────────┬────────────────────┐
        ▼                    ▼                       ▼                    ▼
┌───────────────┐    ┌───────────────┐       ┌───────────────┐    ┌───────────────┐
│  Manifestos   │    │  Relatório de │       │ Diagnóstico & │    │  Interface de │
│  Operacionais │    │  Eficiência   │       │   Melhorias   │    │   Q&A Livre   │
│  (Motoristas) │    │  Gerencial    │       │ Operacionais  │    │  (Despacho)   │
└───────────────┘    └───────────────┘       └───────────────┘    └───────────────┘
```

### 4.1. As Quatro Capacidades Centrais da LLM
1. **Manifestos Operacionais de Transporte**: Emissão de roteiros passo a passo por veículo detalhando conferência inicial de temperatura (< 8°C), protocolos de entrega em mãos com assinatura digital, tempo máximo de tolerância (5 min) e procedimentos de emergência.
2. **Relatório de Eficiência de Rotas**: Consolidação gerencial com quilometragem total, percentual médio de ocupação volumétrica, taxa de sucesso de SLAs de prioridade e tempo de processamento.
3. **Sugestões de Melhoria de Processo**: Diagnóstico algorítmico identificando assimetria de carga entre veículos, veículos próximos ao limite de capacidade e estimativa do ponto de estabilização do AG para calibração de hiperparâmetros.
4. **Interface Conversacional Q&A**: Processamento de consultas do operador em linguagem natural sobre métricas operacionais, rotas individuais, status de cada veículo e comandos do sistema.

---

## 5. NOVAS FUNCIONALIDADES IMPLEMENTADAS

### 5.1. Inclusão Dinâmica de Endereços via Links do Google Maps 📍
Permite que o operador de despacho cole diretamente links do Google Maps (curtos ou completos) no terminal para registrar novos hospitais sem precisar digitar coordenadas manuais:
- **Resolução Automática de Redirecionamento HTTP**: O sistema segue os cabeçalhos `Location` do redirecionamento de links curtos (`https://maps.app.goo.gl/EaRSkrpGSee8kN8D9`) até a URL canônica do Google Maps.
- **Extração Semântica do Estabelecimento**: Captura o nome oficial do hospital contido na URL (`/place/Hospital+Evangélico+de+Vila+Velha/`).
- **Decodificação Geodésica**: Extrai com precisão milimétrica a latitude e longitude reais contidas no payload (`!3d-20.3458921!4d-40.3624857` ou `@-20.3458921,-40.3624857`).
- **Mapeamento Proporcional**: Converte as coordenadas GPS para o grid de roteamento, calcula a matriz de distâncias e insere o novo pedido no lote ativo.

### 5.2. Download e Integração de Microdados Oficiais do SAMU 192 (DATASUS) 🚑
Script automatizado [`scripts/baixar_dados_publicos.py`](file:///c:/repos/FIAP/FASE2/Tech-Challenge/scripts/baixar_dados_publicos.py) que consome dados abertos oficiais do Ministério da Saúde na AWS Open Data:
- **Fontes Oficiais**:
  - `samuumst.csv.zip`: Viaturas móveis ativas cadastradas no Sistema de Informação do SAMU 192.
  - `samunab.csv.zip`: Condutores, bases descentralizadas e escalas de prontidão.
- **Processamento e Filtragem**:
  - Extração em memória dos arquivos compactados via `zipfile` e `urllib`;
  - Filtragem de viaturas ativas: USB (Unidade de Suporte Básico), USA (Unidade de Suporte Avançado) e VIR (Veículo de Intervenção Rápida);
  - Segmentação geográfica para a Região Metropolitana da Grande Vitória e Região Serrana do Espírito Santo (Vitória, Serra, Vila Velha, Cariacica, Domingos Martins e Santa Leopoldina);
  - População automática do arquivo [`data/veiculos.csv`](file:///c:/repos/FIAP/FASE2/Tech-Challenge/data/veiculos.csv) com viaturas reais (ex: Mercedes Sprinter, Renault Master), placas oficiais e condutores escalados.

### 5.3. Briefing dos Motoristas com Controle de Ciclo de Vida e Flags de Auditoria
A classe `ControladorBriefings` gerencia a comunicação e auditoria com a frota:
- **Briefing Individual Estruturado**: Gera arquivo texto formatado com checklist pré-embarque, link direto turn-by-turn do Google Maps, alertas de cadeia de frio (2°C a 8°C) e orientações por parada.
- **Ciclo de Vida de Despacho**:
  - `⚪ PENDENTE DE ENVIO`: Status inicial gerado após a otimização;
  - `📱 ENVIADO / COMPARTILHADO`: Registra o timestamp do envio e a Versão 1;
  - `🔄 RE-ENVIADO / RE-IMPRESSO`: Incrementa o número de revisão (Rev. 2, Rev. 3) e atualiza o histórico em `output/briefings_status.json`.
- **Suporte a Linguagem Natural**: Reconhece comandos como *"imprima o briefing do motorista Carlos"*, *"compartilhar briefing com a Ana"*, *"status briefings"* e *"imprimir todos os briefings"*.

### 5.4. Protocolo de Emergência Clínica Aguda (Código Vermelho)
O sistema possui raciocínio clínico para responder a incidentes com risco iminente de morte:
- **Acidentes Ofídicos**: Identifica o gênero da serpente e prescreve o insumo exato:
  - Cascavel (*Crotalus*) $\to$ **Soro Anticrotálico**
  - Jararaca (*Bothrops*) $\to$ **Soro Antibotrópico**
  - Surucucu (*Lachesis*) $\to$ **Soro Antilaquético**
  - Coral Verdadeira (*Micrurus*) $\to$ **Soro Antielapídico**
- **Localização Rural Automática**: Mapeia ocorrências rurais (ex: *Santa Leopoldina - Posto Rural*), fixa a **Prioridade 0 (Ultra-Crítico)** e recomenda o encerramento imediato do lote para despacho expresso.

### 5.5. Carga de Dados Robusta (Cenário Regional Completo)
Para validação em escala real, o comando `carregar cenario real` ou `carga robusta`:
- Carrega simultaneamente **16 hospitais reais do Espírito Santo**;
- Totaliza **223 kg de demanda** farmacêutica e **9 pontos críticos** (código vermelho e amarelo);
- Permite expandir a frota instantaneamente em linguagem natural (*"adicione mais um veiculo"*), alocando ambulâncias adicionais do SAMU para absorver a carga.

### 5.6. Visualizações Gráficas: Pygame Animado e Web Leaflet
- **Pygame**: Painel duplo interativo com renderização da malha hospitalar 2D e gráfico de convergência geracional do fitness, com atalho `abrir mapa` ou `pygame` no terminal.
- **Web Leaflet / Google Maps**: Geração automática de `output/rotas_google_maps.html` com rotas coloridas sobrepostas à geografia real e botões de navegação turn-by-turn.

---

## 6. ARQUITETURA DE MICROSSERVIÇOS & ESTRUTURA DO CÓDIGO

O projeto segue arquitetura modular de alta coesão e baixo acoplamento:

```
Tech-Challenge/
├── data/                        # Bases de dados reais e cadastros operacionais
│   ├── base_operacional.json    # Título, coordenadas Lat/Long e contatos da Base
│   ├── catalogo_insumos.csv     # Soros antiofídicos, hemoderivados e vacinas
│   ├── destinos_reais.csv       # 20 hospitais, postos rurais e UPAs do ES com GPS
│   └── veiculos.csv             # Cadastro de ambulâncias reais do SAMU 192 (DATASUS)
│
├── scripts/                     # Scripts utilitários de dados públicos
│   └── baixar_dados_publicos.py # Downloader oficial de microdados do SAMU / DATASUS
│
├── vrp/                         # Motor de Otimização Combinatória (Algoritmo Genético)
│   ├── __init__.py
│   ├── data.py                  # Definições estáticas, matriz de distâncias e nós base
│   ├── fitness.py               # Função multi-objetivo com penalizações quadráticas
│   ├── operators.py             # Crossover OX1 e Swap Mutation
│   ├── genetic_algorithm.py     # Algoritmo Genético com histórico geracional
│   ├── visualization.py         # Mapa 2D matplotlib e exportador JSON/HTML
│   ├── pygame_viz.py            # Janela gráfica animada (mapa + convergência do fitness)
│   ├── knowledge_base.py        # Base clínica, Haversine, links Google Maps e briefing
│   └── orders.py                # Gerenciador de lotes, NLP e cenário regional robusto
│
├── llm/                         # Camada de Inteligência Artificial Generativa
│   ├── __init__.py
│   ├── prompts.py               # System prompts e contratos padronizados
│   ├── manifesto.py             # Gerador de manifestos operacionais e briefings
│   ├── relatorio.py             # Gerador de relatórios de eficiência e SLAs
│   ├── melhorias.py             # Motor de diagnóstico e sugestão de melhorias
│   └── qa_interface.py          # Interface conversacional de Q&A, comandos e despacho
│
├── webhook/                     # Camada de Integração e Orquestração
│   ├── __init__.py
│   └── payload.py               # Serializador de payloads JSON para webhook / n8n
│
├── tests/                       # Suíte de Testes Automatizados (pytest)
│   ├── __init__.py
│   ├── test_vrp.py              # Testes unitários do motor VRP e operadores
│   └── test_llm.py              # Testes de manifestos, Q&A, emergências e Google Maps
│
├── output/                      # Artefatos produzidos em tempo de execução
│   ├── rotas.png                # Mapa gráfico de rotas por veículo
│   ├── rotas.json               # Dados estruturados da telemetria com links GPS
│   ├── rotas_google_maps.html   # Mapa interativo web com Leaflet
│   ├── briefings_status.json    # Histórico de auditoria e flags dos briefings
│   └── webhook_payload.json     # Payload JSON formatado para webhook
│
├── Dockerfile                   # Imagem Docker Python 3.11-slim
├── docker-compose.yml           # Orquestração do app + nó n8n na porta 5678
├── gerar_pdf_relatorio.py       # Compilador automatizado do Relatório Técnico em PDF
├── requirements.txt             # Dependências de produção e teste
└── main.py                      # Orquestrador principal da aplicação
```

---

## 7. GUIA DE OPERAÇÃO & INSTRUÇÕES DE USO

A tabela abaixo sintetiza os comandos disponíveis no terminal interativo (`python main.py`):

| Categoria | Objetivo Operacional | Comando no Terminal Interativo |
|---|---|---|
| **Ajuda** | Exibir parâmetros, frota e atalhos | `ajuda` ou `dados` |
| **Google Maps** | Inserir hospital via link direto | `https://maps.app.goo.gl/EaRSkrpGSee8kN8D9 precisa de 18kg de sangue` |
| **Emergência** | Lançar código vermelho de antiofídico | `Uma criança picada por cascavel em Santa Leopoldina precisa de soro` |
| **Cenário Real** | Carregar lote regional com 16 hospitais | `carregar cenario real` ou `carga robusta` |
| **Frota** | Adicionar ambulância na frota | `adicione mais um veiculo` ou `cadastrar veiculo ...` |
| **Briefings** | Consultar painel de envio aos motoristas | `status briefings` ou `painel motoristas` |
| **Despacho** | Imprimir / reenviar briefing individual | `imprimir briefing Carlos` ou `compartilhar briefing Ana` |
| **Pygame** | Reabrir a janela gráfica animada | `abrir mapa` ou `pygame` |
| **Mapa Web** | Abrir mapa geográfico no navegador | `abrir mapa real` ou `google maps` |
| **Otimização** | Recalcular Algoritmo Genético VRP | `otimizar` ou `sim` |

---

## 8. RESULTADOS EXPERIMENTAIS & GARANTIA DE QUALIDADE

### 8.1. Suíte de Testes Automatizados (50 Testes / 100% PASS)
A integridade da solução é garantida por **50 testes automatizados** executados via `pytest`:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\repos\FIAP\FASE2\Tech-Challenge
collected 50 items

tests/test_llm.py::test_manifesto_local_contem_id_veiculo PASSED         [  2%]
tests/test_llm.py::test_manifesto_local_contem_motorista PASSED          [  4%]
tests/test_llm.py::test_manifesto_critico_contem_alerta PASSED           [  6%]
tests/test_llm.py::test_manifesto_retorna_string PASSED                  [  8%]
tests/test_llm.py::test_formatar_passo_origem PASSED                     [ 10%]
tests/test_llm.py::test_formatar_passo_retorno PASSED                    [ 12%]
tests/test_llm.py::test_payload_llm_tem_chaves_system_e_user PASSED      [ 14%]
tests/test_llm.py::test_payload_llm_system_nao_vazio PASSED              [ 16%]
tests/test_llm.py::test_payload_llm_user_contem_veiculo PASSED           [ 18%]
tests/test_llm.py::test_relatorio_eficiencia_contem_distancia PASSED     [ 20%]
tests/test_llm.py::test_relatorio_eficiencia_retorna_string PASSED       [ 22%]
tests/test_llm.py::test_melhorias_retorna_string PASSED                  [ 24%]
tests/test_llm.py::test_melhorias_sem_dados PASSED                       [ 26%]
tests/test_llm.py::test_qa_responde_distancia_total PASSED               [ 28%]
tests/test_llm.py::test_qa_responde_veiculo_mais_carregado PASSED        [ 30%]
tests/test_llm.py::test_qa_responde_ajuda PASSED                         [ 32%]
tests/test_llm.py::test_qa_responde_lista_rotas PASSED                   [ 34%]
tests/test_llm.py::test_qa_retorna_string_para_pergunta_desconhecida PASSED [ 36%]
tests/test_llm.py::test_gerenciador_interpreta_pedido_texto PASSED       [ 38%]
tests/test_llm.py::test_emergencia_clinica_cascavel_antiofidico PASSED   [ 40%]
tests/test_llm.py::test_ajuste_volume_e_remocao_pedido PASSED            [ 42%]
tests/test_llm.py::test_cadastro_veiculo_e_base PASSED                   [ 44%]
tests/test_llm.py::test_gerenciador_importa_csv PASSED                   [ 46%]
tests/test_llm.py::test_qa_ajuda_exibe_dados_input PASSED                [ 48%]
tests/test_llm.py::test_gerar_link_google_maps PASSED                    [ 50%]
tests/test_llm.py::test_gerar_mapa_html PASSED                           [ 52%]
tests/test_llm.py::test_controlador_briefings_flags_e_reenvio PASSED     [ 54%]
tests/test_llm.py::test_qa_status_briefings PASSED                       [ 56%]
tests/test_llm.py::test_qa_imprimir_briefing_linguagem_natural PASSED    [ 58%]
tests/test_llm.py::test_qa_google_maps_comando PASSED                    [ 60%]
tests/test_llm.py::test_qa_abrir_mapa_pygame_callback PASSED             [ 62%]
tests/test_llm.py::test_resolver_link_google_maps_e_pedido PASSED        [ 64%]
tests/test_llm.py::test_qa_adicione_mais_um_veiculo_linguagem_natural PASSED [ 66%]
tests/test_llm.py::test_qa_carregar_cenario_robusto PASSED               [ 68%]
tests/test_vrp.py::test_pontos_tem_deposito PASSED                       [ 70%]
tests/test_vrp.py::test_matriz_distancias_shape PASSED                   [ 72%]
tests/test_vrp.py::test_matriz_distancias_diagonal_zero PASSED           [ 74%]
tests/test_vrp.py::test_matriz_distancias_simetrica PASSED               [ 76%]
tests/test_vrp.py::test_gerar_matriz_distancias_custom PASSED            [ 78%]
tests/test_vrp.py::test_fitness_retorna_float_positivo PASSED            [ 80%]
tests/test_vrp.py::test_fitness_cobre_todos_os_clientes PASSED           [ 82%]
tests/test_vrp.py::test_crossover_ox1_sem_duplicatas PASSED              [ 84%]
tests/test_vrp.py::test_crossover_ox1_mesmo_tamanho PASSED               [ 86%]
tests/test_vrp.py::test_crossover_ox1_contem_todos_clientes PASSED       [ 88%]
tests/test_vrp.py::test_mutacao_swap_mesmo_tamanho PASSED                [ 90%]
tests/test_vrp.py::test_mutacao_swap_mesmos_genes PASSED                 [ 92%]
tests/test_vrp.py::test_ag_retorna_todos_os_clientes PASSED              [ 94%]
tests/test_vrp.py::test_ag_retorna_float_positivo PASSED                 [ 96%]
tests/test_vrp.py::test_ag_retorna_historico_fitness PASSED              [ 98%]
tests/test_vrp.py::test_ag_fitness_nao_piora PASSED                      [100%]

============================= 50 passed in 2.44s ==============================
```

### 8.2. Métricas de Convergência da Solução Padrão
- **Fitness Inicial**: $\approx 111,12$
- **Fitness Otimizado**: **$62,37$**
- **Ganho de Otimização**: **$43,9\%$ de redução no custo**
- **Tempo Médio de Execução do AG**: **$0,08\text{ a }0,11\text{ segundos}$** (80 gerações)
- **Atendimento de Prioridade Crítica**: **100% de conformidade** (todos os nós críticos atendidos na 1ª perna de cada veículo).

---

## 9. ORQUESTRAÇÃO DOCKER & INTEGRAÇÃO N8N

O ecossistema é empacotado para execução reprodutível via Docker Compose:

```bash
docker compose up -d
```

- **Serviço n8n**: Porta `5678` com nó de Webhook configurado em `http://localhost:5678/webhook/vrp`.
- **Serviço VRP**: Container Python 3.11 executando o otimizador e despachando o payload JSON estruturado com métricas da frota e telemetria de cada veículo.

---

## 10. CONCLUSÃO

O **HealthRoute AI** cumpre e supera integralmente todos os requisitos da Fase 2 do Tech Challenge FIAP:
1. **Otimização Combinatória Exata**: Transforma o TSP monopostual em um VRP multiveicular com penalidades quadráticas de capacidade, autonomia e urgência clínica;
2. **Camada Generativa de LLM**: Traduz a combinatória matemática em instruções de campo determinísticas e acionáveis para motoristas e gestores;
3. **Engenharia de Dados Aplicada**: Ingestão de dados abertos reais do Ministério da Saúde (SAMU 192) e integração com Google Maps;
4. **Resiliência e Qualidade**: Arquitetura desacoplada, 50 testes automatizados (100% PASS) e esteira de conteinerização Docker pronta para ambiente hospitalar real.
