"""
main.py — HealthRoute AI: Orquestrador Principal
Tech Challenge Fase 2 — FIAP

Execução:
    python main.py           # Com visualização PyGame
    python main.py --no-gui  # Headless (CI/Docker)
    python main.py --no-qa   # Pula interface Q&A interativa
"""
import argparse
import os
import sys
import time

# Força codificação UTF-8 no stdout/stderr no Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import numpy as np

# Carrega variáveis de ambiente (.env)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ==============================================================================
# MÓDULOS DO PROJETO
# ==============================================================================

from vrp.data import (
    PONTOS,
    NUM_VEICULOS,
    CAPACIDADE_VEICULO,
    AUTONOMIA_VEICULO,
    MATRIZ_DISTANCIAS,
    ITENS_ENTREGA,
    gerar_matriz_distancias,
)
from vrp.genetic_algorithm import executar_ag
from vrp.visualization import (
    plotar_rotas,
    exportar_json,
    gerar_relatorio_executivo,
    gerar_link_google_maps,
    gerar_mapa_html,
)
from vrp.orders import GerenciadorLotes

from llm.manifesto import gerar_manifesto_local, construir_dados_veiculo
from llm.relatorio import gerar_relatorio_eficiencia
from llm.melhorias import sugerir_melhorias_processo
from llm.qa_interface import iniciar_qa_interativo

from webhook.payload import gerar_payload_n8n, disparar_webhook


# ==============================================================================
# FUNÇÕES AUXILIARES
# ==============================================================================

def construir_rotas_detalhadas(melhor_rota, custo, pontos_ref=None, itens_ref=None):
    """Monta a lista de dicts com detalhes por veículo para os módulos llm/ e webhook/."""
    pts = pontos_ref or PONTOS
    itens = itens_ref or ITENS_ENTREGA
    matriz = gerar_matriz_distancias(pts)

    entregas = [p for p in melhor_rota if p != 0]
    partes = np.array_split(entregas, NUM_VEICULOS)

    rotas_detalhadas = []
    for i, parte in enumerate(partes, start=1):
        caminho = [0] + list(parte) + [0]
        dist = sum(matriz[caminho[j]][caminho[j + 1]] for j in range(len(caminho) - 1))
        carga = sum(pts[p]["demanda"] for p in caminho if p != 0)
        dados_v = construir_dados_veiculo(i, caminho, pts, dist)

        # Se houver insumo customizado nos itens_ref
        for dest in dados_v["destinos"]:
            # Procura id do ponto correspondente ao nome
            for pid, dados_p in pts.items():
                if dados_p["nome"] == dest["nome"] and pid in itens:
                    dest["item"] = itens[pid]

        dados_v.update({
            "veiculo": i,
            "identificador": f"{dados_v['veiculo_id']} ({dados_v['motorista']})",
            "caminho": caminho,
            "pontos_nomes": [pts[p]["nome"] for p in caminho],
            "distancia_km": round(dist, 2),
            "carga_kg": round(carga, 1),
            "ocupacao_pct": round(carga / CAPACIDADE_VEICULO * 100, 1),
            "google_maps_url": gerar_link_google_maps(caminho, pts),
        })
        rotas_detalhadas.append(dados_v)
    return rotas_detalhadas


def imprimir_banner():
    print("\n" + "=" * 65)
    print("  HealthRoute AI — Otimização de Rotas Médicas")
    print("  Tech Challenge Fase 2 | FIAP | Algoritmo Genético VRP")
    print("=" * 65 + "\n")


def imprimir_rotas(melhor_rota, custo, pontos_ref=None):
    """Exibe as sub-rotas por veículo no terminal."""
    pts = pontos_ref or PONTOS
    entregas = [p for p in melhor_rota if p != 0]
    rotas = np.array_split(entregas, NUM_VEICULOS)
    print(f"🏆 Melhor sequência : {melhor_rota}")
    print(f"📊 Custo fitness    : {custo:.2f}\n")
    nomes_veiculos = ["V-101 (Carlos Silva)", "V-102 (Ana Souza)", "V-103 (Roberto Lima)"]
    for i, (rota, nome) in enumerate(zip(rotas, nomes_veiculos), start=1):
        caminho = [0] + rota.tolist() + [0]
        nomes = " → ".join(pts[p]["nome"] for p in caminho)
        print(f"  Veículo {i} [{nome}]: {nomes}")
    print()


