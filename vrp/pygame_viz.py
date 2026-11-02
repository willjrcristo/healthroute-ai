"""
vrp/pygame_viz.py — Visualização animada PyGame: mapa 2D + gráfico de fitness em tempo real.

Janela 1280x720 dividida em dois painéis:
  - Esquerdo (720x720): Mapa 2D dos pontos hospitalares e rotas por veículo
  - Direito  (560x720): Gráfico de fitness convergindo geração a geração
"""
from __future__ import annotations

import sys
import time
from typing import List, Tuple

import numpy as np

from .data import PONTOS, NUM_VEICULOS, CAPACIDADE_VEICULO, MATRIZ_DISTANCIAS

# Cores PyGame (RGB)
COR_FUNDO        = (245, 245, 245)
COR_PAINEL_DIR   = (30, 30, 50)
COR_GRADE        = (200, 200, 200)
COR_DEPOSITO     = (255, 193, 7)
COR_CRITICO      = (244, 67, 54)
COR_REGULAR      = (33, 150, 243)
COR_TEXTO        = (30, 30, 30)
COR_TEXTO_CLARO  = (220, 220, 220)
COR_FITNESS      = (76, 175, 80)

CORES_VEICULOS   = [
    (33, 150, 243),   # Azul  — V-101
    (255, 152, 0),    # Laranja — V-102
    (76, 175, 80),    # Verde — V-103
]
NOMES_VEICULOS   = ["V-101", "V-102", "V-103"]

LARGURA_JANELA   = 1280
ALTURA_JANELA    = 720
LARGURA_MAPA     = 720
MARGEM_MAPA      = 40


def _construir_rotas(melhor_rota: List[int]) -> List[List[int]]:
    entregas = [p for p in melhor_rota if p != 0]
    partes = np.array_split(entregas, NUM_VEICULOS)
    return [[0] + list(p) + [0] for p in partes]


def _ponto_para_pixel(pos, margem: int, tamanho: int) -> tuple[int, int]:
    """Converte coordenadas do grid (0-10) para pixels no painel do mapa."""
    x, y = pos
    escala = (tamanho - 2 * margem) / 10.0
    px = int(margem + x * escala)
    py = int(tamanho - margem - y * escala)  # inverte eixo Y
    return px, py


