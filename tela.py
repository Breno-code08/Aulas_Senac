# Codigo Padrão com Tkinter
import tkinter as tk

# 1. Criar a janela principal
janela = tk.Tk()
janela.title("Minha Aplicação")
n1 = int(input("Digite um numero: "))
n2 = int(input("Digite outro numero: "))
janela.geometry(f"{n1}x{n2}")

# 2. Adicionando um rótulo (texto
label = tk.Label(janela, text="Olá Mundo")
label.pack(pady=100)

# 3. Função para botão
def clicar_botao():
    soma = 10 + 10
    label.config(text=f"Você clicou no botão! {soma}")

# 4. Adicionando um botão
botao = tk.Button(janela, text="Clique Aqui", command=clicar_botao)
botao.pack()

# 5. Execução de janela
janela.mainloop()