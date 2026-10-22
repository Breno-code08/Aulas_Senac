from pathlib import Path
import tkinter as tk

def mostrar_conteudo():
    caminho = Path(__file__).with_name("zzzz.txt")
    try:
        print(caminho.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print("Arquivo zzzz.txt não encontrado")

janela = tk.Tk()
janela.title("Janela")
janela.geometry("400x300")

label = tk.Label (janela, text = "Olá, Mundo!", bg = "#000103", fg = "#DEE2E9")
label.pack (pady = 30)

tk.Button (janela, text= "Clique aqui", command=mostrar_conteudo).pack(pady=50)

janela.mainloop()