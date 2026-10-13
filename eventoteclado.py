import tkinter as tk

def mudar_texto(event):
    label.config(text="Mudou o texto!")

janela = tk.Tk()
janela.title("Evento Enter")
janela.geometry("300x180")
janela.configure(bg='#0f172A')

label = tk.Label(
    janela,
    text="Precione Enter para mudar",
    bg="#000103",
    fg="#e9ebf0",
    font=('Arial', 14, 'bold')
)
label.pack(pady=30)

janela.bind('<Return>', mudar_texto)

janela.mainloop()
