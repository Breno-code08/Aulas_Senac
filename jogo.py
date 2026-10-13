import tkinter as tk


LARGURA = 800
ALTURA = 500
ALTURA_RAQUETE = 90
RAIO_BOLA = 10

janela = tk.Tk()
janela.title("Ping Pong")
janela.resizable(False, False)

tela = tk.Canvas(janela, width=LARGURA, height=ALTURA, bg="#010a08", highlightthickness=0)
tela.pack()

tela.create_line(LARGURA // 2, 0, LARGURA // 2, ALTURA, fill="white", dash=(8, 8))

raquete_jogador = tela.create_rectangle(30, 205, 45, 295, fill="white", outline="")
raquete_computador = tela.create_rectangle(755, 205, 770, 295, fill="white", outline="")
bola = tela.create_oval(390, 240, 410, 260, fill="white", outline="")

pontos_jogador = 0
pontos_computador = 0
placar = tela.create_text(
    LARGURA // 2,
    35,
    text="0     :     0",
    fill="white",
    font=("Arial", 28, "bold"),
)
tela.create_text(
    LARGURA // 2,
    ALTURA - 20,
    text="Use W e S para mover a raquete",
    fill="white",
    font=("Arial", 12),
)

bola_x = LARGURA / 2
bola_y = ALTURA / 2
velocidade_x = 10
velocidade_y = 12
teclas_pressionadas = set()


def pressionar_tecla(evento):
    teclas_pressionadas.add(evento.keysym.lower())


def soltar_tecla(evento):
    teclas_pressionadas.discard(evento.keysym.lower())


def atualizar_placar():
    tela.itemconfig(placar, text=f"{pontos_jogador}     :     {pontos_computador}")


def reiniciar_bola(direcao):
    global bola_x, bola_y, velocidade_x, velocidade_y
    bola_x = LARGURA / 2
    bola_y = ALTURA / 2
    velocidade_x = 5 * direcao
    velocidade_y = 3
    tela.coords(
        bola,
        bola_x - RAIO_BOLA,
        bola_y - RAIO_BOLA,
        bola_x + RAIO_BOLA,
        bola_y + RAIO_BOLA,
    )


def mover_raquete(raquete, movimento):
    coordenadas = tela.coords(raquete)
    nova_posicao = max(
        0,
        min(ALTURA - ALTURA_RAQUETE, coordenadas[1] + movimento),
    )
    tela.coords(raquete, coordenadas[0], nova_posicao, coordenadas[2], nova_posicao + ALTURA_RAQUETE)


def atualizar_jogo():
    global bola_x, bola_y, velocidade_x, velocidade_y
    global pontos_jogador, pontos_computador

    if "w" in teclas_pressionadas:
        mover_raquete(raquete_jogador, -7)
    if "s" in teclas_pressionadas:
        mover_raquete(raquete_jogador, 7)

    # O computador acompanha a bola com velocidade limitada.
    computador = tela.coords(raquete_computador)
    centro_computador = (computador[1] + computador[3]) / 2
    if centro_computador < bola_y - 8:
        mover_raquete(raquete_computador, 4)
    elif centro_computador > bola_y + 8:
        mover_raquete(raquete_computador, -4)

    bola_x += velocidade_x
    bola_y += velocidade_y

    if bola_y - RAIO_BOLA <= 0 or bola_y + RAIO_BOLA >= ALTURA:
        velocidade_y *= -1

    esquerda = tela.coords(raquete_jogador)
    direita = tela.coords(raquete_computador)
    if (
        velocidade_x < 0
        and bola_x - RAIO_BOLA <= esquerda[2]
        and esquerda[1] <= bola_y <= esquerda[3]
    ):
        velocidade_x *= -1
    elif (
        velocidade_x > 0
        and bola_x + RAIO_BOLA >= direita[0]
        and direita[1] <= bola_y <= direita[3]
    ):
        velocidade_x *= -1

    if bola_x < 0:
        pontos_computador += 1
        atualizar_placar()
        reiniciar_bola(-1)
    elif bola_x > LARGURA:
        pontos_jogador += 1
        atualizar_placar()
        reiniciar_bola(1)
    else:
        tela.coords(
            bola,
            bola_x - RAIO_BOLA,
            bola_y - RAIO_BOLA,
            bola_x + RAIO_BOLA,
            bola_y + RAIO_BOLA,
        )

    janela.after(16, atualizar_jogo)


janela.bind("<KeyPress>", pressionar_tecla)
janela.bind("<KeyRelease>", soltar_tecla)
tela.focus_set()
atualizar_jogo()
janela.mainloop()