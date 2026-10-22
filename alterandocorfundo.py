import tkinter as tk

janela = tk.Tk()
janela.title("Fundo Personalizado")
janela.geometry("300x180")

ative = 0  # variável global que controla o estado do fundo


def alterar_fundo():
    global ative  # diz ao Python que estamos alterando a variável global

    if ative == 0:
        janela.configure(bg='#06010A')
        ative = 1
    else:
        janela.configure(bg="#EAE6EC")
        ative = 0



janela.configure(bg='#0f172A')
tk.Button(janela, text="Preto", command=alterar_fundo).pack(pady=10)

label = tk.Label(
    janela,
    text="Mudar cor!",
    bg="#000103",
    fg="#e9ebf0",
    font=('Arial', 14, 'bold')
)
label.pack(pady=30)

janela.mainloop()