def executar(historico_fitness: List[float], melhor_rota: List[int]) -> None:
    """
    Abre a janela PyGame e exibe:
    - Animação da construção das rotas no mapa esquerdo
    - Gráfico de fitness sendo desenhado no painel direito
    """
    try:
        import pygame
    except ImportError:
        print("[pygame_viz] PyGame não instalado. Execute: pip install pygame")
        return

    pygame.init()
    pygame.display.set_caption("HealthRoute AI — Visualização do Algoritmo Genético")
    tela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
    clock = pygame.time.Clock()

    # Limpa eventos residuais anteriores
    pygame.event.clear()

    try:
        fonte_titulo = pygame.font.SysFont("segoeui", 18, bold=True)
        fonte_normal = pygame.font.SysFont("segoeui", 13)
        fonte_pequena = pygame.font.SysFont("segoeui", 11)
        fonte_btn = pygame.font.SysFont("segoeui", 13, bold=True)
    except Exception:
        fonte_titulo = pygame.font.Font(None, 22)
        fonte_normal = pygame.font.Font(None, 16)
        fonte_pequena = pygame.font.Font(None, 14)
        fonte_btn = pygame.font.Font(None, 16)

    rotas = _construir_rotas(melhor_rota)
    max_fitness = max(historico_fitness) if historico_fitness else 1
    min_fitness = min(historico_fitness) if historico_fitness else 0
    total_geracoes = len(historico_fitness)

    # Dimensões do painel direito (gráfico)
    pX = LARGURA_MAPA + 40
    pW = LARGURA_JANELA - LARGURA_MAPA - 80
    pY = 70
    pH = ALTURA_JANELA - 170

    geracao_atual = 1
    rodando = True

    # Botão Avançar / Fechar
    btn_rect = pygame.Rect(pX, ALTURA_JANELA - 45, pW, 32)

    try:
        while rodando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    rodando = False
                elif evento.type == pygame.KEYDOWN:
                    if evento.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE, pygame.K_q):
                        rodando = False
                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    # Se clicou no botão "Continuar" ou se a animação já terminou
                    if btn_rect.collidepoint(evento.pos) or geracao_atual >= total_geracoes:
                        rodando = False
                    else:
                        # Se clicou durante a animação, avança direto para o fim da animação
                        geracao_atual = total_geracoes

            tela.fill(COR_FUNDO)

            # ------------------------------------------------------------------ #
            # PAINEL ESQUERDO — Mapa 2D                                           #
            # ------------------------------------------------------------------ #
            # Grade de fundo
            num_linhas = 11
            escala = (LARGURA_MAPA - 2 * MARGEM_MAPA) / 10.0
            for k in range(num_linhas):
                x_lin = int(MARGEM_MAPA + k * escala)
                y_lin = int(MARGEM_MAPA + k * escala)
                pygame.draw.line(tela, COR_GRADE, (x_lin, MARGEM_MAPA), (x_lin, LARGURA_MAPA - MARGEM_MAPA), 1)
                pygame.draw.line(tela, COR_GRADE, (MARGEM_MAPA, y_lin), (LARGURA_MAPA - MARGEM_MAPA, y_lin), 1)

            # Rotas por veículo
            for rota, cor in zip(rotas, CORES_VEICULOS):
                pontos_px = [_ponto_para_pixel(PONTOS[p]["pos"], MARGEM_MAPA, LARGURA_MAPA) for p in rota]
                if len(pontos_px) >= 2:
                    pygame.draw.lines(tela, cor, False, pontos_px, 3)
                    for i in range(len(pontos_px) - 1):
                        pygame.draw.circle(tela, cor, pontos_px[i + 1], 4)

            # Nós hospitalares
            for pid, dados in PONTOS.items():
                px, py = _ponto_para_pixel(dados["pos"], MARGEM_MAPA, LARGURA_MAPA)
                if pid == 0:
                    pygame.draw.circle(tela, COR_DEPOSITO, (px, py), 13)
                    pygame.draw.circle(tela, (0, 0, 0), (px, py), 13, 2)
                    label = fonte_normal.render("Depósito", True, (60, 40, 0))
                    tela.blit(label, (px + 16, py - 8))
                elif dados["critico"]:
                    pygame.draw.circle(tela, COR_CRITICO, (px, py), 11)
                    pygame.draw.circle(tela, (140, 0, 0), (px, py), 11, 2)
                    label = fonte_pequena.render(f"{dados['nome']} [CRITICO]", True, COR_CRITICO)
                    tela.blit(label, (px + 14, py - 9))
                    carga_lbl = fonte_pequena.render(f"Demanda: {dados['demanda']}kg", True, (130, 0, 0))
                    tela.blit(carga_lbl, (px + 14, py + 5))
                else:
                    pygame.draw.circle(tela, COR_REGULAR, (px, py), 9)
                    pygame.draw.circle(tela, (0, 60, 140), (px, py), 9, 2)
                    label = fonte_pequena.render(dados["nome"], True, (20, 80, 160))
                    tela.blit(label, (px + 12, py - 9))
                    carga_lbl = fonte_pequena.render(f"Demanda: {dados['demanda']}kg", True, (30, 90, 160))
                    tela.blit(carga_lbl, (px + 12, py + 5))

            # Título do mapa
            t = fonte_titulo.render("Mapa de Rotas Hospitalares — Grid 10×10 km", True, COR_TEXTO)
            tela.blit(t, (15, 12))

            # Legenda de veículos (canto superior direito)
            fundo_legenda = pygame.Surface((175, 75))
            fundo_legenda.set_alpha(225)
            fundo_legenda.fill((255, 255, 255))
            tela.blit(fundo_legenda, (LARGURA_MAPA - 195, 15))
            pygame.draw.rect(tela, (200, 200, 200), (LARGURA_MAPA - 195, 15, 175, 75), 1)

            for i, (cor, nome) in enumerate(zip(CORES_VEICULOS, NOMES_VEICULOS)):
                pygame.draw.rect(tela, cor, (LARGURA_MAPA - 185, 24 + i * 22, 16, 12))
                lbl = fonte_pequena.render(nome, True, COR_TEXTO)
                tela.blit(lbl, (LARGURA_MAPA - 162, 22 + i * 22))

            # ------------------------------------------------------------------ #
            # PAINEL DIREITO — Gráfico de Fitness                                 #
            # ------------------------------------------------------------------ #
            pygame.draw.rect(tela, COR_PAINEL_DIR, (LARGURA_MAPA, 0, LARGURA_JANELA - LARGURA_MAPA, ALTURA_JANELA))
            titulo_g = fonte_titulo.render("Convergência do Fitness", True, COR_TEXTO_CLARO)
            tela.blit(titulo_g, (pX, 15))

            # Eixos
            pygame.draw.line(tela, COR_TEXTO_CLARO, (pX, pY), (pX, pY + pH), 2)
            pygame.draw.line(tela, COR_TEXTO_CLARO, (pX, pY + pH), (pX + pW, pY + pH), 2)

            # Labels eixos
            lbl_y = fonte_pequena.render(f"{max_fitness:.0f}", True, COR_TEXTO_CLARO)
            tela.blit(lbl_y, (pX - 5 - lbl_y.get_width(), pY))
            lbl_y2 = fonte_pequena.render(f"{min_fitness:.0f}", True, COR_TEXTO_CLARO)
            tela.blit(lbl_y2, (pX - 5 - lbl_y2.get_width(), pY + pH - 10))
            lbl_x1 = fonte_pequena.render("0", True, COR_TEXTO_CLARO)
            tela.blit(lbl_x1, (pX, pY + pH + 5))
            lbl_xN = fonte_pequena.render(str(total_geracoes), True, COR_TEXTO_CLARO)
            tela.blit(lbl_xN, (pX + pW - lbl_xN.get_width(), pY + pH + 5))

            # Linha de fitness
            if geracao_atual > 1:
                fat = max_fitness - min_fitness if max_fitness != min_fitness else 1
                pontos_graf = []
                for i in range(min(geracao_atual, total_geracoes)):
                    gx = pX + int(i / max(total_geracoes - 1, 1) * pW)
                    gy = pY + pH - int((historico_fitness[i] - min_fitness) / fat * pH)
                    pontos_graf.append((gx, gy))
                if len(pontos_graf) >= 2:
                    pygame.draw.lines(tela, COR_FITNESS, False, pontos_graf, 2)
                pygame.draw.circle(tela, COR_FITNESS, pontos_graf[-1], 5)

            # Info geracao
            info = fonte_normal.render(
                f"Geração: {min(geracao_atual, total_geracoes)} / {total_geracoes}",
                True, COR_TEXTO_CLARO
            )
            tela.blit(info, (pX, pY + pH + 20))

            if geracao_atual < total_geracoes:
                fitness_info = fonte_normal.render(
                    f"Fitness Atual: {historico_fitness[min(geracao_atual, total_geracoes) - 1]:.2f}",
                    True, COR_FITNESS
                )
            else:
                fitness_info = fonte_titulo.render(
                    f"Melhor Fitness Final: {historico_fitness[-1]:.2f}",
                    True, COR_FITNESS
                )
            tela.blit(fitness_info, (pX, pY + pH + 45))

            # Botão "Continuar / Fechar"
            mouse_pos = pygame.mouse.get_pos()
            cor_btn = (60, 130, 240) if btn_rect.collidepoint(mouse_pos) else (45, 90, 180)
            pygame.draw.rect(tela, cor_btn, btn_rect, border_radius=6)
            txt_btn = fonte_btn.render("Prosseguir para o Terminal [ESC / Clique Aqui]", True, (255, 255, 255))
            txt_x = btn_rect.x + (btn_rect.width - txt_btn.get_width()) // 2
            txt_y = btn_rect.y + (btn_rect.height - txt_btn.get_height()) // 2
            tela.blit(txt_btn, (txt_x, txt_y))

            pygame.display.flip()
            clock.tick(30)

            # Avança a animação suavemente
            if geracao_atual < total_geracoes:
                geracao_atual = min(total_geracoes, geracao_atual + max(1, total_geracoes // 80))

    except KeyboardInterrupt:
        pass
    finally:
        try:
            pygame.display.quit()
            pygame.quit()
        except Exception:
            pass
