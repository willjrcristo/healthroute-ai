# HealthRoute AI — Otimização de Rotas Médicas
> **Tech Challenge Fase 2 — FIAP**  
> *Algoritmo Genético VRP (Vehicle Routing Problem) + Integração com IA Generativa (LLM)*  
> 🔗 **Repositório GitHub:** [https://github.com/willjrcristo/healthroute-ai](https://github.com/willjrcristo/healthroute-ai)  
> 🎬 **Vídeo de Demonstração (Vimeo):** [https://vimeo.com/reviews/85747154-309e-481b-bb79-7fad42627151/videos/1243045935](https://vimeo.com/reviews/85747154-309e-481b-bb79-7fad42627151/videos/1243045935)  
> 🧪 **Qualidade:** 50/50 Testes Automatizados (100% PASS) | 🐳 Docker & n8n

---

## 🎯 Visão Geral do Projeto

O **HealthRoute AI** é uma solução completa para otimização de rotas de transporte médico e hospitalar sensível. O sistema resolve o problema de roteamento de veículos (Vehicle Routing Problem - VRP) multiveicular partindo e retornando ao Depósito Central, atendendo nós de entrega hospitalares com restrições simultâneas de:
- **Capacidade máxima**: Configurável por veículo (padrão de referência: 45,0 kg a 50,0 kg)
- **Autonomia máxima**: Configurável por veículo (padrão de referência: 35,0 km a 40,0 km por ciclo de rota)
- **Prioridade de Nível 1 e Nível 0**: Atendimento preferencial imediato a pontos críticos e emergências (UTI, Pronto-Socorro, Vacinas e Soros Antiofídicos)
- **Minimização da Distância Total**: Redução da quilometragem da frota e do tempo de resposta

> 💡 **Nota sobre a Frota:** O cenário canônico e benchmark inicial do desafio utiliza **3 veículos** (V-101, V-102 e V-103) para 6 destinos hospitalares padrão. No entanto, **o sistema não é limitado a 3 veículos**: ele possui arquitetura dinâmica que suporta **adição, remoção e reconfiguração de novos veículos e motoristas na frota em tempo de execução** (via comandos em linguagem natural, interface Q&A e arquivos em `data/veiculos.csv`).

Após a otimização evolutiva, a camada de **IA Generativa / LLM** converte os dados brutos de telemetria em:
1. **Manifestos de Transporte Detalhados** para cada motorista com protocolos de segurança e alertas visuais
2. **Relatório Executivo e de Eficiência de Rotas** com métricas globais e verificação de 100% dos SLAs
3. **Sugestões Inteligentes de Melhoria de Processo** identificando desequilíbrios de carga e gargalos
4. **Interface Interativa de Perguntas e Respostas (Q&A)** em linguagem natural sobre o cenário operacional
5. **Integração de Webhook** com payload JSON padronizado para orquestração no **n8n**

---

## 🏗️ Arquitetura do Repositório

```
Tech-Challenge/
├── .env                         # Configurações de ambiente e chaves de API
├── .env.example                 # Modelo de variáveis de ambiente
├── Dockerfile                   # Imagem containerizada Python 3.11-slim
├── docker-compose.yml           # Orquestração do app Python + instância local do n8n
├── requirements.txt             # Dependências do projeto
├── main.py                      # Orquestrador principal da aplicação
│
├── data/                        # Dados reais e cadastros operacionais
│   ├── base_operacional.json    # Parâmetros e geolocalização da Base / Depósito Central
│   ├── catalogo_insumos.csv     # Catálogo médico com soros antiofídicos e hemoderivados
│   ├── destinos_reais.csv       # Hospitais, UPAs e postos reais com latitude/longitude
│   └── veiculos.csv             # Cadastro dinâmico da frota de veículos e motoristas
│
├── scripts/                     # Scripts utilitários de dados públicos
│   └── baixar_dados_publicos.py # Downloader oficial de microdados do SAMU 192 (DATASUS)
│
├── vrp/                         # Motor de Otimização Evolutiva (VRP)
│   ├── __init__.py
│   ├── data.py                  # Definição dos nós, demandas, prioridades e matriz de distâncias
│   ├── fitness.py               # Função multi-objetivo com penalidades ponderadas
│   ├── operators.py             # Operadores especializados (Crossover OX1 e Mutação Swap)
│   ├── genetic_algorithm.py     # Algoritmo Genético com histórico de convergência
│   ├── visualization.py         # Mapas 2D, links de navegação Google Maps e exportação JSON/HTML
│   ├── pygame_viz.py            # Visualização animada com PyGame (mapa 2D + gráfico de fitness)
│   ├── knowledge_base.py        # Base de conhecimento clínico, cálculo Haversine e triagem
│   └── orders.py                # Gerenciador dinâmico de lotes, frota e pedidos em linguagem natural
│
├── llm/                         # Camada de Inteligência Artificial Generativa
│   ├── __init__.py
│   ├── prompts.py               # Definição do System Prompt e contratos de mensagem
│   ├── manifesto.py             # Manifestos e briefings de condutores com controle de flags
│   ├── relatorio.py             # Gerador do Relatório de Eficiência de Rotas e SLAs
│   ├── melhorias.py             # Motor de diagnóstico e sugestões de melhoria contínua
│   └── qa_interface.py          # Interface Q&A interativa com comandos operacionais
│
├── webhook/                     # Camada de Integração e Orquestração
│   ├── __init__.py
│   └── payload.py               # Gerador de payload padronizado e cliente HTTP para n8n
│
├── output/                      # Artefatos gerados em tempo de execução
│   ├── rotas.png                # Mapa 2D das rotas otimizadas por veículo
│   ├── rotas.json               # Dados estruturados das rotas e URLs de navegação Google Maps
│   ├── rotas_google_maps.html   # Mapa web interativo geográfico com Leaflet
│   ├── briefings_status.json    # Painel com histórico e flags de envio dos motoristas
│   └── webhook_payload.json     # Payload JSON formatado para webhook
│
└── tests/                       # Testes automatizados (pytest)
    ├── __init__.py
    ├── test_vrp.py               # Testes unitários do motor VRP e operadores genéticos
    └── test_llm.py               # Testes de briefings, Google Maps, lotes, flags e Q&A
```

---

## 🚀 Como Executar

### 1. Pré-requisitos
- Python 3.10 ou superior instalado
- Git

### 2. Instalação das Dependências
```bash
pip install -r requirements.txt
```

### 3. Modos de Execução

#### A) Modo Completo com Visualização Gráfica PyGame
Abre a janela gráfica interativa 1280×720 exibindo o mapa 2D dos hospitais à esquerda e a curva de convergência do fitness à direita em tempo real:
```bash
python main.py
```

#### B) Modo Headless (Sem GUI / Para Servidores ou Docker)
Gera os relatórios no terminal, salva o mapa em `output/rotas.png` e os arquivos JSON sem abrir janela gráfica:
```bash
python main.py --no-gui
```

#### C) Modo Automatizado / Pipeline CI/CD (Sem GUI e Sem Loop Interativo de Q&A)
Executa todo o pipeline do início ao fim sem interrupções interativas:
```bash
python main.py --no-gui --no-qa
```

#### D) Parâmetros Adicionais do Algoritmo Genético
Você pode configurar o tamanho da população e o número de gerações:
```bash
python main.py --pop 60 --ger 120 --no-gui
```

---

## 🧪 Testes Automatizados

A suíte de testes cobre 100% dos requisitos funcionais, operadores genéticos (OX1, Swap), restrições de frota, geração de manifestos e a interface de Q&A:

```bash
pytest tests/ -v
```

**Resultado:**
- 50 testes automatizados
- 100% PASS

---

## 🐳 Execução com Docker e Docker Compose

O ambiente inclui Dockerfile e Docker Compose orquestrando a aplicação Python e um serviço do **n8n** na porta `5678`:

```bash
# Iniciar a infraestrutura completa:
docker compose up -d

# Acessar a interface do n8n:
# http://localhost:5678
```

---

## 💬 Interface Interativa de Lotes, Parâmetros e Emergências Clínicas

A interface suporta perguntas analíticas, **parametrização em tempo real da frota e base operacional**, **integração com Google Maps**, **briefings operacionais para motoristas com controle de flags** e **protocolo de emergência médica aguda**:

### 1. Mapas e Visualização Interativa
- `abrir mapa` ou `pygame` : Reabre a visualização gráfica interativa animada no Pygame diretamente do terminal.
- `google maps` ou `mapa real` : Exibe as URLs oficiais de direções turn-by-turn do Google Maps para cada condutor.
- `abrir mapa real` : Abre o mapa interativo geográfico (Leaflet) em `output/rotas_google_maps.html` no navegador.

### 2. Briefings dos Motoristas & Controle de Flags de Despacho
- `status briefings` ou `painel motoristas` : Exibe tabela de controle com o status de envio de cada condutor (`⚪ PENDENTE DE ENVIO`, `📱 ENVIADO`, `🔄 RE-ENVIADO`), timestamps e revisões.
- `imprimir briefing <motorista>` : Exibe no terminal e salva o briefing individual em `output/briefing_<veiculo>_<motorista>.txt`.
- `compartilhar briefing <motorista>` : Compartilha/envia o briefing e atualiza a flag de rastreamento.
- **Suporte a Linguagem Natural**:
  - *"Imprima o briefing do motorista Carlos"*
  - *"Compartilhar a rota com a motorista Ana"*
  - *"Pode reimprimir o briefing do Roberto?"*
  - *"imprimir todos os briefings"* (despacho geral da frota)

### 3. Ajuste Dinâmico de Parâmetros Operacionais
- **Base Operacional**:
  `ajustar base Centro Logístico Metropolitano lat -20.31 long -40.30`
- **Cadastrar / Adicionar Veículo**:
  - Comando explícito: `cadastrar veiculo V-104 motorista Marcos modelo Van Fiorino placa ABC-1234 capacidade 50 autonomia 40`
  - Linguagem natural simplificada: `adicione mais um veiculo`, `adicionar ambulancia` (o sistema aloca automaticamente a próxima viatura disponível do SAMU 192 com condutor escalado, placa e especificações técnicas).
- **Remover Veículo da Frota**:
  `remover veiculo V-103`
- **Ajustar Volume de um Insumo já Solicitado**:
  `ajustar pedido 2 para 35 kg`
- **Remover Destino/Pedido do Lote**:
  `remover pedido 3`

### 4. Inclusão de Novos Endereços via Links do Google Maps 📍
Você pode colar links diretos do Google Maps no terminal do assistente para adicionar hospitais e pontos de atendimento sem precisar digitar coordenadas manuais:

- **Formatos suportados**:
  - Links curtos gerados no app mobile ou navegador: `https://maps.app.goo.gl/EaRSkrpGSee8kN8D9`
  - Links completos: `https://www.google.com/maps/place/Hospital+Evangélico+de+Vila+Velha/@-20.3458921,-40.3624857,17z/...`
- **Como o sistema processa**:
  1. Efetua a resolução automática de redirecionamento HTTP da URL.
  2. Extrai o nome oficial do hospital/estabelecimento diretamente do endpoint.
  3. Decodifica as coordenadas geodésicas reais (latitude e longitude) presentes no payload (`!3d...!4d...` ou `@lat,lon`).
  4. Mapeia a geolocalização no grid regional de roteamento e insere no lote ativo de entregas.
- **Exemplos de Prompts**:
  > *"O Hospital precisa de entrega urgente: https://maps.app.goo.gl/EaRSkrpGSee8kN8D9 demanda 18kg de bolsas de sangue"*  
  > *"Adicione https://maps.app.goo.gl/EaRSkrpGSee8kN8D9 com 12kg de vacinas"*  
  > *"https://www.google.com/maps/place/Hospital+Estadual+Dr.+Jayme+Santos+Neves/@-20.170669,-40.2443048,17z precisa de 25kg de soro"*

### 5. Download e Sincronização do Dataset Oficial do SAMU 192 (DATASUS) 🚑
O projeto disponibiliza um script automatizado para baixar e integrar microdados oficiais abertos do Ministério da Saúde / DATASUS:

```bash
python scripts/baixar_dados_publicos.py
```

**Fontes e Funcionamento do Script**:
- **Origem dos Dados**: Bucket público AWS Open Data do Departamento de Informática do SUS (DATASUS):
  - `samuumst.csv.zip`: Unidades Móveis e Viaturas em operação.
  - `samunab.csv.zip`: Condutores, médicos, enfermeiros e bases do SAMU.
- **Processamento Automatizado**:
  1. Efetua o download e descompactação dos arquivos em memória (`zipfile`).
  2. Filtra as Unidades Móveis ativas do SAMU 192 (Unidades de Suporte Básico - USB, Unidades de Suporte Avançado - USA e Veículos de Intervenção Rápida - VIR).
  3. Isola os municípios da Grande Vitória e Região Serrana do Espírito Santo (Vitória, Vila Velha, Serra, Cariacica, Domingos Martins e Santa Leopoldina).
  4. Gera o arquivo [`data/veiculos.csv`](file:///c:/repos/FIAP/FASE2/Tech-Challenge/data/veiculos.csv) com identificadores oficiais, modelos (ex: Mercedes-Benz Sprinter, Renault Master), placas, condutores escalados e capacidades de carga homologadas.

### 6. Carga de Dados Robusta (Cenário Regional Completo)
Para simular um cenário de alta complexidade com múltiplos veículos e 16 destinos reais simultâneos no Espírito Santo:
- No prompt interativo, digite:  
  `carregar cenario real` ou `carga robusta`
- O sistema carrega instantaneamente 16 hospitais, UPAs e postos rurais (Vitória, Serra, Vila Velha, Cariacica, Domingos Martins e Santa Leopoldina), totalizando 223 kg de demanda e 9 pontos de alta criticidade (código vermelho/amarelo), pronto para reotimização com `otimizar`.

### 7. Catálogos Reais em CSV (`data/`)
O projeto agora integra bases de dados reais:
- [`data/destinos_reais.csv`](file:///c:/repos/FIAP/FASE2/Tech-Challenge/data/destinos_reais.csv): 20 hospitais gerais, infantis, UPAs 24h, postos rurais (ex: Santa Leopoldina, Domingos Martins) e maternidades com coordenadas geográficas e contatos.
- [`data/catalogo_insumos.csv`](file:///c:/repos/FIAP/FASE2/Tech-Challenge/data/catalogo_insumos.csv): Catálogo com **Soros Antiofídicos** (Anticrotálico para cascavel, Antibotrópico para jararaca, Antilaquético, Antielapídico), **Hemocomponentes** (Bolsas de Sangue O- Universal), vacinas termossensíveis, etc.
- [`data/veiculos.csv`](file:///c:/repos/FIAP/FASE2/Tech-Challenge/data/veiculos.csv): Cadastro detalhado de furgões/ambulâncias com modelo, placa, hodômetro, consumo (km/l), capacidade e autonomia originadas dos dados do SAMU 192.

### 8. Protocolo Inteligente de Emergência Médica Aguda
Se o usuário reportar uma emergência no prompt, por exemplo:
> *"Uma criança foi picada por uma cobra cascavel em uma zona rural de Santa Leopoldina, ela precisa de uma dose de antiofídico"*

O sistema automaticamente:
1. Reconhece o acidente ofídico e seleciona o **Soro Anticrotálico (Cascavel)**.
2. Identifica o município (**Santa Leopoldina - Posto Rural**) e calcula a geolocalização.
3. Classifica com **Código Vermelho (Prioridade 0 / Ultra-Crítico)**.
4. **Recomenda o despacho imediato da rota prioritária** para salvar vidas!

### 9. Gestão de Lotes e Importação CSV
- `ajuda` ou `dados` : Exibe a tabela completa de parâmetros, frota, pedidos e atalhos.
- `catalogo insumos`  : Exibe a lista completa de soros antiofídicos e remédios.
- `destinos reais`    : Exibe a lista de hospitais e postos reais cadastrados.
- `ver lote`          : Exibe todos os pedidos acumulados no lote ativo.
- `novo lote`         : Abre um lote limpo.
- `carregar cenario real` : Carrega o lote regional robusto com 16 hospitais reais.
- `importar pedidos_exemplo.csv` : Carrega pedidos de uma planilha CSV.
- `otimizar` ou `sim` : **Recalcula instantaneamente o Algoritmo Genético VRP**, atualiza mapa, exporta JSON e gera novos manifestos e relatórios de eficiência!