def executar_pipeline_lote(novos_pontos, novos_itens=None, pop=40, ger=80):
    """Executa a otimização de rotas e geração de artefatos para um lote de pontos."""
    imprimir_banner()
    print(f"🧬 [1/6] Executando Algoritmo Genético para o lote ({len(novos_pontos)-1} destinos)...")
    t_inicio = time.time()

    # O AG usa PONTOS global ou adaptado
    from vrp import data as data_module
    from vrp import fitness as fitness_module
    old_pontos = data_module.PONTOS
    old_matriz = data_module.MATRIZ_DISTANCIAS
    try:
        data_module.PONTOS = novos_pontos
        data_module.MATRIZ_DISTANCIAS = gerar_matriz_distancias(novos_pontos)
        fitness_module.PONTOS = novos_pontos
        fitness_module.MATRIZ_DISTANCIAS = data_module.MATRIZ_DISTANCIAS

        melhor_rota, custo, historico_fitness = executar_ag(
            tam_populacao=pop,
            geracoes=ger,
        )
    finally:
        data_module.PONTOS = old_pontos
        data_module.MATRIZ_DISTANCIAS = old_matriz
        fitness_module.PONTOS = old_pontos
        fitness_module.MATRIZ_DISTANCIAS = old_matriz

    t_total = time.time() - t_inicio
    print(f"         ✅ Concluído em {t_total:.2f}s | Melhor fitness: {custo:.2f}\n")
    imprimir_rotas(melhor_rota, custo, novos_pontos)

    rotas_detalhadas = construir_rotas_detalhadas(melhor_rota, custo, novos_pontos, novos_itens)

    print("🗺️  [2/6] Gerando novo mapa de rotas...")
    caminho_png = plotar_rotas(melhor_rota)
    print(f"         ✅ Mapa atualizado salvo: {caminho_png}\n")

    print("💾 [3/6] Exportando novo JSON e Mapa Google Maps...")
    caminho_html = gerar_mapa_html(rotas_detalhadas, novos_pontos)
    caminho_json = exportar_json(melhor_rota, custo, rotas_detalhadas)
    print(f"         ✅ JSON atualizado salvo: {caminho_json}")
    print(f"         ✅ Mapa HTML atualizado salvo: {caminho_html}\n")

    print("📋 [4/6] Gerando novos manifestos de transporte por motorista...\n")
    for dados_v in rotas_detalhadas:
        manifesto = gerar_manifesto_local(dados_v)
        print(manifesto)
        print()

    print("📈 [5/6] Gerando novo relatório de eficiência...\n")
    relatorio = gerar_relatorio_eficiencia(rotas_detalhadas, historico_fitness, t_total)
    print(relatorio)
    print()

    print("💡 [6/6] Analisando melhorias do processo...\n")
    melhorias = sugerir_melhorias_processo(rotas_detalhadas, historico_fitness)
    print(melhorias)
    print()

    return {
        "rotas": rotas_detalhadas,
        "fitness_final": custo,
        "total_geracoes": len(historico_fitness),
    }


