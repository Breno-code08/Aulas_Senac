# Requer a biblioteca Pillow (PIL) para manipular imagens e usar a classe Image.
import tkinter as tk  # Importa a biblioteca Tkinter para criar a janela e os widgets da interface.
from PIL import ImageTk, Image, ImageDraw  # Importa as classes de imagem do Pillow, incluindo conversão para Tk e desenho.

# Configuração da Janela: cria a janela principal da aplicação Tkinter.
app = tk.Tk()  # Cria a instância da janela principal.
app.title("Exibindo Imagem")  # Define o título que aparece na barra da janela.
app.geometry("350x300")  # Define o tamanho inicial da janela em pixels: largura 350 e altura 300.

# 1. Carrega e redimensiona a imagem: abre a imagem JPG do arquivo e a prepara para uso.
img_pil = Image.open("images.jpg")  # Abre a imagem localizada no arquivo "images.jpg".
img_pil = img_pil.resize((200, 200)).convert("RGBA")  # Redimensiona a imagem para 200x200 pixels e converte para o formato RGBA.
mascara = Image.new("L", img_pil.size, 0)  # Cria uma máscara em escala de cinza com o mesmo tamanho da imagem e preenchida com 0.
ImageDraw.Draw(mascara).ellipse((0, 0, img_pil.width - 1, img_pil.height - 1), fill=255)  # Desenha um círculo branco na máscara para cortar os cantos da imagem em forma circular.
img_pil.putalpha(mascara)  # Aplica a máscara como canal alfa, deixando a imagem com forma redonda.

# 2. Converte para formato do Tkinter: transforma a imagem PIL em um objeto compatível com o canvas do Tk.
imagem_tk = ImageTk.PhotoImage(img_pil)  # Cria a imagem no formato que o Tkinter consegue exibir.

# 3. Exibe a imagem em um Canvas: cria um espaço para desenhar a imagem na janela.
canvas = tk.Canvas(app, highlightthickness=0)  # Cria um canvas na janela principal, sem borda destacada.
canvas.pack(fill=tk.BOTH, expand=True)  # Faz o canvas preencher toda a área disponível na janela e expandir com o tamanho da janela.
imagem_id = canvas.create_image(175, 150, image=imagem_tk)  # Cria a imagem no centro do canvas usando a imagem convertida.
cores = ["red", "blue", "green", "yellow", "magenta"]  # Lista de cores usadas para mudar a coloração da imagem ao tocar nas bordas.
indice_cor = 0  # Controla qual cor da lista está sendo usada no momento.
cor_imagem = None  # Inicialmente, a imagem não tem cor de sobreposição.


def mover_imagem(x=200, y=150, dx=12, dy=12, angulo=0):  # Define a função que move a imagem pela tela e a anima.
    global indice_cor, cor_imagem, imagem_tk  # Indica que as variáveis globais serão alteradas dentro da função.

    largura = canvas.winfo_width()  # Obtém a largura atual do canvas em pixels.
    altura = canvas.winfo_height()  # Obtém a altura atual do canvas em pixels.
    metade_largura = img_pil.width / 2  # Calcula a metade da largura da imagem para definir a borda de colisão horizontal.
    metade_altura = img_pil.height / 2  # Calcula a metade da altura da imagem para definir a borda de colisão vertical.

    proximo_x = x + dx  # Calcula a próxima posição X da imagem com base na velocidade horizontal.
    proximo_y = y + dy  # Calcula a próxima posição Y da imagem com base na velocidade vertical.
    bateu_na_borda = False  # Marca se a imagem encostou em alguma borda do canvas.

    if proximo_x < metade_largura or proximo_x > largura - metade_largura:  # Verifica se a imagem saiu pela borda esquerda ou direita.
        dx = -dx  # Inverte a velocidade horizontal para fazer a imagem ricochetear.
        proximo_x = x + dx  # Atualiza a posição X após a inversão da velocidade.
        bateu_na_borda = True  # Marca que houve colisão com a borda.
    if proximo_y < metade_altura or proximo_y > altura - metade_altura:  # Verifica se a imagem saiu pela borda superior ou inferior.
        dy = -dy  # Inverte a velocidade vertical para fazer a imagem ricochetear.
        proximo_y = y + dy  # Atualiza a posição Y após a inversão da velocidade.
        bateu_na_borda = True  # Marca que houve colisão com a borda.

    if bateu_na_borda:  # Se a imagem bateu em alguma borda, troca a cor da sobreposição.
        indice_cor = (indice_cor + 1) % len(cores)  # Avança para a próxima cor na lista e volta ao início quando atingir o fim.
        cor_imagem = cores[indice_cor]  # Armazena a cor atual para ser usada na sobreposição.

    imagem_girada = img_pil  # Começa com a imagem original, sem alteração.
    if cor_imagem is not None:  # Se houver uma cor de sobreposição definida, aplica a coloração na imagem.
        camada_cor = Image.new("RGB", img_pil.size, cor_imagem)  # Cria uma camada da mesma dimensão com a cor atual.
        imagem_colorida = Image.blend(img_pil.convert("RGB"), camada_cor, 0.4)  # Mistura a imagem original com a camada colorida em 40% de intensidade.
        imagem_girada = imagem_colorida.convert("RGBA")  # Converte a imagem colorida para o formato RGBA para manter o canal alpha.
        imagem_girada.putalpha(img_pil.getchannel("A"))  # Reaplica o canal alpha da imagem original para manter o formato redondo.

    angulo = (angulo + 5) % 360  # Incrementa o ângulo de rotação em 5 graus e mantém o valor dentro de 0 a 359.
    imagem_tk = ImageTk.PhotoImage(imagem_girada.rotate(angulo, resample=Image.Resampling.BICUBIC))  # Gira a imagem com rotação suave e converte para o formato Tkinter.
    canvas.itemconfigure(imagem_id, image=imagem_tk)  # Atualiza a imagem exibida no canvas com a nova imagem girada.
    canvas.coords(imagem_id, proximo_x, proximo_y)  # Move a imagem para a nova posição X e Y no canvas.
    canvas.after(20, mover_imagem, proximo_x, proximo_y, dx, dy, angulo)  # Agenda a próxima chamada da função após 20 milissegundos para animar.


app.after(20, mover_imagem)  # Chama a função mover_imagem pela primeira vez após 20 ms para iniciar a animação.

app.mainloop()  # Inicia o loop principal da aplicação e mantém a janela aberta até o usuário fechá-la.