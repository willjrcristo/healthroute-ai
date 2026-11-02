"""
tests/test_llm.py — Testes automatizados dos módulos LLM.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest

from llm.manifesto import gerar_manifesto_local, formatar_passo, construir_dados_veiculo
from llm.prompts import construir_payload_llm, PROMPT_SISTEMA
from llm.relatorio import gerar_relatorio_eficiencia
from llm.melhorias import sugerir_melhorias_processo
from llm.qa_interface import responder_pergunta


# ─── Fixtures ─────────────────────────────────────────────────────────────── #

@pytest.fixture
def dados_veiculo_simples():
    return {
        "veiculo_id": "V-101",
        "motorista": "Carlos Silva",
        "distancia_total_km": 25.0,
        "carga_total_kg": 37.0,
        "destinos": [
            {"nome": "Depósito Central", "tipo": "Origem",  "critico": False, "demanda_kg": 0},
            {"nome": "Hospital A (UTI)", "tipo": "Entrega", "critico": True,  "demanda_kg": 15, "item": "Anestésicos Críticos"},
            {"nome": "Posto B",          "tipo": "Entrega", "critico": False, "demanda_kg": 22, "item": "Medicamentos Gerais"},
            {"nome": "Depósito Central", "tipo": "Retorno", "critico": False, "demanda_kg": 0},
        ],
    }


@pytest.fixture
def rotas_detalhadas():
    return [
        {
            "veiculo": 1, "identificador": "V-101 (Carlos Silva)", "motorista": "Carlos Silva",
            "caminho": [0, 1, 2, 0], "pontos_nomes": ["Depósito Central", "Hospital A (UTI)", "Posto B", "Depósito Central"],
            "distancia_km": 25.0, "carga_kg": 35.0, "ocupacao_pct": 77.8,
            "destinos": [
                {"nome": "Hospital A (UTI)", "tipo": "Entrega", "critico": True},
            ],
        },
        {
            "veiculo": 2, "identificador": "V-102 (Ana Souza)", "motorista": "Ana Souza",
            "caminho": [0, 3, 4, 0], "pontos_nomes": ["Depósito Central", "Hospital C (Emergência)", "Posto D", "Depósito Central"],
            "distancia_km": 21.0, "carga_kg": 35.0, "ocupacao_pct": 77.8,
            "destinos": [
                {"nome": "Hospital C", "tipo": "Entrega", "critico": True},
            ],
        },
        {
            "veiculo": 3, "identificador": "V-103 (Roberto Lima)", "motorista": "Roberto Lima",
            "caminho": [0, 5, 6, 0], "pontos_nomes": ["Depósito Central", "Hospital E", "Clínica F", "Depósito Central"],
            "distancia_km": 15.0, "carga_kg": 42.0, "ocupacao_pct": 93.3,
            "destinos": [],
        },
    ]


@pytest.fixture
def contexto_qa(rotas_detalhadas):
    return {
        "rotas": rotas_detalhadas,
        "fitness_final": 95.5,
        "total_geracoes": 80,
    }


# ─── Testes de Manifesto ─────────────────────────────────────────────────── #

def test_manifesto_local_contem_id_veiculo(dados_veiculo_simples):
    """O manifesto deve conter o ID do veículo."""
    manifesto = gerar_manifesto_local(dados_veiculo_simples)
    assert "V-101" in manifesto


def test_manifesto_local_contem_motorista(dados_veiculo_simples):
    """O manifesto deve mencionar o nome do motorista."""
    manifesto = gerar_manifesto_local(dados_veiculo_simples)
    assert "Carlos Silva" in manifesto


def test_manifesto_critico_contem_alerta(dados_veiculo_simples):
    """Destino crítico deve gerar alerta de prioridade no manifesto."""
    manifesto = gerar_manifesto_local(dados_veiculo_simples)
    assert "PRIORIDADE CRÍTICA" in manifesto or "ALERTA" in manifesto


def test_manifesto_retorna_string(dados_veiculo_simples):
    """gerar_manifesto_local deve retornar uma string não vazia."""
    resultado = gerar_manifesto_local(dados_veiculo_simples)
    assert isinstance(resultado, str)
    assert len(resultado) > 50


def test_formatar_passo_origem():
    """formatar_passo para tipo Origem deve mencionar 'Partida'."""
    destino = {"nome": "Depósito Central", "tipo": "Origem", "critico": False, "demanda_kg": 0}
    resultado = formatar_passo(1, destino, 37.0)
    assert "Partida" in resultado or "partida" in resultado.lower()


def test_formatar_passo_retorno():
    """formatar_passo para tipo Retorno deve mencionar 'Retorno'."""
    destino = {"nome": "Depósito Central", "tipo": "Retorno", "critico": False, "demanda_kg": 0}
    resultado = formatar_passo(4, destino, 37.0)
    assert "Retorno" in resultado


# ─── Testes de Prompts LLM ───────────────────────────────────────────────── #

def test_payload_llm_tem_chaves_system_e_user(dados_veiculo_simples):
    """construir_payload_llm deve retornar dict com 'system' e 'user'."""
    payload = construir_payload_llm(dados_veiculo_simples)
    assert "system" in payload
    assert "user" in payload


def test_payload_llm_system_nao_vazio():
    """O prompt de sistema não deve estar vazio."""
    assert len(PROMPT_SISTEMA) > 20


def test_payload_llm_user_contem_veiculo(dados_veiculo_simples):
    """O prompt do usuário deve mencionar o ID do veículo."""
    payload = construir_payload_llm(dados_veiculo_simples)
    assert "V-101" in payload["user"]


# ─── Testes de Relatório ─────────────────────────────────────────────────── #

def test_relatorio_eficiencia_contem_distancia(rotas_detalhadas):
    """O relatório deve mencionar a distância total."""
    historico = [500.0, 300.0, 200.0, 150.0, 120.0]
    relatorio = gerar_relatorio_eficiencia(rotas_detalhadas, historico)
    assert "61.0" in relatorio or "km" in relatorio


def test_relatorio_eficiencia_retorna_string(rotas_detalhadas):
    """gerar_relatorio_eficiencia deve retornar string."""
    historico = [500.0, 200.0, 100.0]
    resultado = gerar_relatorio_eficiencia(rotas_detalhadas, historico)
    assert isinstance(resultado, str)
    assert len(resultado) > 100


# ─── Testes de Melhorias ─────────────────────────────────────────────────── #

def test_melhorias_retorna_string(rotas_detalhadas):
    """sugerir_melhorias_processo deve retornar string."""
    historico = [500.0, 300.0, 200.0, 150.0, 120.0]
    resultado = sugerir_melhorias_processo(rotas_detalhadas, historico)
    assert isinstance(resultado, str)
    assert len(resultado) > 50


def test_melhorias_sem_dados():
    """Com lista vazia, deve retornar mensagem de aviso."""
    resultado = sugerir_melhorias_processo([], [])
    assert "Sem dados" in resultado or len(resultado) > 0


# ─── Testes de Q&A ───────────────────────────────────────────────────────── #

def test_qa_responde_distancia_total(contexto_qa):
    """Q&A deve responder perguntas sobre distância total."""
    resp = responder_pergunta("Qual a distância total percorrida?", contexto_qa)
    assert "61" in resp or "km" in resp.lower()


def test_qa_responde_veiculo_mais_carregado(contexto_qa):
    """Q&A deve identificar o veículo com mais carga."""
    resp = responder_pergunta("Qual veículo tem mais carga?", contexto_qa)
    assert "V-103" in resp or "Roberto" in resp or "42" in resp


def test_qa_responde_ajuda(contexto_qa):
    """Q&A deve responder ao comando de ajuda."""
    resp = responder_pergunta("ajuda", contexto_qa)
    assert "distância" in resp.lower() or "rota" in resp.lower()


def test_qa_responde_lista_rotas(contexto_qa):
    """Q&A deve listar as rotas quando solicitado."""
    resp = responder_pergunta("Liste as rotas", contexto_qa)
    assert "V-101" in resp or "V-102" in resp or "V-103" in resp


def test_qa_retorna_string_para_pergunta_desconhecida(contexto_qa):
    """Q&A deve retornar uma string mesmo para perguntas não reconhecidas."""
    resp = responder_pergunta("o que é fotossíntese?", contexto_qa)
    assert isinstance(resp, str)
    assert len(resp) > 5


# ─── Testes do Gerenciador de Lotes e Pedidos ─────────────────────────────── #

def test_gerenciador_interpreta_pedido_texto():
    """Deve interpretar pedido em linguagem natural e extrair demanda e hospital."""
    from vrp.orders import GerenciadorLotes
    gl = GerenciadorLotes()
    pedido, info = gl.interpretar_pedido_texto("O Hospital Santa Casa está precisando de 18kg de bolsas de sangue (crítico)")
    assert pedido is not None
    assert "Santa Casa" in pedido.hospital
    assert pedido.demanda_kg == 18.0
    assert pedido.critico is True
    assert "Sangue" in pedido.insumo or "Bolsas" in pedido.insumo


def test_emergencia_clinica_cascavel_antiofidico(contexto_qa):
    """Deve detectar picada de cascavel em Santa Leopoldina e sugerir anticrotálico e despacho imediato."""
    from vrp.orders import GerenciadorLotes
    gl = GerenciadorLotes()
    resp = responder_pergunta(
        "Uma criança foi picada por uma cobra cascavel em uma zona rural de Santa Leopoldina, ela precisa de uma dose de antiofídico",
        contexto_qa,
        gerenciador_lotes=gl,
    )
    assert "ALERTA DE EMERGÊNCIA MÉDICA" in resp
    assert "Anticrotálico" in resp
    assert "Santa Leopoldina" in resp
    assert "Prioridade 0" in resp or "Ultra-Crítico" in resp


def test_ajuste_volume_e_remocao_pedido(contexto_qa):
    """Deve permitir ajustar volume e remover pedidos no lote."""
    from vrp.orders import GerenciadorLotes
    gl = GerenciadorLotes()
    # Ajuste de volume
    resp_aj = responder_pergunta("ajustar pedido 1 para 32 kg", contexto_qa, gerenciador_lotes=gl)
    assert "32.0 kg" in resp_aj
    assert gl.pedidos[0].demanda_kg == 32.0

    # Remoção de pedido
    qtd_antes = len(gl.pedidos)
    resp_rem = responder_pergunta("remover pedido 2", contexto_qa, gerenciador_lotes=gl)
    assert "removido" in resp_rem.lower()
    assert len(gl.pedidos) == qtd_antes - 1


def test_cadastro_veiculo_e_base(contexto_qa):
    """Deve cadastrar veículo e ajustar parâmetros da base operacional."""
    from vrp.orders import GerenciadorLotes
    gl = GerenciadorLotes()
    resp_v = responder_pergunta(
        "cadastrar veiculo V-109 motorista Fabiano modelo Furgoneta Master placa XYZ-9988 capacidade 55 autonomia 42",
        contexto_qa,
        gerenciador_lotes=gl,
    )
    assert "CADASTRADO" in resp_v
    assert "XYZ-9988" in resp_v

    resp_b = responder_pergunta(
        "ajustar base Centro Logistico Metropolitano lat -20.25 long -40.35",
        contexto_qa,
        gerenciador_lotes=gl,
    )
    assert "ATUALIZADA" in resp_b

    # Limpeza / restauração
    gl.remover_veiculo("V-109")
    gl.ajustar_base_operacional("Centro de Distribuicao e Logistica Medica (Deposito Central)", -20.3167, -40.3083)



def test_gerenciador_importa_csv(tmp_path):
    """Deve importar pedidos a partir de arquivo CSV."""
    from vrp.orders import GerenciadorLotes
    csv_file = tmp_path / "pedidos_teste.csv"
    csv_file.write_text("hospital,insumo,demanda_kg,critico,pos_x,pos_y\nHospital Teste,Vacinas,12,true,3.0,4.0\n", encoding="utf-8")
    gl = GerenciadorLotes()
    qtd_antes = len(gl.pedidos)
    inseridos = gl.importar_csv(str(csv_file))
    assert inseridos == 1
    assert len(gl.pedidos) == qtd_antes + 1
    assert gl.pedidos[-1].hospital == "Hospital Teste"


def test_qa_ajuda_exibe_dados_input(contexto_qa):
    """O comando 'ajuda' deve exibir a tabela de dados de input, comandos de lote, mapas e briefings."""
    from vrp.orders import GerenciadorLotes
    gl = GerenciadorLotes()
    resp = responder_pergunta("ajuda", contexto_qa, gerenciador_lotes=gl)
    assert "DADOS DE INPUT" in resp
    assert "Base Operacional" in resp
    assert "FROTA DE VEÍCULOS" in resp
    assert "GESTÃO DE LOTES" in resp
    assert "abrir mapa" in resp or "pygame" in resp
    assert "google maps" in resp or "mapa real" in resp
    assert "status briefings" in resp
    assert "imprimir briefing" in resp


def test_gerar_link_google_maps():
    """Gera URL válida de navegação Google Maps turn-by-turn."""
    from vrp.visualization import gerar_link_google_maps
    caminho = [0, 3, 2, 0]
    url = gerar_link_google_maps(caminho)
    assert "https://www.google.com/maps/dir/" in url
    assert "origin=" in url
    assert "destination=" in url
    assert "waypoints=" in url
    assert "travelmode=driving" in url


def test_gerar_mapa_html(tmp_path, rotas_detalhadas):
    """Gera mapa interativo HTML com Leaflet e links do Google Maps."""
    from vrp.visualization import gerar_mapa_html
    caminho_teste = str(tmp_path / "mapa_teste.html")
    resultado = gerar_mapa_html(rotas_detalhadas, caminho_saida=caminho_teste)
    assert os.path.exists(resultado)
    with open(resultado, "r", encoding="utf-8") as f:
        html = f.read()
    assert "leaflet" in html.lower()
    assert "HealthRoute AI" in html
    assert "Google Maps" in html
    assert "Carlos Silva" in html


def test_controlador_briefings_flags_e_reenvio(rotas_detalhadas):
    """Testa o ciclo de vida do briefing: PENDENTE -> ENVIADO (v1) -> RE-ENVIADO (v2)."""
    from llm.manifesto import ControladorBriefings
    ctrl = ControladorBriefings()
    ctrl.atualizar_frota(rotas_detalhadas)

    # Inicialmente deve estar PENDENTE
    painel_inicial = ctrl.gerar_painel_status(rotas_detalhadas)
    assert "PENDENTE" in painel_inicial
    assert ctrl.registros["V-101"].status == "PENDENTE"
    assert ctrl.registros["V-101"].versao == 0

    # Primeiro Envio (Carlos)
    texto, msg, ok = ctrl.compartilhar_briefing("Carlos", rotas_detalhadas)
    assert ok is True
    assert "Carlos Silva" in texto
    assert "ENVIADO" in msg
    assert ctrl.registros["V-101"].status == "ENVIADO"
    assert ctrl.registros["V-101"].versao == 1
    assert os.path.exists(ctrl.registros["V-101"].caminho_arquivo)

    # Segundo Envio / Re-impressão (Carlos)
    texto2, msg2, ok2 = ctrl.compartilhar_briefing("Carlos Silva", rotas_detalhadas)
    assert ok2 is True
    assert "RE-ENVIADO" in msg2
    assert ctrl.registros["V-101"].status == "RE-ENVIADO"
    assert ctrl.registros["V-101"].versao == 2


def test_qa_status_briefings(contexto_qa):
    """Q&A deve exibir o painel de controle com status dos motoristas."""
    resp = responder_pergunta("status briefings", contexto_qa)
    assert "PAINEL DE CONTROLE DE BRIEFINGS" in resp
    assert "Carlos Silva" in resp
    assert "Ana Souza" in resp
    assert "Roberto Lima" in resp


def test_qa_imprimir_briefing_linguagem_natural(contexto_qa):
    """Q&A deve processar pedidos de briefing em linguagem natural."""
    # Carlos
    resp = responder_pergunta("Imprima o briefing do motorista Carlos", contexto_qa)
    assert "Carlos Silva" in resp
    assert "BRIEFING OPERACIONAL" in resp
    assert "ENVIADO" in resp or "RE-ENVIADO" in resp

    # Ana
    resp_ana = responder_pergunta("compartilhar briefing com motorista Ana", contexto_qa)
    assert "Ana Souza" in resp_ana
    assert "processado com sucesso" in resp_ana

    # Reenvio Carlos
    resp_reenvio = responder_pergunta("Pode reimprimir o briefing do Carlos Silva?", contexto_qa)
    assert "Carlos Silva" in resp_reenvio
    assert "RE-ENVIADO" in resp_reenvio or "RE-IMPRESSO" in resp_reenvio


def test_qa_google_maps_comando(contexto_qa):
    """Comando 'google maps' no Q&A deve exibir os links de GPS."""
    resp = responder_pergunta("google maps", contexto_qa)
    assert "INTEGRAÇÃO COM GOOGLE MAPS" in resp
    assert "https://www.google.com/maps/dir/" in resp


def test_qa_abrir_mapa_pygame_callback(contexto_qa):
    """Comando 'abrir mapa' deve disparar o callback do visualizador Pygame."""
    chamado = []
    contexto_qa["callback_pygame"] = lambda: chamado.append(True)

    resp = responder_pergunta("abrir mapa", contexto_qa)
    assert len(chamado) == 1
    assert "PyGame" in resp


def test_resolver_link_google_maps_e_pedido():
    """Deve interpretar link encurtado do Google Maps e catalogar como ponto de entrega."""
    from vrp.orders import GerenciadorLotes
    gl = GerenciadorLotes()
    link = "https://maps.app.goo.gl/EaRSkrpGSee8kN8D9 precisa de 18kg de bolsas de sangue (urgente)"
    pedido, emergencia = gl.interpretar_pedido_texto(link)

    assert pedido is not None
    assert "Hospital Evangélico" in pedido.hospital
    assert pedido.demanda_kg == 18.0
    assert pedido.critico is True
    assert pedido.latitude is not None and abs(pedido.latitude - (-20.3458)) < 0.05
    assert pedido.longitude is not None and abs(pedido.longitude - (-40.3434)) < 0.05


def test_qa_adicione_mais_um_veiculo_linguagem_natural(contexto_qa):
    """Deve aceitar comando em linguagem natural 'adicione mais um veiculo' e criar veículo SAMU."""
    from vrp.orders import GerenciadorLotes
    gl = GerenciadorLotes()
    qtd_antes = len(gl.kb.veiculos)
    resp = responder_pergunta("adicione mais um veiculo", contexto_qa, gerenciador_lotes=gl)

    assert "NOVO VEÍCULO ADICIONADO" in resp
    assert len(gl.kb.veiculos) == qtd_antes + 1
    assert "SAMU" in resp


def test_qa_carregar_cenario_robusto(contexto_qa):
    """Deve carregar o cenário regional robusto com múltiplos hospitais reais do ES."""
    from vrp.orders import GerenciadorLotes
    gl = GerenciadorLotes()
    resp = responder_pergunta("carregar cenario real", contexto_qa, gerenciador_lotes=gl)

    assert "CENÁRIO ROBUSTO METROPOLITANO" in resp
    assert len(gl.pedidos) >= 15
    assert any("Hospital Evangélico" in p.hospital for p in gl.pedidos)
    assert any("Santa Leopoldina" in p.hospital for p in gl.pedidos)