# ==============================================================================
# EXECUÇÃO PRINCIPAL
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="HealthRoute AI — Otimizador de Rotas Médicas")
    parser.add_argument("--no-gui",  action="store_true", help="Executa sem PyGame (headless/Docker)")
    parser.add_argument("--no-qa",   action="store_true", help="Pula a interface Q&A interativa")
    parser.add_argument("--pop",     type=int, default=40,  help="Tamanho da população (padrão: 40)")
    parser.add_argument("--ger",     type=int, default=80,  help="Número de gerações (padrão: 80)")
    args = parser.parse_args()

    imprimir_banner()

    # ─── ETAPA 1: Algoritmo Genético ─────────────────────────────────────── #
    print("🧬 [1/7] Executando Algoritmo Genético VRP...")
    print(f"         Configuração: {args.pop} indivíduos × {args.ger} gerações")
    t_inicio = time.time()
    melhor_rota, custo, historico_fitness = executar_ag(
        tam_populacao=args.pop,
        geracoes=args.ger,
    )
    t_total = time.time() - t_inicio
    print(f"         ✅ Concluído em {t_total:.2f}s | Melhor fitness: {custo:.2f}\n")
    imprimir_rotas(melhor_rota, custo)

    # ─── ETAPA 2: Constrói estrutura detalhada das rotas ────────────────── #
    rotas_detalhadas = construir_rotas_detalhadas(melhor_rota, custo)

    # ─── ETAPA 3: Visualização ──────────────────────────────────────────── #
    if args.no_gui:
        print("🗺️  [2/7] Gerando mapa (matplotlib — modo headless)...")
        caminho_png = plotar_rotas(melhor_rota)
        print(f"         ✅ Mapa salvo: {caminho_png}\n")
    else:
        print("🎮 [2/7] Abrindo visualização PyGame...")
        try:
            from vrp.pygame_viz import executar as pygame_executar
            pygame_executar(historico_fitness, melhor_rota)
            print("         ✅ Visualização encerrada.\n")
        except KeyboardInterrupt:
            print("         ✅ Visualização encerrada pelo usuário.\n")
        except Exception as e:
            print(f"         ⚠️  PyGame indisponível ({e}). Gerando PNG via matplotlib...")
            plotar_rotas(melhor_rota)
        plotar_rotas(melhor_rota)

    # ─── ETAPA 4: Exportação JSON e Mapa Google Maps ────────────────── #
    print("💾 [3/7] Exportando rotas para JSON e Google Maps...")
    caminho_html = gerar_mapa_html(rotas_detalhadas)
    caminho_json = exportar_json(melhor_rota, custo, rotas_detalhadas)
    print(f"         ✅ JSON salvo: {caminho_json}")
    print(f"         ✅ Mapa HTML interativo salvo: {caminho_html}\n")

    # ─── ETAPA 5: Manifestos de motoristas ──────────────────────────────── #
    print("📋 [4/7] Gerando manifestos de transporte...\n")
    for dados_v in rotas_detalhadas:
        manifesto = gerar_manifesto_local(dados_v)
        print(manifesto)
        print()

    # ─── ETAPA 6: Relatório de eficiência ───────────────────────────────── #
    print("📈 [5/7] Gerando relatório de eficiência...\n")
    relatorio = gerar_relatorio_eficiencia(rotas_detalhadas, historico_fitness, t_total)
    print(relatorio)
    print()

    # ─── ETAPA 7: Sugestões de melhoria ─────────────────────────────────── #
    print("💡 [6/7] Analisando oportunidades de melhoria...\n")
    melhorias = sugerir_melhorias_processo(rotas_detalhadas, historico_fitness)
    print(melhorias)
    print()

    # ─── ETAPA 8: Webhook n8n ───────────────────────────────────────────── #
    print("🔗 [7/7] Preparando payload para webhook n8n...")
    payload = gerar_payload_n8n(rotas_detalhadas, custo, historico_fitness)
    disparar_webhook(payload)
    print()

    # ─── ETAPA 9: Interface Q&A e Gestão de Lotes ───────────────────────── #
    if not args.no_qa:
        gl = GerenciadorLotes()
        estado_app = {
            "melhor_rota": melhor_rota,
            "historico_fitness": historico_fitness,
        }

        contexto_qa = {
            "rotas": rotas_detalhadas,
            "fitness_final": custo,
            "total_geracoes": len(historico_fitness),
            "gerenciador_lotes": gl,
        }

        def reotimizar_callback(novos_pts, novos_its):
            novo_ctx = executar_pipeline_lote(novos_pts, novos_its, pop=args.pop, ger=args.ger)
            return novo_ctx

        def abrir_pygame_callback():
            try:
                from vrp.pygame_viz import executar as pygame_executar
                pygame_executar(estado_app["historico_fitness"], estado_app["melhor_rota"])
            except Exception as e:
                print(f"⚠️ Erro ao abrir janela PyGame: {e}")

        iniciar_qa_interativo(
            contexto_qa,
            gerenciador_lotes=gl,
            callback_reotimizar=reotimizar_callback,
            callback_pygame=abrir_pygame_callback,
        )

    print("\n✅ HealthRoute AI concluído com sucesso!")
    print(f"   Outputs: output/rotas.png | output/rotas.json | output/rotas_google_maps.html | output/webhook_payload.json")


if __name__ == "__main__":
    main()
